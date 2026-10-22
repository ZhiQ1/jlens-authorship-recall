import csv

import gzip

import json

import math

import random

from collections import defaultdict

from pathlib import Path



from dua.recognition.distractors import (

    DistractorBuilder,

    build_field_pools,

)



SEED = 42

N_SAMPLE = 1000



EVAL_PATH = Path(

    "data/release/eval_sample_9108.csv.gz"

)



RECALL_PATH = Path(

    "data/release/probing/runs/qwen3_32b/scored.tsv.gz"

)



OUT_PATH = Path(

    "/scratch/zhang.zhiqi2/jlens/"

    "recognition_primary_random_field_1000.jsonl"

)



SUMMARY_PATH = Path(

    "/scratch/zhang.zhiqi2/jlens/"

    "recognition_primary_random_field_1000_summary.json"

)





# ============================================================

# 1. Load all 9,108 evaluation papers

# ============================================================



papers = []



with gzip.open(

    EVAL_PATH,

    "rt",

    encoding="utf-8"

) as f:



    reader = csv.DictReader(f)



    for row in reader:



        authors = json.loads(row["authors"])



        paper = {

            "paper_id": row["paper_id"],

            "title": row["title"],

            "year": int(row["year"]),

            "field": row["field"],

            "citations": int(row["citations"]),

            "citation_bin": row["citation_bin"],

            "n_authors": int(row["n_authors"]),

            "authors": authors,

        }



        papers.append(paper)





print("Loaded evaluation papers:", len(papers))





# ============================================================

# 2. Build field pools FROM FULL 9,108

#

# Important:

# This must happen BEFORE subsetting to HR2 failures.

# ============================================================



print("Building full field author pools...")



field_pools = build_field_pools(papers)



print("\nField pool sizes:")



for field in sorted(field_pools):

    print(

        f"{field:20s}",

        len(field_pools[field])

    )





# ============================================================

# 3. Load released Qwen3 recall HR2

# ============================================================



hr2_by_id = {}



with gzip.open(

    RECALL_PATH,

    "rt",

    encoding="utf-8"

) as f:



    reader = csv.DictReader(

        f,

        delimiter="\t"

    )



    for row in reader:



        try:

            hr2 = float(row["hr2"])

        except (TypeError, ValueError):

            continue



        hr2_by_id[row["paper_id"]] = hr2





print(

    "\nLoaded HR2 scores:",

    len(hr2_by_id)

)





# ============================================================

# 4. Attach HR2 and retain recall failures

# ============================================================



candidates = []



missing_hr2 = 0



for paper in papers:



    hr2 = hr2_by_id.get(

        paper["paper_id"]

    )



    if hr2 is None:

        missing_hr2 += 1

        continue



    if hr2 > 0.5:



        item = dict(paper)

        item["hr2"] = hr2



        candidates.append(item)





print(

    "\nRecall-failure candidates "

    "(HR2 > 0.5):",

    len(candidates)

)



print(

    "Missing HR2:",

    missing_hr2

)





# ============================================================

# 5. Stratify by:

#

#       field × citation_bin

#

# ============================================================



strata = defaultdict(list)



for paper in candidates:



    key = (

        paper["field"],

        paper["citation_bin"],

    )



    strata[key].append(paper)





print(

    "\nNumber of non-empty strata:",

    len(strata)

)





# ============================================================

# 6. Largest-remainder proportional allocation

#

# Makes total quota exactly N_SAMPLE.

# ============================================================



total_candidates = len(candidates)



allocation = {}



remainders = []



allocated = 0



for key, rows in strata.items():



    exact = (

        N_SAMPLE

        * len(rows)

        / total_candidates

    )



    base = math.floor(exact)



    # cannot sample more than available

    base = min(base, len(rows))



    allocation[key] = base



    allocated += base



    remainders.append(

        (

            exact - base,

            key,

        )

    )





remaining = N_SAMPLE - allocated



# Largest fractional remainder first.

remainders.sort(

    key=lambda x: x[0],

    reverse=True

)



for _, key in remainders:



    if remaining <= 0:

        break



    if allocation[key] < len(strata[key]):



        allocation[key] += 1

        remaining -= 1





