"""Item 2-11b (DRAFT addendum 15, NOT locked): model-generated names, labels from names generated IN THIS RUN.

Plan draft: 381_stage13/config/prereg_addendum15_DRAFT.json (unlocked; this script refuses the real `gpu` command until a locked
prereg_addendum15.json + .sha256 exists). New file; v1/v2 scripts are not edited, only imported by path:
  v1 stage13_b2_gennames.py : words / same / match_gen (= Stage 10 stage10_extra_r0r1 matcher, verbatim), chat_prompt, fit_oof
  v2 stage13_b2_gennames_v2.py : pair_stats / within_auroc (within-paper AUROC + author-team cluster bootstrap)

Pipeline per paper: chat prompt -> HF generate (greedy, max_new_tokens 96, batch 1, KV cache, output_hidden_states=True,
output_logits=True) -> parse (rule P1-P7 below) -> label with match_gen (M / H; U = not analysed) -> residuals taken from the
hidden states RETURNED BY THAT SAME generate call (no second forward) -> probe (CPU) -> report.

Hidden-state indexing (HF generate): step 0 returns the prompt states [1, P, d]; step t >= 1 returns the state of generated token
t-1 (absolute position P+t-1). hidden_states[l + 1] = output of decoder block l (checked against jlens ActivationRecorder in tiny).
Positions per kept name: pred_first = position before the first name token (its output predicts the first name token);
name tokens = all token positions of the name (primary feature = mean over them); last = last name token (descriptive).

HARD self-consistency check (H2): at every analysed position p (pred_first and every name-token position), the logits recomputed
from the stored final-layer state at p (final norm + lm_head) must have argmax == the token generated at p+1. This checks that the
stored vectors are the ones that produced the generated text and that the position bookkeeping is right. Agreement < 0.99 -> stop.

Commands: examples --root | parity --root | tiny --root | gpu --shard K (refused until the addendum is locked)
"""
import argparse, hashlib, importlib.util, json, os, re, resource, sys, time, traceback
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R13 = BASE / '381_stage13'
LAB = BASE / 'labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15'
PLAN_LOCKED = R13 / 'config/prereg_addendum15.json'


def load_mod(p, n):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


V1 = load_mod(H / '13_stage13/stage13_b2_gennames.py', 'gn_v1')
V2 = load_mod(H / '13_stage13/stage13_b2_gennames_v2.py', 'gn_v2')
words, same, match_gen = V1.words, V1.same, V1.match_gen
LAYERS = [16, 24, 32, 40, 48, 52, 56]; POS = ['name_mean', 'pred_first', 'last']   # name_mean = primary (ii); pred_first = secondary (i)
MAX_NEW = 96; H2_MIN = 0.99; MAX_WORDS = 7; NB = 2000
EOS_IDS = [151645, 151643]                                                     # <|im_end|>, <|endoftext|> (Qwen3 chat)
ETAL = re.compile(r'(?:\s*,?\s*(?:et\.?\s*al\.?|and others|and colleagues))\s*$', re.I)
TRAIL = ' \t\n.,:'


def now(): return time.strftime('%Y-%m-%dT%H:%M:%S')
def log(*x): print(now(), *x, flush=True)


# ------------------------------------------------------------------ parser (rule P1-P7)
def parse_items(text, eos):
    """P1 split on ';'. P2 strip whitespace and trailing '.', ',', ':'. P3 strip a trailing 'et al.' / 'and others' / 'and colleagues'
    (flag etal). P4 < 2 words (words() of the matcher) -> U_short (includes empty, non-Latin script). P5 > MAX_WORDS words -> U_prose
    (sentences, refusals). P6 same words() key as an earlier kept name -> U_dup. P7 last item when generation hit max_new_tokens
    without EOS -> U_trunc. Kept items: status 'ok'. Returns list of dict(name, start, end, status, etal)."""
    out, at, keys = [], 0, set(); segs = text.split(';')
    for si, seg in enumerate(segs):
        s, e = at, at + len(seg); at = e + 1
        raw = text[s:e]; a = s + (len(raw) - len(raw.lstrip())); b = e
        while b > a and text[b - 1] in TRAIL: b -= 1
        etal = False; m = ETAL.search(text[a:b])
        if m and m.start() > 0:
            etal = True; b = a + m.start()
            while b > a and text[b - 1] in TRAIL: b -= 1
        elif m and m.start() == 0: b = a                                    # item is only 'et al.'
        name = text[a:b]; w = words(name)
        if not name.strip() and si == len(segs) - 1: continue               # trailing ';'
        st = 'ok'
        if len(w) < 2: st = 'U_short'
        elif len(w) > MAX_WORDS: st = 'U_prose'
        elif ' '.join(w) in keys: st = 'U_dup'
        if not eos and si == len(segs) - 1: st = 'U_trunc'
        if st == 'ok': keys.add(' '.join(w))
        out.append(dict(name=name, start=a, end=b, status=st, etal=etal))
    return out


