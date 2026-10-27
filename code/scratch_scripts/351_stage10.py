"""Stage 10 - per-token author-name readout across layers, all 9,108 labelled papers.

For every paper and every listed author, the context is
    encode(PROMPT) + encode(" " + author)            (each author alone after "Authors:", as Stage 6)
and every name token j is scored at the position just before it (teacher forcing).
For each readout x layer we store rank / logprob / top-1 / ties of the gold token.

Readouts:  jlens_<lens>  (J_l transport + unembed),  logit  (unembed only),  final (L63 model output).
Storage:   raw/<readout>/L<layer>/shard_<k>.npz, rows aligned to cohort/name_tokens.parquet.
           One file per (readout, layer, shard): adding layers or lenses later only adds files.

Commands
  freeze        CPU   freeze cohort, token table, contexts, shards, protocol, lens registry
  audit         CPU   verify frozen hashes + show completion matrix
  freeze-conditions CPU  matched false titles (K=5, tiered) + delete-title prompts
  remaining     CPU   number of missing output files for --condition/--shards
  register-lens CPU   add a lens to the registry (e.g. Fit B later)
  parity        GPU   fast path vs per-prefix lens.apply on sample contexts (gate for run)
  run           GPU   compute missing (readout, layer, shard) files
  crosscheck    CPU   compare ranks with Stage 6 raw rows on the Pilot50 overlap
  analyze-title CPU   true vs false vs delete contrasts (needs all 7 conditions)
  analyze       CPU   paper-level scores, grouping analyses A-E, figures, report (see config/analysis_plan.json)
"""
import argparse, datetime, hashlib, json, math, os, re, sys, time, warnings
from pathlib import Path

MODEL = 'Qwen/Qwen3-32B'
REV = '9216db5781bf21249d130ec9da846c4624c16137'
PROMPT = 'Who are the authors of the paper titled "{title}" ({year})?\nAuthors:'
FINAL_LAYER = 63
MAX_NAME_TOKENS = 32
MAX_CONTEXT = 512
PAPERS_PER_SHARD = 128
BASE = Path('/scratch') / os.environ.get('USER', '') / 'jlens'
ROOT = BASE / '351_stage10'
LABELS = BASE / 'labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/paper_labels_with_papers.csv'
DEFAULT_LENSES = {
    'public': BASE / 'public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt',
    'self100': BASE / 'qwen32b_jlens_prelim_100.pt',
    'fitA': BASE / '351_stage9/runner_runs/full_A_repair_101_100valid/lens.pt',
}
DEFAULT_LAYERS = [24, 32, 40, 48, 56, 62]
PARTICLES = {'de', 'da', 'di', 'do', 'dos', 'das', 'del', 'della', 'der', 'den', 'van', 'von', 'le', 'la', 'du', 'ten', 'ter', 'bin', 'al', 'el', 'y'}
INITIAL = re.compile(r'^[^\W\d_]\.?$')
PUNCT = re.compile(r'^[\s\W_]+$')


# ---------------------------------------------------------------- helpers
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 24), b''): h.update(chunk)
    return h.hexdigest()
def sha_obj(o): return sha_bytes(json.dumps(o, sort_keys=True, ensure_ascii=False).encode())
def now(): return datetime.datetime.now().isoformat(timespec='seconds')
def dump(p, obj):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + f'.tmp.{os.getpid()}')
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + '\n'); os.replace(tmp, p)
def load(p): return json.loads(Path(p).read_text())
def parse_layers(s): return sorted({int(x) for x in s.split(',') if x.strip()}) if s else None
def parse_shards(s, n):
    if not s: return list(range(n))
    out = set()
    for part in s.split(','):
        a, _, b = part.partition('-'); out.update(range(int(a), int(b or a) + 1))
    bad = [k for k in out if not 0 <= k < n]
    if bad: raise ValueError(f'shards out of range: {bad}')
    return sorted(out)
def raw_dir(root, cond='true'): return root / 'raw' if cond == 'true' else root / 'raw' / f'cond_{cond}'
def out_file(root, readout, layer, shard, cond='true'): return raw_dir(root, cond) / readout / f'L{layer:02d}' / f'shard_{shard:03d}.npz'


def tokenizer():
    import transformers
    return transformers.AutoTokenizer.from_pretrained(MODEL, revision=REV)


def token_roles(name, offsets, texts):
    """Role of each name token, from character offsets into ' ' + name."""
    s = ' ' + name
    words = [(m.start(), m.end(), m.group()) for m in re.finditer(r'\S+', s)]
    def word_role(i, w):
        if i == len(words) - 1: return 'surname'
        if w.lower() in PARTICLES: return 'particle'
        if INITIAL.match(w): return 'initial'
        return 'given'
    roles, widx, seen = [], [], set()
    for (a, b), txt in zip(offsets, texts):
        c = a
        while c < b and s[c].isspace(): c += 1
        wi = next((i for i, (ws, we, _) in enumerate(words) if ws <= c < we), len(words) - 1)
        wr = word_role(wi, words[wi][2])
        if PUNCT.match(txt): r = 'punct'
        else:
            r = f'{wr}_first' if wi not in seen else f'{wr}_cont'
            seen.add(wi)
        roles.append(r); widx.append(wi)
    return roles, widx, len(words)