if remaining != 0:

    raise RuntimeError(

        f"Could not allocate all samples; "

        f"{remaining} left."

    )





print(

    "\nAllocated sample total:",

    sum(allocation.values())

)





# ============================================================

# 7. Deterministic within-stratum sampling

# ============================================================



rng = random.Random(SEED)



sampled = []



for key in sorted(strata):



    rows = list(strata[key])



    # Stable ordering before seeded sampling.

    rows.sort(

        key=lambda x: x["paper_id"]

    )



    k = allocation[key]



    if k == 0:

        continue



    chosen = rng.sample(

        rows,

        k

    )



    sampled.extend(chosen)





assert len(sampled) == N_SAMPLE





# Stable final order.

sampled.sort(

    key=lambda x: x["paper_id"]

)





print(

    "\nFinal stratified sample:",

    len(sampled)

)





# ============================================================

# 8. Construct official repo random_field MC items

#

# IMPORTANT:

# Builder uses pools from FULL 9,108 papers.

# ============================================================



builder = DistractorBuilder(

    field_pools,

    seed=SEED

)





OUT_PATH.parent.mkdir(

    parents=True,

    exist_ok=True

)





records = []



for i, paper in enumerate(

    sampled,

    start=1

):



    mc = builder.random_field(

        paper

    )



    record = {

        **mc.as_record(),



        # Keep original truth for later analysis.

        "ground_truth_authors":

            paper["authors"],



        "n_gt_authors":

            paper["n_authors"],



        "hr2":

            paper["hr2"],



        "sampling_field":

            paper["field"],



        "sampling_citation_bin":

            paper["citation_bin"],



        "sampling_seed":

            SEED,



        "sampling_n":

            N_SAMPLE,

    }



    records.append(record)



    if i <= 5:



        print("\n" + "=" * 70)

        print(

            f"Example {i}"

        )

        print(

            "paper_id:",

            record["paper_id"]

        )

        print(

            "title:",

            record["title"]

        )

        print(

            "year:",

            record["year"]

        )

        print(

            "field:",

            record["field"]

        )

        print(

            "citation_bin:",

            record["citation_bin"]

        )

        print(

            "HR2:",

            record["hr2"]

        )

        print(

            "correct:",

            record["correct_label"]

        )



        for label in "abcd":

            print(

                label.upper() + ":",

                record[

                    f"option_{label}"

                ]

            )





# ============================================================

# 9. Save JSONL

# ============================================================



with open(

    OUT_PATH,

    "w",

    encoding="utf-8"

) as f:



    for r in records:



        f.write(

            json.dumps(

                r,

                ensure_ascii=False

            )

            + "\n"

        )





# ============================================================

# 10. Save summary

# ============================================================



field_counts = defaultdict(int)

bin_counts = defaultdict(int)

stratum_counts = defaultdict(int)



for r in records:



    field_counts[

        r["field"]

    ] += 1



    bin_counts[

        r["citation_bin"]

    ] += 1



    key = (

        r["field"],

        r["citation_bin"],

    )



    stratum_counts[str(key)] += 1





summary = {

    "total_eval_papers":

        len(papers),



    "recall_failure_candidates":

        len(candidates),



    "hr2_threshold":

        0.5,



    "sample_n":

        len(records),



    "seed":

        SEED,



    "stratification":

        [

            "field",

            "citation_bin",

        ],



    "distractor_mode":

        "random_field",



    "field_counts":

        dict(field_counts),



    "citation_bin_counts":

        dict(bin_counts),



    "stratum_counts":

        dict(stratum_counts),

}





with open(

    SUMMARY_PATH,

    "w",

    encoding="utf-8"

) as f:



    json.dump(

        summary,

        f,

        ensure_ascii=False,

        indent=2

    )





print("\n" + "=" * 70)

print("COMPLETE")



print(

    "\nSaved MC items:"

)

print(OUT_PATH)



print(

    "\nSaved summary:"

)

print(SUMMARY_PATH)



print(

    "\nTotal items:",

    len(records)

)



print(

    "\nCitation-bin counts:"

)



for k in sorted(bin_counts):

    print(

        k,

        bin_counts[k]

    )



print(

    "\nField counts:"

)



for k in sorted(field_counts):

    print(

        k,

        field_counts[k]

    )