def label_items(true, items):
    """match_gen on the kept names only (order kept) -> 'M' / 'H'; other items keep their U_* status."""
    ok = [i for i, it in enumerate(items) if it['status'] == 'ok']
    lab, nhit = match_gen(true, [items[i]['name'] for i in ok])
    res = [it['status'] for it in items]
    for i, l in zip(ok, lab): res[i] = 'M' if l else 'H'
    return res, nhit


# ------------------------------------------------------------------ author pool (descriptive split of H)
class Pool:
    """Cohort author pool (all 9,108 papers). An H name is 'in pool (rule)' if it would match, under the SAME matcher rule (surname +
    first initial, either order), some author of ANOTHER cohort paper; 'in pool (exact)' if its full normalised word string equals
    that of an author of another paper (either order for 2-word names)."""
    def __init__(self, P):
        self.rule, self.single, self.full = {}, {}, {}
        for pid, al in zip(P.paper_id, P.authors):
            for a in str(al).split('; '):
                w = words(a)
                if not w: continue
                ti = w[0][0] if len(w) > 1 else ''
                (self.rule.setdefault((w[-1], ti), set()) if ti else self.single.setdefault(w[-1], set())).add(pid)
                self.full.setdefault(' '.join(w), set()).add(pid)

    def _other(self, s, pid): return bool(s) and bool(s - {pid})

    def in_rule(self, name, pid):
        g = words(name)
        if len(g) < 2: return False
        for gs, gi in ((g[-1], g[0][0]), (g[0], g[1][0])):
            if self._other(self.rule.get((gs, gi), set()), pid) or self._other(self.single.get(gs, set()), pid): return True
        return False

    def in_exact(self, name, pid):   # PRIMARY definition of 'real but mismatched' (descriptive split)
        g = words(name)
        return self._other(self.full.get(' '.join(g), set()), pid) or (len(g) == 2 and self._other(self.full.get(' '.join(g[::-1]), set()), pid))


# ------------------------------------------------------------------ data
def load_papers(limit_ids=None):
    import pandas as pd
    c13 = load_mod(H / '13_stage13/stage13_cpu.py', 'c13')
    P = pd.read_parquet(R10 / 'cohort/papers.parquet'); folds, teams = c13.group_folds(P.paper_id.to_numpy()); P['fold'] = folds; P['team'] = teams
    d = P[P.group_tight.isin(['target', 'control'])].reset_index(drop=True)
    if limit_ids is not None: d = d.set_index('paper_id').loc[limit_ids].reset_index()
    return P, d


def token_char_ends(tok, ids):
    ends, m = [], 0
    for k in range(len(ids)):
        m = max(m, len(tok.decode(ids[:k + 1], skip_special_tokens=True))); ends.append(m)
    return ends


# ------------------------------------------------------------------ generation with stored residuals
class Force:
    """LogitsProcessor used ONLY by the tiny replay test: forces a given continuation so that real names flow through the pipeline
    with a random tiny model. Not used by the real run (greedy)."""
    def __init__(self, ids, plen): self.ids, self.plen = ids, plen
    def __call__(self, input_ids, scores):
        import torch
        t = input_ids.shape[1] - self.plen; s = torch.full_like(scores, -1e9)
        s[:, self.ids[min(t, len(self.ids) - 1)]] = 0; return s