# ---------------------------------------------------------------- freeze / audit
def freeze(a):
    import pandas as pd
    root = Path(a.root)
    labels = Path(a.labels)
    if (root / 'config/manifest.json').exists():
        verify(root); print('ALREADY FROZEN; verified', root); return
    if root.exists() and any(root.iterdir()): raise FileExistsError(f'non-frozen, non-empty {root}')
    tok = tokenizer()
    df = pd.read_csv(labels, dtype=str, keep_default_na=False).sort_values('paper_id').reset_index(drop=True)
    if df.paper_id.duplicated().any(): raise ValueError('duplicate paper_id in labels')
    papers, contexts, rows, excluded = [], [], [], []
    for pi, p in df.iterrows():
        prompt = PROMPT.format(title=p['title'], year=p['year'])
        pids = tok(prompt).input_ids
        authors = [x.strip() for x in p['authors'].split(';') if x.strip()]
        shard = pi // PAPERS_PER_SHARD
        n_ok = 0
        for ai, au in enumerate(authors):
            enc = tok(' ' + au, add_special_tokens=False, return_offsets_mapping=True)
            ids = enc.input_ids
            why = None
            if not ids: why = 'no_tokens'
            elif len(ids) > MAX_NAME_TOKENS: why = f'name_tokens>{MAX_NAME_TOKENS}'
            elif len(pids) + len(ids) - 1 > MAX_CONTEXT: why = f'context>{MAX_CONTEXT}'
            if why:
                excluded.append(dict(paper_id=p['paper_id'], author_index=ai, author=au, reason=why)); continue
            texts = [tok.decode([i]) for i in ids]
            roles, widx, nw = token_roles(au, enc.offset_mapping, texts)
            cid = len(contexts)
            contexts.append(dict(context_id=cid, paper_id=p['paper_id'], shard=shard, author_index=ai, author=au,
                                 n_prompt_tokens=len(pids), n_name_tokens=len(ids), row_start=len(rows),
                                 duplicate_in_paper=authors.count(au) > 1))
            for j, (tid, txt, r, w, off) in enumerate(zip(ids, texts, roles, widx, enc.offset_mapping)):
                rows.append(dict(row_id=len(rows), context_id=cid, paper_id=p['paper_id'], shard=shard, author_index=ai,
                                 token_index=j, token_id=tid, token_text=txt, role=r, word_index=w, n_words=nw,
                                 char_start=off[0], char_end=off[1]))
            n_ok += 1
        # every label column is kept, so grouping can be (re)defined at analysis time without touching raw outputs
        papers.append(dict(p.to_dict(), shard=shard, n_authors_listed=len(authors), n_authors_scored=n_ok,
                           prompt_ids=json.dumps(pids)))
    n_shards = papers[-1]['shard'] + 1
    (root / 'cohort').mkdir(parents=True); (root / 'config').mkdir(); (root / 'reports').mkdir()
    out = {'cohort/papers.parquet': pd.DataFrame(papers), 'cohort/contexts.parquet': pd.DataFrame(contexts),
           'cohort/name_tokens.parquet': pd.DataFrame(rows), 'cohort/excluded_authors.csv': pd.DataFrame(excluded, columns=['paper_id', 'author_index', 'author', 'reason'])}
    for rel, d in out.items():
        (d.to_csv if rel.endswith('.csv') else d.to_parquet)(root / rel, index=False)
    protocol = dict(
        version='stage10_v1', model=MODEL, revision=REV, prompt=PROMPT,
        cohort=f'all papers of {labels.name} (sorted by paper_id); groups from group_tight (also group)',
        context='encode(PROMPT) [tokenizer default, no BOS for Qwen3] + encode(" " + author, add_special_tokens=False); each author alone',
        input_ids='prompt_ids + name_ids[:-1] (causal: position len(prompt)-1+j predicts name token j)',
        authors='labels column authors split on ";" and stripped, spelling kept exactly as given',
        rank='1 + number of vocab logits strictly greater than the gold logit (logits as returned by jlens unembed, bf16 lm_head -> float)',
        ties='number of other vocab logits exactly equal to the gold logit (stored; rank is tie-favourable)',
        logprob='log_softmax over the readout logits',
        readouts={'jlens_<lens>': 'lens.transport(residual_l) then model.unembed (final norm + lm_head), = JacobianLens.apply(use_jacobian=True)',
                  'logit': 'model.unembed(residual_l), = JacobianLens.apply(use_jacobian=False)',
                  'final': 'model.unembed(residual_63) = actual model next-token logits'},
        residual='output of decoder block l (jlens ActivationRecorder convention)',
        token_roles='initial_first | punct | given_first/_cont | particle_first/_cont | surname_first/_cont (surname = last word)',
        exclusions=f'name tokens > {MAX_NAME_TOKENS} or context > {MAX_CONTEXT} tokens (see cohort/excluded_authors.csv)',
        primary_metric='per paper, readout, layer: sum over all scored authors and all their name tokens of 1/rank',
        secondary_metrics='mean 1/rank per token; mean over authors of per-author mean 1/rank; role-specific sums/means; mean log10 rank; top-1 share',
        shards=f'{PAPERS_PER_SHARD} consecutive papers per shard, {n_shards} shards',
        extension='new layers / lenses only add raw/<readout>/L<layer>/shard_<k>.npz files; frozen cohort never changes')
    dump(root / 'config/protocol.json', protocol)
    lenses = {}
    for name, path in DEFAULT_LENSES.items(): lenses[name] = lens_entry(path)
    dump(root / 'config/lenses.json', lenses)
    manifest = dict(created=now(), script_sha256=sha_file(__file__), inputs={'labels': str(labels), 'labels_sha256': sha_file(labels)},
                    protocol_sha256=sha_obj(protocol), n_shards=n_shards, n_papers=len(papers), n_contexts=len(contexts),
                    n_tokens=len(rows), n_excluded_authors=len(excluded),
                    outputs={rel: sha_file(root / rel) for rel in out})
    dump(root / 'config/manifest.json', manifest)
    print('FROZEN', root, json.dumps({k: manifest[k] for k in ('n_papers', 'n_contexts', 'n_tokens', 'n_excluded_authors', 'n_shards')}))


def lens_entry(path):
    import torch
    path = Path(path)
    d = torch.load(path, map_location='cpu', mmap=True, weights_only=False)
    return dict(path=str(path), sha256=sha_file(path), source_layers=[int(x) for x in d['source_layers']],
                n_prompts=int(d['n_prompts']) if 'n_prompts' in d else None, registered=now())


def verify(root):
    m = load(root / 'config/manifest.json')
    for rel, h in m['outputs'].items():
        if sha_file(root / rel) != h: raise ValueError(f'FROZEN FILE CHANGED {rel}')
    if sha_file(m['inputs']['labels']) != m['inputs']['labels_sha256']: raise ValueError('LABEL FILE CHANGED')
    if sha_obj(load(root / 'config/protocol.json')) != m['protocol_sha256']: raise ValueError('PROTOCOL CHANGED')
    lenses = load(root / 'config/lenses.json')
    return m, lenses


def completion(root, m, cond='true'):
    done = {}
    raw = raw_dir(root, cond)
    if raw.exists():
        for f in raw.glob('*/L*/shard_*.npz'):  # cond_* dirs hold readout dirs, never L*, so 'true' never picks them up
            done.setdefault((f.parts[-3], int(f.parts[-2][1:])), set()).add(int(f.stem.split('_')[1]))
    return done


def audit(a):
    root = Path(a.root); m, lenses = verify(root)
    print('STAGE 10 FROZEN OK', m['n_papers'], 'papers', m['n_contexts'], 'contexts', m['n_tokens'], 'tokens', m['n_shards'], 'shards')
    for k, v in lenses.items():
        ok = Path(v['path']).exists() and (a.quick or sha_file(v['path']) == v['sha256'])
        print(f'  lens {k:8s} layers={v["source_layers"] if len(v["source_layers"]) < 10 else str(v["source_layers"][0]) + ".." + str(v["source_layers"][-1])} sha={v["sha256"][:12]} {"OK" if ok else "MISSING/CHANGED"}')
    pr = root / 'reports/parity.json'
    print('  parity:', (load(pr)['status'] if pr.exists() else 'not run'))
    conds = ['true']
    if (root / 'config/conditions_manifest.json').exists():
        cm = verify_conditions(root); conds = cm['conditions']
        print('  conditions frozen:', ', '.join(conds), '| tiers', {t['tier']: t['n'] for t in cm['tier_summary']})
    else: print('  conditions: not frozen')
    if a.compact:  # one line per condition (phone-friendly)
        expected = len(readout_plan(lenses, a.readouts.split(','), parse_layers(a.layers) or DEFAULT_LAYERS)) * m['n_shards']
        for cond in conds:
            got = sum(len(v) for v in completion(root, m, cond).values())
            print(f'  {cond:8s} {got:5d}/{expected} files  {100 * got / expected:5.1f}%')
        return
    for cond in conds:
        done = completion(root, m, cond)
        if not done: print(f'  [{cond}] no raw outputs yet'); continue
        for (r, l), s in sorted(done.items()):
            print(f'  [{cond}] {r:14s} L{l:02d}  {len(s):3d}/{m["n_shards"]} shards')


def register_lens(a):
    root = Path(a.root); verify(root)
    lenses = load(root / 'config/lenses.json')
    if a.name in lenses: raise ValueError(f'lens {a.name} already registered; names are immutable')
    lenses[a.name] = lens_entry(a.path); dump(root / 'config/lenses.json', lenses)
    print('REGISTERED', a.name, lenses[a.name]['source_layers'], lenses[a.name]['sha256'])


# ---------------------------------------------------------------- title conditions (false / delete)
K_FALSE = 5
DELETE_PROMPT = 'Who are the authors of the paper ({year})?\nAuthors:'
# tier: max |d year|, n_authors tolerance max(1, rel*n), title-token tolerance max(1, rel*len), max citation-bin distance, donor use cap
TIERS = [('strict', 5, 0.0, .20, 1, K_FALSE), ('medium', 5, .25, .25, 1, K_FALSE),
         ('loose', 8, .34, .30, 1, K_FALSE), ('nearest', None, None, None, None, K_FALSE + 2)]
NEAR_DUP_JACCARD = .6
BIG = 1e6


def condition_names(): return ['true'] + [f'false_{k}' for k in range(K_FALSE)] + ['delete']


