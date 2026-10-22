
import json

import random

import statistics

from pathlib import Path

from collections import Counter, defaultdict



import networkx as nx



ROOT = Path("/scratch/zhang.zhiqi2/jlens")

SEED = 42

MAX_YEAR_GAP = 10

MAX_AUTHOR_GAP = 2



RECOG = ROOT / "recognition_primary_random_field_1000_results.jsonl"

HIDDEN = ROOT / "title_hidden_random_field_772_results.jsonl"

PREFIX = "matched_optimized"



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



def stratum(r):

    return (

        r["field"],

        r["citation_bin"],

        r["correct_label"]

    )



K = defaultdict(list)

U = defaultdict(list)



for r in known:

    K[stratum(r)].append(r)



for r in unknown:

    U[stratum(r)].append(r)



pairs = []



for key in sorted(set(K) & set(U)):

    ks = sorted(K[key], key=lambda x: x["paper_id"])

    us = sorted(U[key], key=lambda x: x["paper_id"])



    G = nx.Graph()



    for i in range(len(ks)):

        G.add_node(("k", i), bipartite=0)

    for j in range(len(us)):

        G.add_node(("u", j), bipartite=1)



    for i, k in enumerate(ks):

        for j, u in enumerate(us):

            yg = abs(int(k["year"]) - int(u["year"]))

            ag = abs(

                int(k["n_gt_authors"]) -

                int(u["n_gt_authors"])

            )



            if yg > MAX_YEAR_GAP or ag > MAX_AUTHOR_GAP:

                continue



            cost = yg + 5 * ag



            G.add_edge(

                ("k", i),

                ("u", j),

                weight=-cost

            )



    matching = nx.algorithms.matching.max_weight_matching(

        G,

        maxcardinality=True,

        weight="weight"

    )



    for a, b in matching:

        if a[0] == "u":

            a, b = b, a



        k = ks[a[1]]

        u = us[b[1]]



        yg = abs(int(k["year"]) - int(u["year"]))

        ag = abs(

            int(k["n_gt_authors"]) -

            int(u["n_gt_authors"])

        )



        pairs.append({

            "known": k,

            "unknown": u,

            "year_gap": yg,

            "author_gap": ag,

            "matching_cost": yg + 5 * ag,

            "matching_stratum": list(key)

        })



# Reproducible ordering and pair-level split.

pairs.sort(key=lambda p: (

    p["known"]["paper_id"],

    p["unknown"]["paper_id"]

))

rng = random.Random(SEED)

rng.shuffle(pairs)



n = len(pairs)

assert n > 0



n_build = round(n * 0.50)

n_tune = round(n * 0.10)



for i, p in enumerate(pairs):

    if i < n_build:

        split = "build"

    elif i < n_build + n_tune:

        split = "tune"

    else:

        split = "test"



    p["pair_id"] = f"optimized_{i:04d}"

    p["split"] = split



flat = []



for p in pairs:

    for group in ("known", "unknown"):

        r = dict(p[group])

        r["group"] = "G_" + group

        r["pair_id"] = p["pair_id"]

        r["split"] = p["split"]

        flat.append(r)



assert len({r["paper_id"] for r in flat}) == 2*n

assert all(

    p["year_gap"] <= MAX_YEAR_GAP

    and p["author_gap"] <= MAX_AUTHOR_GAP

    for p in pairs

)



write_jsonl(ROOT / f"{PREFIX}_pairs.jsonl", pairs)

write_jsonl(ROOT / f"{PREFIX}_papers.jsonl", flat)



for split in ("build", "tune", "test"):

    write_jsonl(

        ROOT / f"{PREFIX}_{split}.jsonl",

        [r for r in flat if r["split"] == split]

    )



years = [p["year_gap"] for p in pairs]

authors = [p["author_gap"] for p in pairs]



summary = {

    "method": "maximum-cardinality minimum-cost matching",

    "seed": SEED,

    "known_pool": len(known),

    "unknown_pool": len(unknown),

    "pairs": n,

    "papers": 2*n,

    "exact_match": [

        "field", "citation_bin", "correct_label"

    ],

    "max_year_gap": MAX_YEAR_GAP,

    "max_author_gap": MAX_AUTHOR_GAP,

    "mean_year_gap": round(statistics.mean(years), 2),

    "median_year_gap": statistics.median(years),

    "max_observed_year_gap": max(years),

    "mean_author_gap": round(statistics.mean(authors), 2),

    "median_author_gap": statistics.median(authors),

    "max_observed_author_gap": max(authors),

    "splits_pairs": dict(Counter(p["split"] for p in pairs)),

    "correct_labels": dict(

        Counter(p["known"]["correct_label"] for p in pairs)

    ),

    "fields": dict(Counter(p["known"]["field"] for p in pairs)),

    "citation_bins": dict(

        Counter(p["known"]["citation_bin"] for p in pairs)

    )

}



(ROOT / f"{PREFIX}_summary.json").write_text(

    json.dumps(summary, indent=2)

)



print(json.dumps(summary, indent=2))

print("\nSaved files to:", ROOT)