def gen_one(hf, tok, torch, prompt_ids, layers, final_fn, force=None, max_new=MAX_NEW):
    """one paper: greedy generate with hidden states + raw logits. Returns gen ids, eos flag, a position->state accessor, timings."""
    t0 = time.perf_counter(); inp = torch.tensor([prompt_ids], device=hf.device)
    kw = dict(do_sample=False, temperature=None, top_p=None, top_k=None, max_new_tokens=max_new if force is None else len(force),
              output_hidden_states=True, output_logits=True, return_dict_in_generate=True, eos_token_id=EOS_IDS, pad_token_id=EOS_IDS[1])
    if force is not None:
        from transformers import LogitsProcessorList
        kw['logits_processor'] = LogitsProcessorList([Force(force, len(prompt_ids))])
    with torch.inference_mode(): out = hf.generate(inp, **kw)
    if hf.device.type == 'cuda': torch.cuda.synchronize()
    t_gen = time.perf_counter() - t0
    seq = out.sequences[0].tolist(); gen = seq[len(prompt_ids):]
    eos = bool(gen) and gen[-1] in EOS_IDS
    hs = out.hidden_states; P = len(prompt_ids)
    hs_bytes = sum(t.numel() * t.element_size() for step in hs for t in step)
    def state(layer_idx, p):                        # layer_idx into hidden_states tuple (0 = embeddings, l+1 = block l, -1 = final)
        return hs[0][layer_idx][0, p] if p < P else hs[p - P + 1][layer_idx][0, 0]
    return dict(seq=seq, gen=gen, eos=eos, state=state, logits=out.logits, P=P, t_gen=t_gen, hs_bytes=hs_bytes, n_steps=len(hs))


def process_paper(r, tok, torch, hf, final_fn, layers, pool, force=None):
    """generate -> parse -> label -> residuals (+ H2 check rows). Returns (name rows, vectors {pos@l: [n, d]}, paper row, h2 list)."""
    pr = V1.chat_prompt(tok, r.title, r.year); pids = tok(pr, add_special_tokens=False).input_ids
    g = gen_one(hf, tok, torch, pids, layers, final_fn, force=force)
    t1 = time.perf_counter()
    gen = g['gen']; body = gen[:-1] if g['eos'] else gen
    text = tok.decode(body, skip_special_tokens=True); ends = token_char_ends(tok, body); starts = [0] + ends[:-1]
    items = parse_items(text, g['eos']); true = str(r.authors).split('; ')
    labs, nhit = label_items(true, items)
    rows, vec, h2 = [], {f'{p}@{l}': [] for p in POS for l in layers}, []
    for j, (it, lab) in enumerate(zip(items, labs)):
        rec = dict(paper_id=r.paper_id, item_index=j, name=it['name'], status=lab, etal=it['etal'], group_tight=r.group_tight, team=int(r.team), fold=int(r.fold))
        if lab not in ('M', 'H'): rows.append(rec); continue
        ti = [k for k in range(len(body)) if starts[k] < it['end'] and ends[k] > it['start']]
        if not ti: rec['status'] = 'U_tokmap'; rows.append(rec); continue
        absn = [g['P'] + k for k in ti]; pf = absn[0] - 1
        span_txt = tok.decode([body[k] for k in ti], skip_special_tokens=True)
        w = words(it['name'])
        rec.update(tok_first=absn[0], tok_last=absn[-1], n_name_tokens=len(absn), span_ok=it['name'] in span_txt,
                   in_pool_rule=bool(pool.in_rule(it['name'], r.paper_id)) if lab == 'H' else None,
                   in_pool_exact=bool(pool.in_exact(it['name'], r.paper_id)) if lab == 'H' else None,
                   name_len_chars=len(it['name']), name_n_words=len(w), fullname_freq_cohort=len(pool.full.get(' '.join(w), ())))
        rows.append(rec)
        for p in [pf] + absn:                                           # H2: stored final state at p reproduces token p+1
            nxt = g['seq'][p + 1]
            fin = int(final_fn(g['state'](-1, p)[None, None]).argmax().item())   # same [1, 1, d] shape as the decode step
            stp = int(g['logits'][p - g['P'] + 1][0].argmax().item())  # raw logits of the step that consumed position p
            h2.append(dict(paper_id=r.paper_id, pos=p, next_tok=nxt, final_argmax=fin, step_logit_argmax=stp))
        for l in layers:
            hl = l + 1
            vec[f'pred_first@{l}'].append(g['state'](hl, pf).float().cpu().numpy())
            vec[f'last@{l}'].append(g['state'](hl, absn[-1]).float().cpu().numpy())
            vec[f'name_mean@{l}'].append(torch.stack([g['state'](hl, p) for p in absn]).float().mean(0).cpu().numpy())
    t_post = time.perf_counter() - t1
    prow = dict(paper_id=r.paper_id, group_tight=r.group_tight, n_prompt=g['P'], n_gen=len(gen), eos=g['eos'], text=text, gen_ids=json.dumps(gen),
                n_items=len(items), n_M=labs.count('M'), n_H=labs.count('H'), n_U=sum(x.startswith('U') for x in labs), n_true=len(true), n_true_hit=nhit,
                t_gen=g['t_gen'], t_post=t_post, hs_bytes=g['hs_bytes'])
    return rows, vec, prow, h2, g