def match_false_titles(df, tok):
    """Tiered matched title donors within field: each paper gets K_FALSE distinct donors (best tier first)."""
    import unicodedata, numpy as np, pandas as pd
    from scipy.optimize import linear_sum_assignment
    norm = lambda s: unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    order = sorted(df.citation_bin.unique(), key=lambda b: int(b.split('-')[0].rstrip('+')))
    out = []
    for field, g in df.groupby('field', sort=True):
        g = g.reset_index(drop=True); n = len(g)
        y = pd.to_numeric(g.year).to_numpy(float); na = pd.to_numeric(g.n_authors).to_numpy(float)
        tl = np.array([len(tok(t, add_special_tokens=False).input_ids) for t in g.title], float)
        bi = g.citation_bin.map(order.index).to_numpy(float)
        dy, dna, dtl, db = (abs(v[:, None] - v) for v in (y, na, tl, bi))
        base = ~np.eye(n, dtype=bool)
        surn = [{norm(x.split()[-1]) for x in s.split(';') if x.strip()} for s in g.authors]
        words = [set(re.findall(r'[a-z]{4,}', norm(t))) for t in g.title]
        index = {}
        for i, s in enumerate(surn):
            for w in s: index.setdefault(w, []).append(i)
        for ids in index.values():
            if len(ids) > 1: base[np.ix_(ids, ids)] = False          # shared surname (incl. shared author)
        np.fill_diagonal(base, False)
        for i in range(n):
            if not words[i]: continue
            for j in range(n):
                if i != j and base[i, j] and words[j] and len(words[i] & words[j]) / len(words[i] | words[j]) > NEAR_DUP_JACCARD: base[i, j] = False
        cost = dy / 5 + dna / np.maximum(1, .25 * na[:, None]) + dtl / np.maximum(1, .2 * tl[:, None]) + 1.5 * db
        need = np.full(n, K_FALSE); uses = np.zeros(n, int); taken = np.zeros((n, n), bool)
        for tier, cy, rna, rtl, mdb, cap in TIERS:
            ok = base.copy()
            if cy is not None:
                ok &= (dy <= cy) & (dna <= np.maximum(1, np.round(rna * na[:, None]))) & (dtl <= np.maximum(1, rtl * tl[:, None])) & (db <= mdb)
            while True:
                rows = np.nonzero(need > 0)[0]; cols = np.nonzero(uses < cap)[0]
                if not len(rows) or not len(cols): break
                C = np.where(ok[np.ix_(rows, cols)] & ~taken[np.ix_(rows, cols)], cost[np.ix_(rows, cols)], BIG)
                r, c = linear_sum_assignment(np.hstack([C, np.full((len(rows), len(rows)), BIG / 10)]))
                made = 0
                for i, j in zip(r, c):
                    if j < len(cols) and C[i, j] < BIG:
                        ti, dj = rows[i], cols[j]
                        out.append(dict(paper_id=g.paper_id[ti], donor_paper_id=g.paper_id[dj], donor_title=g.title[dj], tier=tier,
                                        cost=float(cost[ti, dj]), d_year=int(dy[ti, dj]), d_n_authors=int(dna[ti, dj]),
                                        d_title_tokens=int(dtl[ti, dj]), rel_d_title=float(dtl[ti, dj] / tl[ti]), d_bin=int(db[ti, dj]),
                                        target_title_tokens=int(tl[ti]), donor_title_tokens=int(tl[dj])))
                        need[ti] -= 1; uses[dj] += 1; taken[ti, dj] = True; made += 1
                if not made: break
        if (need > 0).any(): raise RuntimeError(f'{field}: {int((need > 0).sum())} papers without {K_FALSE} donors')
    m = pd.DataFrame(out)
    m['tier_rank'] = m.tier.map({t[0]: i for i, t in enumerate(TIERS)})
    m = m.sort_values(['paper_id', 'tier_rank', 'cost', 'donor_paper_id']).reset_index(drop=True)
    m['k'] = m.groupby('paper_id').cumcount()  # false_0 = best match
    return m.drop(columns='tier_rank')


def freeze_conditions(a):
    import pandas as pd
    root = Path(a.root); m, _ = verify(root)
    C = root / 'cohort/conditions'
    if (root / 'config/conditions_manifest.json').exists():
        verify_conditions(root); print('CONDITIONS ALREADY FROZEN; verified'); return
    if C.exists() and any(C.iterdir()): raise FileExistsError(f'non-frozen, non-empty {C}')
    tok = tokenizer()
    papers = pd.read_parquet(root / 'cohort/papers.parquet')
    ctx = pd.read_parquet(root / 'cohort/contexts.parquet')
    longest = ctx.groupby('paper_id').n_name_tokens.max()
    fm = match_false_titles(papers, tok)
    rows = []
    for p in papers.itertuples():
        prompts = {'true': PROMPT.format(title=p.title, year=p.year), 'delete': DELETE_PROMPT.format(year=p.year)}
        for d in fm[fm.paper_id == p.paper_id].itertuples(): prompts[f'false_{d.k}'] = PROMPT.format(title=d.donor_title, year=p.year)
        for cond, pr in prompts.items():
            ids = tok(pr).input_ids
            if cond == 'true' and ids != json.loads(p.prompt_ids): raise RuntimeError(f'true prompt ids differ from frozen: {p.paper_id}')
            if len(ids) + int(longest.get(p.paper_id, 1)) - 1 > MAX_CONTEXT: raise RuntimeError(f'context too long {p.paper_id} {cond}')
            rows.append(dict(paper_id=p.paper_id, condition=cond, prompt=pr, prompt_ids=json.dumps(ids), n_prompt_tokens=len(ids)))
    pdf = pd.DataFrame(rows)
    if len(pdf) != len(papers) * len(condition_names()): raise RuntimeError('missing condition prompts')
    C.mkdir(parents=True, exist_ok=True)
    fm.to_parquet(C / 'false_titles.parquet', index=False); pdf.to_parquet(C / 'prompts.parquet', index=False)
    tiers = fm.groupby('tier').agg(n=('k', 'size'), median_d_year=('d_year', 'median'), p90_d_year=('d_year', lambda v: v.quantile(.9)),
                                   median_rel_d_title=('rel_d_title', 'median'), max_d_n_authors=('d_n_authors', 'max')).reset_index()
    per_paper = fm.groupby('paper_id').tier.apply(lambda s: (s == 'strict').sum()).value_counts().sort_index()
    cm = dict(created=now(), script_sha256=sha_file(__file__), base_protocol_sha256=m['protocol_sha256'], conditions=condition_names(),
              K=K_FALSE, prompt=PROMPT, delete_prompt=DELETE_PROMPT, false_title_year='target paper year (title swapped only)',
              matching=dict(scope='same field; donors within citation bin distance per tier', hard_exclusions='self; any shared surname; title word-Jaccard > 0.6',
                            cost='|dyear|/5 + |dn_authors|/max(1,.25n) + |dtitle_tokens|/max(1,.2len) + 1.5*|dbin|',
                            tiers=[dict(zip(['tier', 'max_d_year', 'n_authors_rel_tol', 'title_rel_tol', 'max_d_bin', 'donor_use_cap'], t)) for t in TIERS],
                            algorithm='per tier, repeated min-cost assignment (scipy linear_sum_assignment) with dummy columns; a donor used at most once per round; false_0 = best tier/cost'),
              tier_summary=tiers.to_dict('records'), papers_by_n_strict_donors={int(k): int(v) for k, v in per_paper.items()},
              donor_use_max=int(fm.donor_paper_id.value_counts().max()),
              outputs={rel: sha_file(root / rel) for rel in ['cohort/conditions/false_titles.parquet', 'cohort/conditions/prompts.parquet']})
    dump(root / 'config/conditions_manifest.json', cm)
    print('CONDITIONS FROZEN', len(fm), 'false-title assignments;', tiers.to_string(index=False))
    print('papers by number of strict donors', cm['papers_by_n_strict_donors'], 'max donor use', cm['donor_use_max'])


def verify_conditions(root):
    cm = load(root / 'config/conditions_manifest.json')
    for rel, h in cm['outputs'].items():
        if sha_file(root / rel) != h: raise ValueError(f'FROZEN CONDITION FILE CHANGED {rel}')
    return cm


def condition_prompts(root, papers, cond):
    """{paper_id: (prompt, prompt_ids)} for a condition; 'true' comes from the base freeze."""
    import pandas as pd
    if cond == 'true':
        return {p.paper_id: (PROMPT.format(title=p.title, year=p.year), json.loads(p.prompt_ids)) for p in papers.itertuples()}, None
    cm = verify_conditions(root)
    if cond not in cm['conditions']: raise ValueError(f'unknown condition {cond}; frozen: {cm["conditions"]}')
    pdf = pd.read_parquet(root / 'cohort/conditions/prompts.parquet'); pdf = pdf[pdf.condition == cond]
    return {r.paper_id: (r.prompt, json.loads(r.prompt_ids)) for r in pdf.itertuples()}, cm['outputs']['cohort/conditions/prompts.parquet']


