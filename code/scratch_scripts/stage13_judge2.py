"""X3 paraphrase judge, version 2 (user decisions 2026-10-30, U51). GPU (Qwen3-32B) or --tiny (CPU, random 2-layer model).

Prompt v2 states the user's 5 criteria verbatim in spirit: same object, same scope, technical terms kept, numbers / names /
abbreviations kept, direction of relations unchanged; mere rewording or reordering counts as KEEP.
Blind A/B, both orders, score = P(Yes) / (P(Yes) + P(No)) of the first answer token (chat template, thinking off).
Calibration set (set A, logs/para_review_sample20_labels.csv): the threshold on mean P(Yes) over both orders is chosen to
maximise agreement with the human labels (keep vs not keep; borderline counts as not keep).
Test set (set B, logs/para_review_sample20_b_labels.csv, labelled by the user before the judge saw it): agreement at that
threshold, with borderline as not keep (primary) and with borderline items dropped (secondary). The user's rule: below 0.80
the judge is not used. Output: followup/judge2_{tiny,sample}.csv and judge2_summary.json; nothing else is touched.
Usage: python stage13_judge2.py --tiny | --run"""
import importlib.util, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; ROOT = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
TINY = '--tiny' in sys.argv
OUT = ROOT / ('followup_tiny' if TINY else 'followup'); OUT.mkdir(parents=True, exist_ok=True)
JUDGE2 = ('Do these two research paper titles say the same thing?\n'
          'Answer Yes if ALL of these hold:\n'
          '1. the same object of study;\n'
          '2. the same scope (not broader, not narrower);\n'
          '3. no technical term is replaced by a plain word or by a different term;\n'
          '4. every number, name and abbreviation is still there;\n'
          '5. the direction of every relation is unchanged (what affects what, what is compared with what).\n'
          'Different wording or a different word order alone is fine and still counts as Yes. If any condition fails, answer No.\n'
          'Title A: {a}\nTitle B: {b}\nAnswer with Yes or No.')


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def model():
    import torch, transformers
    s10 = load(H / '10_stage10/351_stage10.py', 's10'); tok = s10.tokenizer()
    if TINY:
        cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
        cfg.num_hidden_layers = 2; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
        if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:2]
        torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval(); dev = 'cpu'
    else:
        hf = transformers.AutoModelForCausalLM.from_pretrained(s10.MODEL, revision=s10.REV, dtype=torch.bfloat16, device_map='cuda:0').eval(); dev = 'cuda:0'
    return torch, tok, hf, dev


def judge(torch, tok, hf, dev, items):
    yes = tok.encode('Yes', add_special_tokens=False)[0]; no = tok.encode('No', add_special_tokens=False)[0]; out = []
    for r in items.itertuples():
        ps = []
        for a, b in ((r.title, r.paraphrase), (r.paraphrase, r.title)):
            txt = tok.apply_chat_template([{'role': 'user', 'content': JUDGE2.format(a=a, b=b)}], add_generation_prompt=True, enable_thinking=False, tokenize=False)
            ids = tok(txt, return_tensors='pt', add_special_tokens=False).input_ids.to(dev)
            with torch.inference_mode():
                lg = hf(ids).logits[0, -1].float()
            ps.append(torch.softmax(lg[[yes, no]], 0)[0].item())
        out.append((r.item, ps[0], ps[1]))
    d = pd.DataFrame(out, columns=['item', 'p_yes_title_first', 'p_yes_para_first']); d['p_mean'] = d[['p_yes_title_first', 'p_yes_para_first']].mean(1); return d


def main():
    L = ROOT / 'logs'
    A = pd.read_csv(L / 'para_review_sample20_labels.csv'); A['item'] = 'A' + A['item'].astype(str)
    Bs = pd.read_csv(L / 'para_review_sample20_b_labels.csv')
    items = pd.concat([A[['item', 'title', 'paraphrase', 'human_label']], Bs[['item', 'title', 'paraphrase', 'human_label']]], ignore_index=True)
    if TINY: items = pd.concat([items.head(3), items.tail(3)])
    torch, tok, hf, dev = model(); log('model ready', dev, len(items), 'items')
    J = judge(torch, tok, hf, dev, items).merge(items[['item', 'human_label']], on='item')
    J.to_csv(OUT / f'judge2_{"tiny" if TINY else "sample"}.csv', index=False)
    a = J[J.item.str.startswith('A')]; b = J[J.item.str.startswith('B')]
    keepA = (a.human_label == 'keep').to_numpy()
    cands = np.unique(np.concatenate([[0.0, 1.0], a.p_mean.to_numpy()]))
    accs = [((a.p_mean.to_numpy() > t) == keepA).mean() for t in cands]
    best = float(cands[int(np.argmax(accs))]); tie = [float(t) for t, x in zip(cands, accs) if x == max(accs)]
    thr = float(np.median(tie))                   # middle of the tied best thresholds
    def agree(df, drop_border):
        df = df[df.human_label != 'borderline'] if drop_border else df
        return float(((df.p_mean > thr) == (df.human_label == 'keep')).mean()), len(df)
    sb, nb = agree(b, False); sb2, nb2 = agree(b, True); sa, na = agree(a, False)
    conf = pd.crosstab(b.human_label, np.where(b.p_mean > thr, 'judge keep', 'judge not keep')).to_dict()
    S = dict(threshold=thr, calibration_agreement=sa, n_calibration=na, test_agreement_borderline_as_not_keep=sb, n_test=nb,
             test_agreement_borderline_dropped=sb2, n_test_no_borderline=nb2, test_confusion=conf, rule='use judge only if test agreement >= 0.80',
             verdict=('judge usable' if sb >= 0.80 else 'judge NOT usable -> fallback (manual check + with/without sensitivity)'))
    json.dump(S, open(OUT / f'judge2_summary{"_tiny" if TINY else ""}.json', 'w'), indent=1, ensure_ascii=False)
    log(json.dumps(S, ensure_ascii=False)); log('JUDGE2 DONE')


if __name__ == '__main__':
    main()