def h2_status(h2):
    if not h2: return 'NO_POSITIONS', float('nan')
    a = float(np.mean([x['final_argmax'] == x['next_tok'] for x in h2])); return ('PASS' if a >= H2_MIN else 'FAIL'), a


# ------------------------------------------------------------------ probe (CPU)
def probe(N, X, layers, nb=NB):
    """N: kept names (M/H) aligned with X[pos@l]. Within-paper AUROC (target papers with >= 1 M and >= 1 H), team bootstrap,
    position + string baselines (as D12-3); shuffled-label control; descriptive M vs H-in-pool / H-not-in-pool."""
    import pandas as pd
    y = (N.status == 'M').to_numpy(int); fold = N.fold.to_numpy(); paper = N.paper_id.to_numpy(); PT = dict(zip(N.paper_id, N.team))
    XP = N[['item_index', 'item_rel']].to_numpy(float); XS = np.stack([N.name_len_chars.to_numpy(float), np.log1p(N.fullname_freq_cohort.to_numpy(float))], 1)
    pp_, _, _ = V1.fit_oof(XP, y, fold); ps_, _, _ = V1.fit_oof(XS, y, fold)
    tgt = (N.group_tight == 'target').to_numpy(); inpool = N.in_pool_exact.astype('boolean').fillna(False).to_numpy(bool)   # primary split definition = exact
    rows = []
    for l in layers:
        for pos in POS:
            pr, C, _ = V1.fit_oof(X[f'{pos}@{l}'], y, fold); psh, _, ysh = V1.fit_oof(X[f'{pos}@{l}'], y, fold, seed_shuffle=1212)
            role = 'primary' if pos == 'name_mean' else ('secondary' if pos == 'pred_first' else 'descriptive')
            st = [V2.pair_stats(paper[tgt], y[tgt], sc[tgt]) for sc in (pr, pp_, ps_)]
            common = set(st[0]) & set(st[1]) & set(st[2]); st = [{p: s[p] for p in common} for s in st]
            ssh = V2.pair_stats(paper[tgt], ysh[tgt], psh[tgt]); shv = sum(v[0] for v in ssh.values()) / max(1, sum(v[1] for v in ssh.values())) if ssh else np.nan
            sub = {}
            for nm, keep in (('H_in_pool', (y == 1) | inpool), ('H_not_in_pool', (y == 1) | ~inpool)):
                m_ = tgt & keep; s_ = V2.pair_stats(paper[m_], y[m_], pr[m_]); sub[nm] = sum(v[0] for v in s_.values()) / max(1, sum(v[1] for v in s_.values())) if s_ else np.nan
            row = dict(layer=l, position=pos, role=role, C=C, n_M=int(y[tgt].sum()), n_H=int((1 - y[tgt]).sum()), shuffled_within=shv,
                       within_M_vs_H_in_pool=sub['H_in_pool'], within_M_vs_H_not_in_pool=sub['H_not_in_pool'])
            if common and not any(np.isnan(sc[tgt]).any() for sc in (pr, pp_, ps_)):
                est, bt, npap, npair = V2.within_auroc(st, PT, nb=nb); ci = lambda v: np.percentile(v, [2.5, 97.5])
                (a1, b1), (a2, b2), (lo, hi) = ci(bt[:, 0] - bt[:, 1]), ci(bt[:, 0] - bt[:, 2]), ci(bt[:, 0])
                row.update(auroc_within=est[0], lo=lo, hi=hi, position_baseline=est[1], string_baseline=est[2], diff_pos_lo=a1, diff_str_lo=a2,
                           n_papers=npap, n_pairs=npair, signal=bool(a1 > 0 and a2 > 0))
            else: row.update(auroc_within=np.nan, n_papers=0, n_pairs=0, signal=False)
            rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ matcher examples (computed by the code above)