# ---------------------------------------------------------------- GPU side
def load_model():
    """Whole model on the visible GPUs (1 x H200/A100-80 or split over 2 x A100-40); never CPU offload."""
    import torch, transformers, jlens
    tok = tokenizer()
    n = torch.cuda.device_count()
    if n == 0: raise RuntimeError('no GPU visible')
    gib = [torch.cuda.get_device_properties(i).total_memory / 2**30 for i in range(n)]
    # headroom: GPU0 also holds embeddings + activations; last GPU holds lm_head + vocab logits
    max_memory = {i: f'{int(g - (6 if i in (0, n - 1) else 3))}GiB' for i, g in enumerate(gib)}
    max_memory['cpu'] = '0GiB'
    hf = transformers.AutoModelForCausalLM.from_pretrained(MODEL, revision=REV, dtype=torch.bfloat16, device_map='auto',
                                                           max_memory=max_memory, low_cpu_mem_usage=True).eval()
    placement = sorted({str(v) for v in hf.hf_device_map.values()})
    if any(p in ('cpu', 'disk') for p in placement): raise RuntimeError(f'model offloaded to CPU/disk: {placement}')
    print('model placement', placement, 'gpus', [torch.cuda.get_device_name(i) for i in range(n)], flush=True)
    return jlens.from_hf(hf, tok), tok


def layer_device(model, l):
    return next(model.layers[l].parameters()).device


def readout_plan(lenses, readouts, layers):
    """[(readout, layer)] requested; checks layer availability per lens."""
    plan = []
    for r in readouts:
        if r == 'final': plan.append(('final', FINAL_LAYER)); continue
        if r == 'logit': plan += [('logit', l) for l in layers]; continue
        name = r[len('jlens_'):] if r.startswith('jlens_') else None
        if name not in lenses: raise ValueError(f'unknown readout {r}; registered lenses {list(lenses)}')
        miss = [l for l in layers if l not in lenses[name]['source_layers']]
        if miss: raise ValueError(f'{r}: layers {miss} not fitted (has {lenses[name]["source_layers"]})')
        plan += [(r, l) for l in layers]
    return plan


def open_lenses(lenses, plan, model):
    """Each kept J_l goes to the GPU that holds decoder block l, so transport never copies across GPUs."""
    import jlens
    out = {}
    for r, l in plan:
        if not r.startswith('jlens_'): continue
        name = r[len('jlens_'):]
        if name not in out:
            e = lenses[name]
            if sha_file(e['path']) != e['sha256']: raise ValueError(f'lens {name} file changed')
            out[name] = jlens.JacobianLens.load(e['path'])
            keep = {ll for rr, ll in plan if rr == r}
            for k in list(out[name].jacobians):  # keep only needed layers, on GPU (same dtype -> transport math unchanged)
                if k in keep: out[name].jacobians[k] = out[name].jacobians[k].to(layer_device(model, k))
                else: del out[name].jacobians[k]
    return out


def fast_readout(model, lenses, ids, positions, plan, torch):
    """One forward; returns {(readout, layer): logits[n_pos, vocab] float}."""
    from jlens.hooks import ActivationRecorder
    need = sorted({l for _, l in plan} | {FINAL_LAYER})
    x = torch.tensor([ids], device=model.input_device)
    with torch.inference_mode():
        with ActivationRecorder(model.layers, at=need) as rec:
            model.forward(x)
            acts = {i: rec.activations[i].detach() for i in need}
        res = {}
        for r, l in plan:
            h = acts[l][0][positions].float()
            if r.startswith('jlens_'): h = lenses[r[len('jlens_'):]].transport(h, l)
            res[(r, l)] = model.unembed(h).float()
    return res


def score(logits, gold, torch):
    gold = gold.to(logits.device)
    g = logits.gather(1, gold[:, None])
    rank = (logits > g).sum(1) + 1
    ties = (logits == g).sum(1) - 1
    lp = torch.log_softmax(logits, -1).gather(1, gold[:, None])[:, 0]
    top1 = logits.argmax(1)
    return rank.int().cpu().numpy(), ties.int().cpu().numpy(), lp.float().cpu().numpy(), top1.int().cpu().numpy()


def gpu_setup(a):
    import torch, pandas as pd
    root = Path(a.root); m, lenses = verify(root)
    readouts = a.readouts.split(',')
    layers = parse_layers(a.layers) or DEFAULT_LAYERS
    plan = readout_plan(lenses, readouts, layers)
    papers = pd.read_parquet(root / 'cohort/papers.parquet')
    ctx = pd.read_parquet(root / 'cohort/contexts.parquet')
    toks = pd.read_parquet(root / 'cohort/name_tokens.parquet', columns=['row_id', 'context_id', 'token_index', 'token_id'])
    return torch, root, m, lenses, plan, papers, ctx, toks


def parity(a):
    """Fast path (one forward, all positions) vs jlens apply on each prefix separately (Stage 6 style)."""
    torch, root, m, lenses, plan, papers, ctx, toks = gpu_setup(a)
    model, tok = load_model()
    L = open_lenses(lenses, plan, model)
    if not L: raise RuntimeError('parity needs at least one jlens_* readout (apply() lives on a lens object)')
    any_lens = next(iter(L.values()))  # use_jacobian=False never touches the J matrices
    import numpy as np
    rng = np.random.default_rng(10)
    sample = ctx.iloc[rng.choice(len(ctx), size=min(a.n, len(ctx)), replace=False)].sort_values('context_id')
    pids_by = dict(zip(papers.paper_id, papers.prompt_ids))
    worst = {}; rank_mismatch = {}; n_rows = 0
    for _, c in sample.iterrows():
        pids = json.loads(pids_by[c.paper_id]); t = toks[toks.context_id == c.context_id].sort_values('token_index')
        name = t.token_id.tolist(); ids = pids + name[:-1]
        pos = [len(pids) - 1 + j for j in range(len(name))]
        fast = fast_readout(model, L, ids, pos, plan, torch)
        gold = torch.tensor(name, device=model.input_device)
        for j in range(len(name)):
            pre = pids + name[:j]
            for r, l in plan:
                if r == 'final':  # apply's second return value is the actual final-layer logits
                    _, ref, _ = apply_on_ids(model, any_lens, pre, [62], False, torch)
                else:
                    lens = L[r[len('jlens_'):]] if r.startswith('jlens_') else any_lens
                    out, _, _ = apply_on_ids(model, lens, pre, [l], r.startswith('jlens_'), torch)
                    ref = out[l]
                f = fast[(r, l)][j:j + 1].cpu(); ref = ref[-1:].float()
                d = (f - ref).abs().max().item()
                worst[(r, l)] = max(worst.get((r, l), 0.0), d)
                rf = int((f[0] > f[0, name[j]]).sum()) + 1; rr = int((ref[0] > ref[0, name[j]]).sum()) + 1
                if rf != rr: rank_mismatch.setdefault((r, l), []).append(dict(context_id=int(c.context_id), j=j, fast=rf, ref=rr))
            n_rows += 1
    status = 'PASS' if all(v <= a.tol for v in worst.values()) else 'FAIL'
    rep = dict(status=status, created=now(), n_contexts=len(sample), n_token_positions=n_rows, tolerance_max_abs_logit=a.tol,
               max_abs_logit_diff={f'{r}@L{l}': v for (r, l), v in worst.items()},
               rank_mismatches={f'{r}@L{l}': v[:20] for (r, l), v in rank_mismatch.items()},
               n_rank_mismatches={f'{r}@L{l}': len(v) for (r, l), v in rank_mismatch.items()},
               lenses={k: lenses[k]['sha256'] for k in L}, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], torch=torch.__version__)
    prev = load(root / 'reports/parity.json') if (root / 'reports/parity.json').exists() else {'runs': []}
    prev['runs'] = prev.get('runs', []) + [rep]; prev['status'] = status if status == 'FAIL' else ('PASS' if all(x['status'] == 'PASS' for x in prev['runs']) else 'FAIL')
    prev['passed_pairs'] = sorted({k for x in prev['runs'] if x['status'] == 'PASS' for k in x['max_abs_logit_diff']})
    dump(root / 'reports/parity.json', prev)
    print(json.dumps({k: rep[k] for k in ('status', 'n_contexts', 'n_token_positions', 'max_abs_logit_diff', 'n_rank_mismatches')}, indent=1))
    if status != 'PASS': sys.exit(2)


