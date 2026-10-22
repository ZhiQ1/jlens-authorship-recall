
import json

import random

from pathlib import Path

from collections import Counter, defaultdict



ROOT = Path("/scratch/zhang.zhiqi2/jlens")

RECOG = ROOT / "recognition_primary_random_field_1000_results.jsonl"

HIDDEN = ROOT / "title_hidden_random_field_772_results.jsonl"

SEED = 42

MAX_PAIRS = 200



def read_jsonl(path):

    with path.open(encoding="utf-8") as f:

        return [json.loads(x) for x in f if x.strip()]



def write_jsonl(path, rows):

    with path.open("w", encoding="utf-8") as f:

        for r in rows:

            f.write(json.dumps(r, ensure_ascii=False) + "\n")



recog = read_jsonl(RECOG)

hidden = read_jsonl(HIDDEN)



assert len(recog) == 1000

assert len(hidden) == 772

assert len({r["paper_id"] for r in recog}) == 1000

assert len({r["paper_id"] for r in hidden}) == 772



recog_by_id = {r["paper_id"]: r for r in recog}

assert all(

    r["paper_id"] in recog_by_id and

    recog_by_id[r["paper_id"]]["recognition_correct"] == 1

    for r in hidden

)



known = [

    r for r in hidden

    if r["recognition_correct"] == 1

    and r["title_hidden_correct"] == 0

    and r["title_hidden_parse_failed"] == 0

]



unknown = [

    r for r in recog

    if r["recognition_correct"] == 0

    and r["parse_failed"] == 0

]



assert len(known) == 384

assert len(unknown) == 228



def key(r):

    return (

        r["field"],

        r["citation_bin"],

        r["correct_label"]

    )



k_groups = defaultdict(list)

u_groups = defaultdict(list)



for r in known:

    k_groups[key(r)].append(r)



for r in unknown:

    u_groups[key(r)].append(r)



rng = random.Random(SEED)

pairs = []



# Exact matching within field, citation bin and label.

for stratum in sorted(k_groups):

    ks = list(k_groups[stratum])

    us = list(u_groups.get(stratum, []))

    rng.shuffle(ks)

    rng.shuffle(us)



    # Pair constrained cases first.

    while ks and us:

        best = None

        for i, k in enumerate(ks):

            for j, u in enumerate(us):

                year_gap = abs(int(k["year"]) - int(u["year"]))

                author_gap = abs(

                    int(k["n_gt_authors"]) -

                    int(u["n_gt_authors"])

                )

                cost = year_gap + 5 * author_gap

                if best is None or cost < best[0]:

                    best = (cost, i, j, year_gap, author_gap)



        cost, i, j, yg, ag = best

        k = ks.pop(i)

        u = us.pop(j)



        pairs.append({

            "known": k,

            "unknown": u,

            "year_gap": yg,

            "author_gap": ag,

            "matching_cost": cost

        })



# Freeze the subset before J-Lens scoring.

rng.shuffle(pairs)

pairs = pairs[:MAX_PAIRS]



n = len(pairs)

assert n > 0, "No matching pairs found"



# 50/10/40 split at the pair level.

n_build = int(n * 0.50)

n_tune = int(n * 0.10)



for i, p in enumerate(pairs):

    if i < n_build:

        split = "build"

    elif i < n_build + n_tune:

        split = "tune"

    else:

        split = "test"



    p["pair_id"] = f"pair_{i:04d}"

    p["split"] = split



flat = []

for p in pairs:

    for group in ("known", "unknown"):

        item = dict(p[group])

        item["group"] = "G_" + group

        item["pair_id"] = p["pair_id"]

        item["split"] = p["split"]

        flat.append(item)



assert len({r["paper_id"] for r in flat}) == 2*n



write_jsonl(ROOT / "matched_pairs.jsonl", pairs)

write_jsonl(ROOT / "matched_papers.jsonl", flat)



for split in ("build", "tune", "test"):

    write_jsonl(

        ROOT / f"matched_{split}.jsonl",

        [r for r in flat if r["split"] == split]

    )



summary = {

    "seed": SEED,

    "known_pool": len(known),

    "unknown_pool": len(unknown),

    "pairs": n,

    "papers": 2*n,

    "matching": "exact field + citation_bin + correct_label",

    "mean_year_gap": sum(p["year_gap"] for p in pairs)/n,

    "mean_author_gap": sum(p["author_gap"] for p in pairs)/n,

    "splits": dict(Counter(p["split"] for p in pairs)),

    "correct_labels": dict(Counter(

        p["known"]["correct_label"] for p in pairs

    ))

}



(ROOT / "matched_summary.json").write_text(

    json.dumps(summary, indent=2)

)



print(json.dumps(summary, indent=2))

print("\nSaved matched files to:", ROOT)