EXAMPLES = [  # (topic, true author list, generated text)
    ('case', ['John Smith'], 'JOHN SMITH'),
    ('diacritics stripped', ['José Muñoz'], 'Jose Munoz'),
    ('diacritics transliterated', ['Jürgen Müller'], 'Juergen Mueller'),
    ('eszett', ['Hans Strauß'], 'Hans Strauss'),
    ('initial vs full given name', ['John R. Smith'], 'J. Smith'),
    ('full given vs initial in truth', ['J. Smith'], 'James Smith'),
    ('wrong initial', ['John Smith'], 'K. Smith'),
    ('nickname', ['Robert Jones'], 'Bob Jones'),
    ('hyphenated surname, first part only', ['María García-López'], 'María García'),
    ('hyphenated surname, second part only', ['María García-López'], 'Maria Lopez'),
    ('hyphenated given name as initials', ['Jean-Pierre Dupont'], 'J.-P. Dupont'),
    ('particle dropped', ['Hans van der Berg'], 'Hans Berg'),
    ('particle fused', ['Hans van der Berg'], 'Hans Vanderberg'),
    ('apostrophe surname', ["Seán O'Brien"], 'Sean OBrien'),
    ('suffix Jr. in truth', ['Martin Luther King Jr.'], 'Martin Luther King'),
    ('et al. truncation', ['John Smith', 'Jane Doe'], 'John Smith et al.'),
    ('surname-first order', ['Shimon Sakaguchi'], 'Sakaguchi Shimon'),
    ('surname, initial with comma', ['Shimon Sakaguchi'], 'Sakaguchi, S.'),
    ('two names in one item (comma)', ['Jane Doe', 'Bob Brown'], 'John Smith, Jane Doe'),
    ('one-to-one: second variant of same author', ['John Smith'], 'John Smith; J. Smith'),
]