def apply_on_ids(model, lens, ids, layers, use_jacobian, torch):
    """JacobianLens.apply with forced token ids (as Stage 5 readout)."""
    import jlens
    saved = model.encode
    fixed = torch.tensor([ids], device=model.input_device)
    model.encode = lambda _t, max_length=512: fixed
    try:
        return lens.apply(model, '', layers=layers, positions=[-1], max_seq_len=MAX_CONTEXT, use_jacobian=use_jacobian)
    finally:
        model.encode = saved


def run(a):
    torch, root, m, lenses, plan, papers, ctx, toks = gpu_setup(a)
    import numpy as np
    pr = root / 'reports/parity.json'
    if not a.skip_parity_gate:
        if not pr.exists() or load(pr)['status'] != 'PASS': raise RuntimeError('run parity first (reports/parity.json PASS)')
        passed = set(load(pr)['passed_pairs'])
        miss = [f'{r}@L{l}' for r, l in plan if f'{r}@L{l}' not in passed]
        if miss: raise RuntimeError(f'no parity PASS for {miss}; run parity with these readouts/layers')
    shards = parse_shards(a.shards, m['n_shards'])
    jobs = []
    for cond in a.condition.split(','):  # several conditions share one model load, in the order given
        prompts, cond_sha = condition_prompts(root, papers, cond)
        todo = [(k, [(r, l) for r, l in plan if not out_file(root, r, l, k, cond).exists()]) for k in shards]
        todo = [(k, p) for k, p in todo if p]
        if todo: jobs.append((cond, prompts, cond_sha, todo))
        else: print(f'NOTHING TO DO [{cond}]')
    if not jobs: return
    model, tok = load_model()
    L = open_lenses(lenses, plan, model)
    env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], script_sha256=sha_file(__file__))
    t_start = time.monotonic()
    for cond, prompts, cond_sha, todo in jobs:
      for k, kplan in todo:
        t0 = time.monotonic()
        cs = ctx[ctx.shard == k].sort_values('context_id')
        tk = toks[toks.context_id.isin(cs.context_id)].sort_values('row_id')
        rows = tk.row_id.to_numpy()
        n = len(rows); off = rows[0] if n else 0
        if n and not np.array_equal(rows, np.arange(off, off + n)): raise RuntimeError('row ids not contiguous in shard')
        buf = {rl: {x: np.zeros(n, dt) for x, dt in (('rank', np.int32), ('ties', np.int32), ('logprob', np.float32), ('top1', np.int32))} for rl in kplan}
        enc_checked = set()
        for _, c in cs.iterrows():
            prompt, pids = prompts[c.paper_id]
            if c.paper_id not in enc_checked:
                if model.encode(prompt, max_length=MAX_CONTEXT).reshape(-1).tolist() != pids:
                    raise RuntimeError(f'prompt encoding differs from frozen ids: {c.paper_id}')
                enc_checked.add(c.paper_id)
            t = tk[tk.context_id == c.context_id]
            name = t.token_id.tolist(); idx = (t.row_id.to_numpy() - off)
            ids = pids + name[:-1]; pos = [len(pids) - 1 + j for j in range(len(name))]
            res = fast_readout(model, L, ids, pos, kplan, torch)
            gold = torch.tensor(name, device=model.input_device)
            for rl, logits in res.items():
                rk, ti, lp, t1 = score(logits, gold, torch)
                b = buf[rl]; b['rank'][idx] = rk; b['ties'][idx] = ti; b['logprob'][idx] = lp; b['top1'][idx] = t1
        for (r, l), b in buf.items():
            if n and (b['rank'] < 1).any(): raise RuntimeError(f'unfilled rows {r} L{l} shard {k}')
            lens_sha = lenses[r[len('jlens_'):]]['sha256'] if r.startswith('jlens_') else None
            meta = dict(readout=r, layer=l, shard=k, row_start=int(off), n_rows=n, protocol_sha256=m['protocol_sha256'],
                        condition=cond, condition_prompts_sha256=cond_sha,
                        lens_sha256=lens_sha, created=now(), **env)
            f = out_file(root, r, l, k, cond); f.parent.mkdir(parents=True, exist_ok=True)
            tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
            np.savez(tmp, row_id=rows, meta=np.array(json.dumps(meta, sort_keys=True)), **b); os.replace(tmp, f)
        el = time.monotonic() - t0
        print(f'{now()} [{cond}] shard {k:03d} contexts={len(cs)} tokens={n} pairs={len(kplan)} {el:.0f}s total={(time.monotonic()-t_start)/60:.1f}min', flush=True)
        if a.max_minutes and (time.monotonic() - t_start) / 60 + 1.5 * el / 60 > a.max_minutes:
            print('time budget reached; remaining shards left for next job', flush=True); return


def remaining(a):
    """CPU: count missing (condition, readout, layer, shard) files; prints one integer (used by the self-requeueing worker)."""
    root = Path(a.root); m, lenses = verify(root)
    plan = readout_plan(lenses, a.readouts.split(','), parse_layers(a.layers) or DEFAULT_LAYERS)
    shards = parse_shards(a.shards, m['n_shards'])
    n = sum(not out_file(root, r, l, k, c).exists() for c in a.condition.split(',') for r, l in plan for k in shards)
    print(n)


# ---------------------------------------------------------------- CPU analysis
def load_raw(root, m, lenses, require_complete=True, cond='true'):
    import numpy as np, pandas as pd
    done = completion(root, m, cond); frames = []
    cond_sha = None if cond == 'true' else verify_conditions(root)['outputs']['cohort/conditions/prompts.parquet']
    for (r, l), s in sorted(done.items()):
        if len(s) != m['n_shards']:
            if require_complete: print(f'skip incomplete [{cond}] {r} L{l}: {len(s)}/{m["n_shards"]} shards'); continue
        parts = []
        for k in sorted(s):
            z = np.load(out_file(root, r, l, k, cond))
            meta = json.loads(str(z['meta']))
            if meta.get('condition', 'true') != cond or meta.get('condition_prompts_sha256') != cond_sha: raise ValueError(f'condition mismatch {cond} {r} L{l} shard {k}')
            if meta['protocol_sha256'] != m['protocol_sha256']: raise ValueError(f'protocol mismatch {r} L{l} shard {k}')
            if r.startswith('jlens_') and meta['lens_sha256'] != lenses[r[6:]]['sha256']: raise ValueError(f'lens sha mismatch {r} L{l} shard {k}')
            parts.append(pd.DataFrame({'row_id': z['row_id'], 'rank': z['rank'], 'ties': z['ties'], 'logprob': z['logprob'], 'top1': z['top1']}))
        d = pd.concat(parts); d['readout'] = r; d['layer'] = l; frames.append(d)
    return pd.concat(frames) if frames else None


