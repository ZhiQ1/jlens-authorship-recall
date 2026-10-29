"""X3 paraphrase meaning check (user request 2026-10-29, item 2a/2d). CPU.
For every para_gen paraphrase: NLI cross-encoder (cross-encoder/nli-deberta-v3-large) in both directions,
original -> paraphrase and paraphrase -> original; p_entail in each direction. Also the corrected word Jaccard
(jaccard2: lowercase, punctuation -> space, sklearn English stop words removed, tokens of ANY length kept, light
suffix stemming so 'symmetric'/'symmetrical' match) next to the original one (words > 3 characters, no stemming).
Output: 381_stage13/summary_x3/para_nli.csv (no filtering decision here; the rule goes into addendum 5)."""
import glob, re
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); OUT = ROOT / 'summary_x3'; OUT.mkdir(parents=True, exist_ok=True)
MODEL = 'cross-encoder/nli-deberta-v3-large'


def stem(w):
    for suf in ('ically', 'ation', 'ities', 'ness', 'ment', 'ical', 'ally', 'ing', 'ity', 'ies', 'ive', 'al', 'ed', 'es', 'ic', 'ly', 's'):
        if len(w) > len(suf) + 2 and w.endswith(suf): return w[:-len(suf)]
    return w


def words2(s):
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    return {stem(x) for x in re.sub(r'[^a-z0-9]+', ' ', str(s).lower()).split() if x not in ENGLISH_STOP_WORDS}


def jac(a, b): return len(a & b) / max(1, len(a | b))


def main():
    zs = [np.load(f) for f in sorted(glob.glob(str(ROOT / 'raw/para_gen/shard_*.npz')))]
    d = pd.DataFrame({k: np.concatenate([z[k] for z in zs]) for k in ['paper_id', 'title', 'paraphrase', 'auto_ok', 'word_jaccard']})
    norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower()); d['identical'] = d.title.map(norm) == d.paraphrase.map(norm)
    d['jaccard2'] = [jac(words2(a), words2(b)) for a, b in zip(d.title, d.paraphrase)]
    import torch, transformers
    tok = transformers.AutoTokenizer.from_pretrained(MODEL); m = transformers.AutoModelForSequenceClassification.from_pretrained(MODEL).eval()
    lab = {v.lower(): k for k, v in m.config.id2label.items()}; ie = lab['entailment']; ic = lab['contradiction']
    def nli(prem, hyp):
        out = []
        with torch.inference_mode():
            for i in range(0, len(prem), 16):
                e = tok(list(prem[i:i + 16]), list(hyp[i:i + 16]), padding=True, truncation=True, max_length=256, return_tensors='pt')
                out.append(torch.softmax(m(**e).logits.float(), -1).numpy())
        return np.concatenate(out)
    f = nli(d.title.tolist(), d.paraphrase.tolist()); b = nli(d.paraphrase.tolist(), d.title.tolist())
    d['p_entail_fwd'], d['p_contra_fwd'] = f[:, ie], f[:, ic]; d['p_entail_bwd'], d['p_contra_bwd'] = b[:, ie], b[:, ic]
    d['nli_both'] = (f.argmax(1) == ie) & (b.argmax(1) == ie)
    d.to_csv(OUT / 'para_nli.csv', index=False)
    print(d[['auto_ok', 'identical', 'nli_both']].value_counts().to_string())
    s = pd.read_csv(ROOT / 'logs/para_review_sample20.csv')
    t = s[['paper_id']].merge(d, on='paper_id')
    for i, r in enumerate(t.itertuples(), 1):
        print(f'{i:2d}. fwd {r.p_entail_fwd:.2f} bwd {r.p_entail_bwd:.2f} both={r.nli_both} | J {r.word_jaccard:.2f} -> J2 {r.jaccard2:.2f} | {r.title[:70]} => {r.paraphrase[:70]}')
    print('NLI DONE')


if __name__ == '__main__':
    main()