def examples(root):
    import pandas as pd
    rows = []
    for k, (topic, true, text) in enumerate(EXAMPLES, 1):
        items = parse_items(text, eos=True); labs, _ = label_items(true, items)
        for it, lab in zip(items, labs):
            rows.append(dict(ex=k, topic=topic, true_authors='; '.join(true), generated=text, parsed_item=it['name'], etal_stripped=it['etal'],
                             words_gen=' '.join(words(it['name'])), decision=lab))
    D = pd.DataFrame(rows); root.mkdir(parents=True, exist_ok=True); D.to_csv(root / 'matcher_examples.csv', index=False)
    L = ['| # | topic | true author(s) | generated | parsed item | normalised words | decision |', '|---|---|---|---|---|---|---|']
    for r in D.itertuples():
        L.append(f'| {r.ex} | {r.topic} | {r.true_authors} | {r.generated} | {r.parsed_item}{" (et al. stripped)" if r.etal_stripped else ""} | {r.words_gen} | **{r.decision}** |')
    (root / 'matcher_examples.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L), flush=True)
    return D


# ------------------------------------------------------------------ H3 parity on stored text (CPU)
def parity(root, d):
    import pandas as pd
    o = pd.read_json(LAB / 'open_results.jsonl', lines=True)[['paper_id', 'generated_text', 'finish_reason', 'names', 'm', 'h', 'u']]
    x = d.merge(o, on='paper_id', suffixes=('', '_pkg')); eq = 0; pa = []
    quirks = dict(true_authors=0, true_suffix_jr_sr_roman=0, kept_items=0, kept_items_with_comma_and_4plus_words=0, kept_items_et_al_stripped=0)
    for r in x.itertuples():
        names = list(r.names); true = str(r.authors).split('; '); lab, nhit = match_gen(true, names)
        mr = int(sum(lab)); eq += (mr, len(names) - mr, len(true) - nhit) == (int(r.m_pkg), int(r.h_pkg), int(r.u_pkg)) and mr == nhit
        it = parse_items(r.generated_text, r.finish_reason == 'stop'); kept = [i['name'] for i in it if i['status'] == 'ok']
        quirks['true_suffix_jr_sr_roman'] += sum(1 for t in true if words(t) and words(t)[-1] in ('jr', 'sr', 'ii', 'iii', 'iv'))
        quirks['kept_items_with_comma_and_4plus_words'] += sum(1 for k in kept if ',' in k and len(words(k)) >= 4)
        quirks['kept_items_et_al_stripped'] += sum(1 for i in it if i['status'] == 'ok' and i['etal'])
        quirks['true_authors'] += len(true); quirks['kept_items'] += len(kept)
        pa.append(dict(paper_id=r.paper_id, same_list=kept == names, n_pkg=len(names), n_kept=len(kept),
                       n_U=dict(pd.Series([i['status'] for i in it if i['status'] != 'ok']).value_counts()) if any(i['status'] != 'ok' for i in it) else {}))
    PA = pd.DataFrame(pa); Us = {}
    for v in PA.n_U:
        for k, c in v.items(): Us[k] = Us.get(k, 0) + int(c)
    res = dict(papers=len(x), H3_counts_equal=int(eq), parser_list_equal_pkg_names=int(PA.same_list.sum()), pkg_names=int(PA.n_pkg.sum()),
               parser_kept=int(PA.n_kept.sum()), parser_U_by_reason=Us, matcher_quirk_counts_stored_text=quirks)
    (root / 'parity.json').write_text(json.dumps(res, indent=1)); log('H3 parity + parser on stored text', res); return res


# ------------------------------------------------------------------ tiny full pipeline
def tiny(root, n_papers=20):
    import torch, transformers, jlens, pandas as pd
    t_all = time.perf_counter(); root.mkdir(parents=True, exist_ok=True); res = dict(created=now(), job=os.environ.get('SLURM_JOB_ID'))
    examples(root)
    s12 = load_mod(H / '12_stage12/371_stage12.py', 's12'); s10 = s12.s10; tok = s10.tokenizer()
    P, d = load_papers(); pool = Pool(P)
    res['parity'] = parity(root, d)
    # pool rule == brute-force matcher on 40 random H-like names
    o = pd.read_json(LAB / 'open_results.jsonl', lines=True)[['paper_id', 'generated_text', 'finish_reason', 'names', 'm', 'h']]
    rng = np.random.default_rng(1511); cand = d.merge(o, on='paper_id', suffixes=('', '_pkg'))
    allauth = [(pid, words(a)) for pid, al in zip(P.paper_id, P.authors) for a in str(al).split('; ') if words(a)]
    bf_ok = 0; sample = cand.iloc[rng.choice(len(cand), 40, replace=False)]
    for r in sample.itertuples():
        nm = r.names[0] if len(r.names) else 'John Smith'; g = words(nm)
        bf = len(g) >= 2 and any(pid != r.paper_id and (same(w, g, False) or same(w, g, True)) for pid, w in allauth)
        bf_ok += bf == pool.in_rule(nm, r.paper_id)
    res['pool_rule_vs_bruteforce'] = f'{bf_ok}/40'
    # 20 target papers with package m >= 1 and h >= 1 (so the replay has both labels)
    sel = cand[(cand.group_tight == 'target') & (cand.m_pkg >= 1) & (cand.h_pkg >= 1) & (cand.finish_reason == 'stop')]
    sel = sel.iloc[np.sort(rng.choice(len(sel), n_papers, replace=False))].reset_index(drop=True)
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 4; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:4]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    lm = jlens.from_hf(hf, tok); final_fn = lambda h: hf.lm_head(h)
    # which convention is hidden_states[-1]? (post final norm or not) -> decided on the first paper, recorded
    layers = [0, 1, 2]; checks = {}
    # ---- free greedy run, twice (H1 reproducibility = WARN only)
    runs = []
    for rep in (0, 1):
        R = []
        for r in sel.itertuples():
            rows, vec, prow, h2, g = process_paper(r, tok, torch, hf, final_fn, layers, pool); R.append((rows, vec, prow, h2, g))
        runs.append(R)
    g0 = runs[0][0][4]
    post = float((final_fn(g0['state'](-1, g0['P'] - 1)) - g0['logits'][0][0]).abs().max())
    pre = float((lm.unembed(g0['state'](-1, g0['P'] - 1)) - g0['logits'][0][0]).abs().max())
    res['hidden_states[-1] convention'] = dict(max_abs_diff_lm_head_only=post, max_abs_diff_norm_then_lm_head=pre, adopted='lm_head only (state already normed)' if post < pre else 'norm + lm_head')
    if pre < post: final_fn = lambda h: lm.unembed(h)
    same_tok = [a[2]['gen_ids'] == b[2]['gen_ids'] for a, b in zip(*runs)]
    res['H1_repro_WARN_only'] = dict(identical=int(sum(same_tok)), n=len(same_tok), status='OK' if all(same_tok) else 'WARN')
    free = runs[0]; free_h2 = [x for R in free for x in R[3]]
    st, a = h2_status(free_h2); res['free'] = dict(papers=len(free), names_kept=sum(p[2]['n_M'] + p[2]['n_H'] for p in free), H2_status=st, H2_agreement=a, H2_positions=len(free_h2),
                                                 mean_gen_tokens=float(np.mean([p[2]['n_gen'] for p in free])), eos_share=float(np.mean([p[2]['eos'] for p in free])))
    # H2 on ALL generated positions of the free run (random tiny model emits few parseable names): stored final state -> argmax == next token
    allpos = []
    for R in free:
        g = R[4]
        for p in range(g['P'] - 1, len(g['seq']) - 1): allpos.append(int(final_fn(g['state'](-1, p)[None, None]).argmax().item()) == g['seq'][p + 1])
    res['free']['H2_all_generated_positions'] = dict(agreement=float(np.mean(allpos)), n=len(allpos))
    checks['H2 free greedy (all generated positions) >= 0.99'] = np.mean(allpos) >= H2_MIN
    # ---- replay: stored package text forced through the SAME generate path (real names -> labels -> residuals -> probe)
    names, vecs, prows, h2r, tfr = [], {f'{p}@{l}': [] for p in POS for l in layers}, [], [], []
    for r in sel.itertuples():
        pr = V1.chat_prompt(tok, r.title, r.year); full = tok(pr + r.generated_text, add_special_tokens=False).input_ids
        pids = tok(pr, add_special_tokens=False).input_ids
        cont = full[len(pids):] if full[:len(pids)] == pids else tok(r.generated_text, add_special_tokens=False).input_ids
        force = cont + [EOS_IDS[0]]
        rows, vec, prow, h2, g = process_paper(r, tok, torch, hf, final_fn, layers, pool, force=force)
        names += rows; prows.append(prow); h2r += h2
        for k in vecs: vecs[k] += vec[k]
        # teacher-forced comparison (the alternative method): one forward over prompt + generated tokens, jlens recorder
        from jlens.hooks import ActivationRecorder
        kept = [x for x in rows if x['status'] in ('M', 'H')]
        with torch.inference_mode(), ActivationRecorder(lm.layers, at=layers) as rec:
            o_ = lm.forward(torch.tensor([g['seq'][:-1]])); fin = o_.last_hidden_state[0]
            for x in kept:
                for p in [x['tok_first'] - 1] + list(range(x['tok_first'], x['tok_last'] + 1)):
                    tfr.append(dict(diff=max(float((rec.activations[l][0, p] - g['state'](l + 1, p)).abs().max()) for l in layers),
                                    tf_argmax_eq_next=int(hf.lm_head(fin[p]).argmax().item()) == g['seq'][p + 1],
                                    tf_argmax_eq_gen_step=int(hf.lm_head(fin[p]).argmax().item()) == int(g['logits'][p - g['P'] + 1][0].argmax().item())))
    N = pd.DataFrame(names); N.to_parquet(root / 'names_replay.parquet', index=False); pd.DataFrame(prows).to_csv(root / 'papers_replay.csv', index=False)
    K = N[N.status.isin(['M', 'H'])].reset_index(drop=True)
    K['item_rel'] = K.item_index / K.groupby('paper_id').item_index.transform('max').clip(lower=1)
    X = {k: np.stack(v).astype(np.float32) for k, v in vecs.items()}
    np.savez(root / 'resid_replay.npz', key=(K.paper_id + '|' + K.item_index.astype(str)).to_numpy(), **X)
    idx_ok = float(np.mean([x['final_argmax'] == x['step_logit_argmax'] for x in h2r])) if h2r else float('nan')
    res['replay'] = dict(papers=len(prows), items=len(N), status_counts=N.status.value_counts().to_dict(), span_ok=f'{int(K.span_ok.sum())}/{len(K)}',
                         H_in_pool_rule=int(K.in_pool_rule.astype('boolean').fillna(False).sum()), H_in_pool_exact=int(K.in_pool_exact.astype('boolean').fillna(False).sum()),
                         index_check_final_state_vs_step_logits=idx_ok,
                         H2_vs_forced_token_expected_low=h2_status(h2r)[1],
                         teacher_forced_vs_generate=dict(n_positions=len(tfr), max_abs_resid_diff=max(t['diff'] for t in tfr) if tfr else None,
                                                         tf_argmax_eq_generate_step_argmax=float(np.mean([t['tf_argmax_eq_gen_step'] for t in tfr])) if tfr else None))
    checks['replay: names kept, both labels'] = set(K.status) == {'M', 'H'}
    checks['replay: token spans contain the names'] = bool(K.span_ok.all())
    checks['replay: stored final state reproduces the step logits (indexing) = 1.0'] = idx_ok == 1.0
    checks['hidden_states[l+1] == jlens block-l output (teacher-forced, fp32) < 1e-4'] = bool(tfr) and max(t['diff'] for t in tfr) < 1e-4
    T = probe(K, X, layers, nb=50); T.to_csv(root / 'probe_within_tiny.csv', index=False); checks['probe table'] = len(T) == len(layers) * len(POS)
    # ---- cost
    fr = [p[2] for p in free]; rp = prows
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    res['cost_tiny'] = dict(model=dict(layers=4, hidden=64, dtype='float32', device='cpu', threads=torch.get_num_threads()),
                            free_s_per_paper_gen=float(np.mean([p['t_gen'] for p in fr])), free_s_per_paper_post=float(np.mean([p['t_post'] for p in fr])),
                            free_ms_per_generated_token=1000 * float(np.sum([p['t_gen'] for p in fr]) / np.sum([p['n_gen'] for p in fr])),
                            replay_s_per_paper_gen=float(np.mean([p['t_gen'] for p in rp])), replay_s_per_paper_post=float(np.mean([p['t_post'] for p in rp])),
                            replay_mean_gen_tokens=float(np.mean([p['n_gen'] for p in rp])), replay_mean_prompt_tokens=float(np.mean([p['n_prompt'] for p in rp])),
                            hidden_states_bytes_per_paper_mean=float(np.mean([p['hs_bytes'] for p in rp])), hidden_states_bytes_per_paper_max=float(np.max([p['hs_bytes'] for p in rp])),
                            peak_rss_MB=rss, wall_total_s=time.perf_counter() - t_all)
    sc = (65 / 5) * (5120 / 64) * (2 / 4)                       # (n_layers+1) ratio x hidden ratio x bf16/fp32
    res['cost_tiny']['hidden_states_bytes_per_paper_scaled_to_32B_max_MB'] = res['cost_tiny']['hidden_states_bytes_per_paper_max'] * sc / 2**20
    for k, v in checks.items(): print('TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    res['checks'] = {k: bool(v) for k, v in checks.items()}; res['tiny_status'] = 'PASS' if all(checks.values()) else 'FAIL'
    (root / 'tiny_result.json').write_text(json.dumps(res, indent=1, default=str)); print(json.dumps(res, indent=1, default=str), flush=True)
    report(root, res, T); return all(checks.values())


def report(root, res, T):
    try:
        L = ['# 2-11b tiny full-pipeline run (random 4-layer Qwen3-shaped model, CPU) - plumbing and cost only, values not meaningful', '',
             f'Job {res.get("job")}. Draft plan `config/prereg_addendum15_DRAFT.json` (unlocked).', '',
             '## Checks', ''] + [f'- {"PASS" if v else "FAIL"} {k}' for k, v in res['checks'].items()] + ['',
             '## Results (JSON)', '', '```', json.dumps({k: v for k, v in res.items() if k != 'checks'}, indent=1, default=str), '```', '',
             '## Probe table (tiny, nb = 50; numbers meaningless)', '', T.round(3).to_csv(sep='|', index=False), '', '## Matcher examples', '', (root / 'matcher_examples.md').read_text()]
        (root / 'tiny_report.md').write_text('\n'.join(L) + '\n'); print('wrote', root / 'tiny_report.md', flush=True)
    except Exception:
        print('WARN report writing failed', flush=True); traceback.print_exc()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['examples', 'parity', 'tiny', 'gpu']); ap.add_argument('--root', required=True)
    ap.add_argument('--shard', type=int); a = ap.parse_args(); root = Path(a.root)
    if a.cmd == 'examples': examples(root); return
    if a.cmd == 'parity': _, d = load_papers(); root.mkdir(parents=True, exist_ok=True); parity(root, d); return
    if a.cmd == 'tiny': sys.exit(0 if tiny(root) else 1)
    if a.cmd == 'gpu':
        if not PLAN_LOCKED.exists() or not (PLAN_LOCKED.parent / 'prereg_addendum15.json.sha256').exists():
            raise SystemExit('addendum 15 is not locked (prereg_addendum15.json + .sha256 missing): real run refused')
        raise SystemExit('real gpu runner is written after locking (new file); this draft script only covers tiny / examples / parity')


if __name__ == '__main__':
    main()