def crosscheck(a):
    import pandas as pd
    root = Path(a.root); m, lenses = verify(root)
    s6 = BASE / '351_stage6/raw/token_layer_scores.csv'
    old = pd.read_csv(s6)
    toks = pd.read_parquet(root / 'cohort/name_tokens.parquet'); ctx = pd.read_parquet(root / 'cohort/contexts.parquet')
    raw = load_raw(root, m, lenses, require_complete=False)
    if raw is None: raise RuntimeError('no raw outputs')
    j = raw.merge(toks[['row_id', 'context_id', 'token_index', 'token_id']], on='row_id').merge(ctx[['context_id', 'paper_id', 'author']], on='context_id')
    j['mode'] = j.readout.map({'jlens_public': 'jlens', 'logit': 'vanilla', 'final': 'final'})
    x = j.dropna(subset=['mode']).merge(old, on=['paper_id', 'author', 'token_index', 'mode', 'layer'], suffixes=('', '_s6'))
    if x.empty: print('no overlap with Stage 6 yet (Pilot50 shards not computed?)'); return
    x['token_ok'] = x.token_id == x.token_id_s6
    x['rank_eq'] = x['rank'] == x['rank_s6']
    x['lp_diff'] = (x.logprob - x.logprob_s6).abs()
    rep = x.groupby(['mode', 'layer']).agg(n=('rank', 'size'), token_id_match=('token_ok', 'mean'), rank_exact=('rank_eq', 'mean'),
                                           max_logprob_diff=('lp_diff', 'max'), median_logprob_diff=('lp_diff', 'median')).reset_index()
    rep.to_csv(root / 'reports/crosscheck_stage6.csv', index=False)
    print(rep.to_string(index=False))


METRICS = {  # paper-level metric -> label. nlr = log10(1/rank) = -log10(rank): 0 = rank 1, -1 = rank 10, min -5.18
    'mean_nlr': 'mean log10(1/rank) per token',
    'author_mean_nlr': 'mean over authors of per-author mean log10(1/rank)',
    'mean_nlr_surname_first': 'mean log10(1/rank), surname first token',
    'mean_rr': 'mean 1/rank per token',
    'top1_share': 'share of tokens at rank 1',
}
SUMS = ['sum_nlr', 'sum_rr']  # within-paper only (depend on number of tokens)
MIN_STRATUM = 30
LOW_BINS = ('0-2', '3-4')
HIGH_FROM = 129
B_BOOT = 2000


def bin_lo(b): return int(str(b).split('-')[0].rstrip('+'))


def paper_scores(d, papers):
    import numpy as np, pandas as pd
    d = d.assign(rr=1.0 / d['rank'], nlr=-np.log10(d['rank'].astype(float)), top1_hit=(d['rank'] == 1).astype(float))
    key = ['paper_id', 'readout', 'layer']
    ps = d.groupby(key).agg(sum_nlr=('nlr', 'sum'), mean_nlr=('nlr', 'mean'), sum_rr=('rr', 'sum'), mean_rr=('rr', 'mean'),
                            top1_share=('top1_hit', 'mean'), n_tokens=('nlr', 'size')).reset_index()
    au = d.groupby(key + ['author_index'])[['nlr', 'rr']].mean().groupby(level=[0, 1, 2]).mean()
    ps = ps.merge(au.rename(columns={'nlr': 'author_mean_nlr', 'rr': 'author_mean_rr'}).reset_index(), on=key)
    for role in ['surname_first', 'surname_cont', 'initial_first', 'given_first', 'given_cont', 'punct']:
        r = d[d.role == role].groupby(key).agg(**{f'mean_nlr_{role}': ('nlr', 'mean'), f'mean_rr_{role}': ('rr', 'mean'),
                                                f'n_{role}': ('nlr', 'size')}).reset_index()
        ps = ps.merge(r, on=key, how='left')
    ps = ps.merge(papers, on='paper_id')
    ps['bin_lo'] = ps.citation_bin.map(bin_lo)
    ps['log10_citations'] = np.log10(pd.to_numeric(ps.citations, errors='coerce').fillna(0) + 1)
    ps['mc_team_a'] = pd.to_numeric(ps.mc_team_a, errors='coerce')
    return ps


def stratified_diff(ps, col, a, b, strata, metrics, rng, min_n=MIN_STRATUM):
    """Pooled within-stratum mean difference a-b (weights n_a*n_b/(n_a+n_b)); bootstrap resamples papers within stratum x group."""
    import numpy as np
    out = []
    for (r, l), sub in ps.groupby(['readout', 'layer']):
        cells = []
        for s, ss in sub.groupby(strata):
            A = ss[ss[col] == a][metrics].to_numpy(float); Bm = ss[ss[col] == b][metrics].to_numpy(float)
            if len(A) >= min_n and len(Bm) >= min_n: cells.append((s, A, Bm))
        if not cells: continue
        w = np.array([len(A) * len(Bm) / (len(A) + len(Bm)) for _, A, Bm in cells]); w = w / w.sum()
        est = sum(wi * (np.nanmean(A, 0) - np.nanmean(Bm, 0)) for wi, (_, A, Bm) in zip(w, cells))
        boot = np.zeros((B_BOOT, len(metrics)))
        for wi, (_, A, Bm) in zip(w, cells):
            boot += wi * (np.nanmean(A[rng.integers(0, len(A), (B_BOOT, len(A)))], 1) - np.nanmean(Bm[rng.integers(0, len(Bm), (B_BOOT, len(Bm)))], 1))
        row = dict(readout=r, layer=l, n_strata=len(cells), strata=';'.join(str(s) for s, _, _ in cells),
                   n_a=int(sum(len(A) for _, A, _ in cells)), n_b=int(sum(len(Bm) for _, _, Bm in cells)))
        for k, mt in enumerate(metrics):
            row[f'{mt}_diff'] = est[k]; row[f'{mt}_lo'], row[f'{mt}_hi'] = np.percentile(boot[:, k], [2.5, 97.5])
        out.append(row)
    import pandas as pd
    return pd.DataFrame(out)


def group_means(ps, by, metrics, rng, ci=True, sums=SUMS):
    import numpy as np, pandas as pd
    out = []
    for k, sub in ps.groupby(by + ['readout', 'layer']):
        row = dict(zip(by + ['readout', 'layer'], k), n_papers=len(sub))
        for mt in metrics + list(sums):
            v = sub[mt].to_numpy(float); v = v[~np.isnan(v)]
            row[f'{mt}_mean'] = v.mean() if len(v) else np.nan
            if ci and mt in metrics and len(v) > 1:
                mm = v[rng.integers(0, len(v), (B_BOOT, len(v)))].mean(1); row[f'{mt}_lo'], row[f'{mt}_hi'] = np.percentile(mm, [2.5, 97.5])
        out.append(row)
    return pd.DataFrame(out)


def graded(ps, metrics):
    """mc_team_a 0..4 among R0/R1 papers: metric centred within citation bin; per-level means + Spearman."""
    import pandas as pd
    from scipy.stats import spearmanr
    s = ps[ps.recall_level.isin(['R0', 'R1']) & ps.mc_team_a.notna()].copy()
    out = []
    for (r, l), sub in s.groupby(['readout', 'layer']):
        sub = sub.copy()
        for mt in metrics: sub[mt + '_c'] = sub[mt] - sub.groupby('citation_bin')[mt].transform('mean')
        for mt in metrics:
            row = dict(readout=r, layer=l, metric=mt, n=len(sub))
            for a_, g in sub.groupby('mc_team_a'): row[f'a{int(a_)}_centred_mean'] = g[mt + '_c'].mean(); row[f'a{int(a_)}_n'] = len(g)
            ok = sub[mt + '_c'].notna(); rho, p = spearmanr(sub.loc[ok, 'mc_team_a'], sub.loc[ok, mt + '_c'])
            row['spearman_rho_within_bin'] = rho; row['p'] = p; out.append(row)
    return pd.DataFrame(out)


def citation_effect(ps, metrics):
    import pandas as pd
    from scipy.stats import spearmanr
    out = []
    for (g, r, l), sub in ps[ps.group_tight.isin(['target', 'control', 'guard'])].groupby(['group_tight', 'readout', 'layer']):
        for mt in metrics:
            ok = sub[mt].notna()
            if ok.sum() < 10: continue
            rho, p = spearmanr(sub.loc[ok, 'log10_citations'], sub.loc[ok, mt])
            out.append(dict(group_tight=g, readout=r, layer=l, metric=mt, n=int(ok.sum()), spearman_rho=rho, p=p))
    return pd.DataFrame(out)


