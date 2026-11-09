"""Addendum 15 lock statistics (stored texts only, matcher v3b): (1) kept name items that contain two names, (2) true author names
ending in 'and', (3) items labelled P only because of that trailing 'and'. Output: --out JSON."""
import argparse, importlib.util, json, re
from pathlib import Path

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('gnb_v3b', H / '13_stage13/stage13_b2_gennames_b_v3b.py'); V3B = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V3B)
V3 = V3B.V3; B = V3.B
V3.patch()


def two_names(item):
    """an item counts as holding two names if it splits on ',', '&' or ' and ' into >= 2 parts that each have >= 2 words."""
    for sep in (r',', r'&', r'\band\b'):
        parts = [p for p in re.split(sep, item) if p.strip()]
        if len(parts) >= 2 and sum(len(V3.words3(p)) >= 2 for p in parts) >= 2: return True
    return False


def main():
    import pandas as pd
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
    _, d = B.load_papers()
    o = pd.read_json(B.LAB / 'open_results.jsonl', lines=True)[['paper_id', 'generated_text', 'finish_reason']]
    x = d.merge(o, on='paper_id'); n_items = n_two = n_true = n_and = n_p = n_p_and = 0; ex_two, ex_and = [], []
    for r in x.itertuples():
        true = str(r.authors).split('; '); n_true += len(true)
        ta = [t for t in true if V3.words3(t)[-1:] == ['and']]; n_and += len(ta)
        if ta and len(ex_and) < 10: ex_and += ta[:1]
        it = B.parse_items(r.generated_text, r.finish_reason == 'stop')
        lab, _ = V3.label_items3(true, it)
        names = [i for i, l in zip(it, lab) if l in ('M', 'H', 'P')]; n_items += len(names)
        tw = [i['name'] for i in names if two_names(i['name'])]; n_two += len(tw)
        if tw and len(ex_two) < 10: ex_two += tw[:1]
        n_p += lab.count('P')
        if ta and 'P' in lab:
            fixed = [re.sub(r'[\s,]+and\s*$', '', t) for t in true]
            lab2, _ = V3.label_items3(fixed, it)
            n_p_and += sum(1 for l1, l2 in zip(lab, lab2) if l1 == 'P' and l2 != 'P')
    res = dict(papers=int(x.paper_id.nunique()), name_items_MHP=n_items, items_with_two_names=n_two, share=n_two / max(1, n_items),
               two_name_rule="item splits on ',', '&' or ' and ' into >= 2 parts with >= 2 words each", examples_two=ex_two,
               true_author_names=n_true, true_names_ending_in_and=n_and, examples_and=ex_and, P_items_total=n_p, P_items_due_to_trailing_and=n_p_and)
    Path(a.out).write_text(json.dumps(res, indent=1, ensure_ascii=False)); print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