def analyze(a):
    import numpy as np, pandas as pd
    root = Path(a.root); m, lenses = verify(root)
    raw = load_raw(root, m, lenses, require_complete=not a.allow_partial)
    if raw is None: raise RuntimeError('no complete (readout, layer) outputs')
    toks = pd.read_parquet(root / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'role'])
    papers = pd.read_parquet(root / 'cohort/papers.parquet').drop(columns=['prompt_ids', 'shard'])
    ps = paper_scores(raw.merge(toks, on='row_id'), papers)
    S = root / 'summary'; S.mkdir(exist_ok=True); (root / 'figures').mkdir(exist_ok=True)
    ps.to_parquet(S / 'paper_scores.parquet', index=False)
    rng = np.random.default_rng(3510); mets = list(METRICS)
    T = {}
    T['A_group_layer'] = group_means(ps, ['group_tight'], mets, rng)
    T['A_group_bin_layer'] = group_means(ps, ['group_tight', 'citation_bin'], mets, rng, ci=False)
    T['B_target_vs_control_within_bin'] = stratified_diff(ps, 'group_tight', 'target', 'control', 'citation_bin', mets, rng)
    T['B_sens_drop_low_bins'] = stratified_diff(ps[~ps.citation_bin.isin(LOW_BINS)], 'group_tight', 'target', 'control', 'citation_bin', mets, rng)
    T['B_sens_plain_group'] = stratified_diff(ps, 'group', 'target', 'control', 'citation_bin', mets, rng)
    T['B_sens_bin_x_field'] = stratified_diff(ps, 'group_tight', 'target', 'control', ['citation_bin', 'field'], mets, rng, min_n=10)
    T['B_sens_strong_both'] = stratified_diff(ps, 'group_both', 'target', 'control', ['readout'], mets, rng, min_n=10)  # 500-paper second draw, pooled
    hi = ps[ps.bin_lo >= HIGH_FROM]
    T['D_ladder_high_citation'] = group_means(hi, ['group_tight'], mets, rng)
    T['D_guard_vs_target_within_bin'] = stratified_diff(hi, 'group_tight', 'guard', 'target', 'citation_bin', mets, rng, min_n=10)
    T['C_graded_mc_team_a'] = graded(ps, mets)
    T['E_citation_within_group'] = citation_effect(ps, mets)
    T['paper_best_layer'] = best_layer(ps)
    for k, v in T.items(): v.to_csv(S / f'{k}.csv', index=False)
    figures(root, T)
    write_report(root, m, ps, T)
    print('ANALYZED', sorted(ps.readout.unique()), sorted(ps.layer.unique()), '->', S)


def best_layer(ps):
    """Within each paper and readout, the layer with the highest sum log10(1/rank) (same token set across layers)."""
    sub = ps[ps.readout != 'final']
    idx = sub.groupby(['paper_id', 'readout']).sum_nlr.idxmax()
    b = sub.loc[idx, ['paper_id', 'readout', 'layer', 'group_tight', 'citation_bin']]
    return b.groupby(['readout', 'group_tight', 'layer']).size().rename('n_papers_best').reset_index()


def figures(root, T):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    tab = T['A_group_layer']
    groups = [g for g in ['guard', 'target', 'control', 'excluded'] if g in set(tab.group_tight)]
    for mt in ['mean_nlr', 'author_mean_nlr', 'mean_nlr_surname_first', 'mean_rr']:
        fig, axes = plt.subplots(1, len(groups), figsize=(4.2 * len(groups), 3.6), sharey=True, squeeze=False)
        for ax, g in zip(axes[0], groups):
            for r, sub in tab[(tab.group_tight == g) & (tab.readout != 'final')].groupby('readout'):
                sub = sub.sort_values('layer'); ax.plot(sub.layer, sub[f'{mt}_mean'], marker='o', label=r)
                ax.fill_between(sub.layer, sub[f'{mt}_lo'], sub[f'{mt}_hi'], alpha=.15)
            fin = tab[(tab.group_tight == g) & (tab.readout == 'final')]
            if len(fin): ax.axhline(fin[f'{mt}_mean'].iloc[0], color='k', ls='--', lw=1, label='final L63')
            ax.set(title=f'{g} (n={int(tab[tab.group_tight == g].n_papers.max())})', xlabel='layer'); ax.grid(alpha=.2)
        axes[0][0].set_ylabel(METRICS[mt]); axes[0][-1].legend(fontsize=7)
        fig.tight_layout(); fig.savefig(root / f'figures/A_{mt}_by_group.png', dpi=150); plt.close(fig)
    d = T['B_target_vs_control_within_bin']
    if len(d):
        fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), squeeze=False)
        for ax, mt in zip(axes[0], ['mean_nlr', 'author_mean_nlr', 'mean_nlr_surname_first']):
            for r, sub in d[d.readout != 'final'].groupby('readout'):
                sub = sub.sort_values('layer'); ax.plot(sub.layer, sub[f'{mt}_diff'], marker='o', label=r)
                ax.fill_between(sub.layer, sub[f'{mt}_lo'], sub[f'{mt}_hi'], alpha=.15)
            ax.axhline(0, color='k', lw=.8); ax.set(title=f'target - control within bin\n{METRICS[mt]}', xlabel='layer'); ax.grid(alpha=.2)
        axes[0][-1].legend(fontsize=7); fig.tight_layout(); fig.savefig(root / 'figures/B_target_minus_control.png', dpi=150); plt.close(fig)


def write_report(root, m, ps, T):
    def table(df, val, lo, hi, rowkey):
        layers = sorted(df.layer.unique())
        out = ['| ' + rowkey + ' | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---|' + '---|' * len(layers)]
        for r, s in df.groupby(rowkey):
            c = {int(x.layer): f'{getattr(x, val):.3f} [{getattr(x, lo):.3f}, {getattr(x, hi):.3f}]' for x in s.itertuples()}
            out.append(f'| {r} | ' + ' | '.join(c.get(int(l), '') for l in layers) + ' |')
        return out
    L = ['# Stage 10 - author-name token readout by layer', '', f'Generated {now()}. Protocol sha256 `{m["protocol_sha256"]}`.', '',
         f'{m["n_papers"]} papers, {m["n_contexts"]} author contexts, {m["n_tokens"]} name tokens. Present: '
         + ', '.join(f'{r}@{sorted(ps[ps.readout == r].layer.unique())}' for r in sorted(ps.readout.unique())), '',
         'Main metric: log10(1/rank) of the gold name token (0 = rank 1, -1 = rank 10, minimum -5.18).', '',
         '## A. Mean log10(1/rank) per token by group (95% bootstrap CI over papers)', '']
    for g, sub in T['A_group_layer'].groupby('group_tight'):
        L += [f'### {g}', ''] + table(sub, 'mean_nlr_mean', 'mean_nlr_lo', 'mean_nlr_hi', 'readout') + ['']
    d = T['B_target_vs_control_within_bin']
    if len(d):
        L += ['## B. target - control within citation bin (pooled, bins with >= 30 papers in both groups)', '',
              f'Strata used: {d.strata.iloc[0]}', ''] + table(d, 'mean_nlr_diff', 'mean_nlr_lo', 'mean_nlr_hi', 'readout') + ['']
    L += ['## Files', '', 'summary/: A_* descriptive, B_* target-control (+ sensitivity: drop 0-4 bins, plain group, bin x field, strong_both), '
          'C_graded_mc_team_a, D_* high-citation ladder (>=129), E_citation_within_group, paper_best_layer, paper_scores.parquet.', '',
          '## Caveats', '',
          '- rank measures predictability, not memory alone: "." after an initial, surname continuations, common names are guessable without the paper. Compare against the later title-dependence control.',
          '- Name format matters (initials vs full given names); role-specific metrics separate them.',
          '- Sums (sum_nlr, sum_rr) depend on the number of tokens: use only within a paper (across layers/readouts).',
          '- Group and citation are confounded (target share 25% at 0-2 vs 99% at 4097+): only within-bin contrasts (B) compare groups.',
          '- Low bins (0-4): target is near the 25% fixed-preference rate; see B_sens_drop_low_bins.',
          '- Each author is scored alone after "Authors:". Ranks use bf16-rounded logits; ties stored, rank counts only strictly greater logits.']
    (root / 'reports/stage10_report.md').write_text('\n'.join(L) + '\n')


TITLE_BASE = ['mean_nlr', 'author_mean_nlr', 'mean_nlr_surname_first', 'mean_nlr_surname_cont', 'mean_nlr_initial_first',
              'mean_nlr_given_first', 'mean_nlr_punct', 'mean_rr']


def analyze_title(a):
    """spec = true - mean(false_k) (paper-specific), total = true - delete, topic = mean(false_k) - delete; same token set, so paired."""
    import numpy as np, pandas as pd
    root = Path(a.root); m, lenses = verify(root); cm = verify_conditions(root)
    papers = pd.read_parquet(root / 'cohort/papers.parquet').drop(columns=['prompt_ids', 'shard'])
    toks = pd.read_parquet(root / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'role'])
    key = ['paper_id', 'readout', 'layer']; per = {}
    for cond in cm['conditions']:
        raw = load_raw(root, m, lenses, require_complete=True, cond=cond)
        if raw is None: raise RuntimeError(f'condition {cond}: no complete outputs')
        ps = paper_scores(raw.merge(toks, on='row_id'), papers)
        per[cond] = ps.set_index(key)[TITLE_BASE]
        if cond == 'true': info = ps.drop(columns=[c for c in ps.columns if c in TITLE_BASE or c.startswith(('sum_', 'mean_', 'author_', 'n_', 'top1'))]).drop_duplicates(key).set_index(key)
        del raw, ps
    common = per['true'].index
    for cond, v in per.items(): common = common.intersection(v.index)
    if len(common) < len(per['true'].index): print(f'note: {len(per["true"].index) - len(common)} (paper, readout, layer) rows missing in some condition')
    fk = [f'false_{k}' for k in range(cm['K'])]
    T = per['true'].loc[common]; D = per['delete'].loc[common]
    F = np.stack([per[c].loc[common].to_numpy(float) for c in fk])            # [K, rows, metrics]
    ft = pd.read_parquet(root / 'cohort/conditions/false_titles.parquet')
    strict = ft.pivot(index='paper_id', columns='k', values='tier').eq('strict').reindex(common.get_level_values(0)).to_numpy().T  # [K, rows]
    Fs = np.where(strict[:, :, None], F, np.nan)
    out = pd.DataFrame(index=common)
    for i, mt in enumerate(TITLE_BASE):
        fmean = F[:, :, i].mean(0)
        out[f'true_{mt}'] = T[mt].to_numpy(); out[f'false_{mt}'] = fmean; out[f'delete_{mt}'] = D[mt].to_numpy()
        out[f'spec_{mt}'] = T[mt].to_numpy() - fmean
        out[f'total_{mt}'] = T[mt].to_numpy() - D[mt].to_numpy()
        out[f'topic_{mt}'] = fmean - D[mt].to_numpy()
        with warnings.catch_warnings():  # papers without any strict donor -> NaN (expected)
            warnings.simplefilter('ignore', RuntimeWarning); out[f'spec_strict_{mt}'] = T[mt].to_numpy() - np.nanmean(Fs[:, :, i], 0)
    out['tail_fraction'] = (1 + (F[:, :, 0] >= T['mean_nlr'].to_numpy()).sum(0)) / (cm['K'] + 1)  # reference-tail, not a p-value
    out['n_strict_false'] = strict.sum(0)
    ds = out.join(info).reset_index()
    S = root / 'summary_title'; S.mkdir(exist_ok=True); (root / 'figures').mkdir(exist_ok=True)
    ds.to_parquet(S / 'paper_title_contrasts.parquet', index=False)
    rng = np.random.default_rng(3511)
    main = ['spec_mean_nlr', 'spec_author_mean_nlr', 'spec_mean_nlr_surname_first', 'total_mean_nlr', 'topic_mean_nlr', 'spec_strict_mean_nlr', 'tail_fraction']
    R = {}
    R['A_group_layer'] = group_means(ds, ['group_tight'], main, rng, sums=[])
    R['A_group_bin_layer'] = group_means(ds, ['group_tight', 'citation_bin'], main, rng, ci=False, sums=[])
    ds['all'] = 'all'
    roles = [f'spec_{x}' for x in TITLE_BASE if x.startswith('mean_nlr_')]
    R['negative_control_by_role'] = group_means(ds, ['all'], roles, rng, sums=[])  # punct / surname_cont should sit near 0
    R['B_spec_target_vs_control_within_bin'] = stratified_diff(ds, 'group_tight', 'target', 'control', 'citation_bin', main[:3] + ['spec_strict_mean_nlr'], rng)
    R['B_sens_drop_low_bins'] = stratified_diff(ds[~ds.citation_bin.isin(LOW_BINS)], 'group_tight', 'target', 'control', 'citation_bin', main[:3], rng)
    R['C_graded_mc_team_a'] = graded(ds, main[:3])
    R['D_ladder_high_citation'] = group_means(ds[ds.bin_lo >= HIGH_FROM], ['group_tight'], main, rng, sums=[])
    R['E_citation_within_group'] = citation_effect(ds, main[:3])
    for k, v in R.items(): v.to_csv(S / f'{k}.csv', index=False)
    title_figures(root, R)
    print('TITLE ANALYZED', len(ds), 'rows ->', S)


def title_figures(root, R):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    tab = R['A_group_layer']; groups = [g for g in ['guard', 'target', 'control', 'excluded'] if g in set(tab.group_tight)]
    for mt in ['spec_mean_nlr', 'spec_mean_nlr_surname_first', 'total_mean_nlr', 'topic_mean_nlr']:
        fig, axes = plt.subplots(1, len(groups), figsize=(4.2 * len(groups), 3.6), sharey=True, squeeze=False)
        for ax, g in zip(axes[0], groups):
            for r, sub in tab[(tab.group_tight == g) & (tab.readout != 'final')].groupby('readout'):
                sub = sub.sort_values('layer'); ax.plot(sub.layer, sub[f'{mt}_mean'], marker='o', label=r)
                ax.fill_between(sub.layer, sub[f'{mt}_lo'], sub[f'{mt}_hi'], alpha=.15)
            fin = tab[(tab.group_tight == g) & (tab.readout == 'final')]
            if len(fin): ax.axhline(fin[f'{mt}_mean'].iloc[0], color='k', ls='--', lw=1, label='final L63')
            ax.axhline(0, color='grey', lw=.8); ax.set(title=g, xlabel='layer'); ax.grid(alpha=.2)
        axes[0][0].set_ylabel(mt); axes[0][-1].legend(fontsize=7)
        fig.tight_layout(); fig.savefig(root / f'figures/title_{mt}_by_group.png', dpi=150); plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['freeze', 'freeze-conditions', 'remaining', 'audit', 'register-lens', 'parity', 'run', 'crosscheck', 'analyze', 'analyze-title'])
    p.add_argument('--root', default=str(ROOT)); p.add_argument('--labels', default=str(LABELS))
    p.add_argument('--readouts', default='jlens_public,jlens_self100,jlens_fitA,logit,final')
    p.add_argument('--layers', default=','.join(map(str, DEFAULT_LAYERS)))
    p.add_argument('--shards', default=None, help='e.g. 0-17,30')
    p.add_argument('--condition', default='true', help='run/remaining: comma list of true | false_0..false_4 | delete')
    p.add_argument('--max-minutes', type=float, default=None)
    p.add_argument('--n', type=int, default=12, help='parity: number of sampled contexts')
    p.add_argument('--tol', type=float, default=0.25, help='parity: max abs logit difference allowed')
    p.add_argument('--skip-parity-gate', action='store_true')
    p.add_argument('--allow-partial', action='store_true')
    p.add_argument('--quick', action='store_true', help='audit: skip lens sha256')
    p.add_argument('--compact', action='store_true', help='audit: one progress line per condition')
    p.add_argument('--name'); p.add_argument('--path')
    a = p.parse_args()
    {'freeze': freeze, 'freeze-conditions': freeze_conditions, 'remaining': remaining, 'analyze-title': analyze_title, 'audit': audit, 'register-lens': register_lens, 'parity': parity, 'run': run,
     'crosscheck': crosscheck, 'analyze': analyze}[a.command](a)


if __name__ == '__main__':
    main()
