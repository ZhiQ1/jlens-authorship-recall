
import json

import random

from pathlib import Path

from collections import Counter



import networkx as nx



ROOT = Path("/scratch/zhang.zhiqi2/jlens")

NAMES = ["optimized", "moderate", "relaxed"]

SEED = 42

TARGET = {"build": 0.50, "tune": 0.10, "test": 0.40}



def read_jsonl(path):

    with path.open(encoding="utf-8") as f:

        return [json.loads(x) for x in f if x.strip()]



def write_jsonl(path, rows):

    with path.open("w", encoding="utf-8") as f:

        for r in rows:

            f.write(json.dumps(r, ensure_ascii=False) + "\n")



cohorts = {}

graph = nx.Graph()



# All matching relationships across all three specifications.

for name in NAMES:

    pairs = read_jsonl(ROOT / f"matched_{name}_pairs.jsonl")

    cohorts[name] = pairs



    for p in pairs:

        a = p["known"]["paper_id"]

        b = p["unknown"]["paper_id"]



        assert a != b

        graph.add_edge(a, b)



components = list(nx.connected_components(graph))

rng = random.Random(SEED)



print("Total unique papers:", graph.number_of_nodes())

print("Total components:", len(components))

print("Largest components:",

      sorted((len(c) for c in components), reverse=True)[:10])



# Assign whole connected components to splits.

# Greedy balance against 50/10/40 target.

rng.shuffle(components)

components.sort(key=len, reverse=True)



total = graph.number_of_nodes()

target_counts = {s: total * frac for s, frac in TARGET.items()}

counts = Counter()

assignment = {}



for component in components:

    size = len(component)



    def score(split):

        future = dict(counts)

        future[split] = future.get(split, 0) + size

        return sum(

            (future.get(s, 0) - target_counts[s]) ** 2

            for s in TARGET

        )



    selected = min(TARGET, key=score)



    for paper_id in component:

        assignment[paper_id] = selected



    counts[selected] += size



# Write aligned files, preserving the original matches.

summary = {

    "seed": SEED,

    "unique_papers": total,

    "connected_components": len(components),

    "largest_component": max(map(len, components)),

    "universe_split_papers": dict(counts),

    "cohorts": {}

}



for name, pairs in cohorts.items():

    aligned_pairs = []

    flat = []



    for p in pairs:

        a = p["known"]["paper_id"]

        b = p["unknown"]["paper_id"]



        assert assignment[a] == assignment[b]

        split = assignment[a]



        new_pair = dict(p)

        new_pair["split"] = split

        aligned_pairs.append(new_pair)



        for group in ("known", "unknown"):

            r = dict(p[group])

            r["pair_id"] = p["pair_id"]

            r["group"] = "G_" + group

            r["split"] = split

            flat.append(r)



    prefix = f"matched_{name}_aligned"



    write_jsonl(ROOT / f"{prefix}_pairs.jsonl", aligned_pairs)

    write_jsonl(ROOT / f"{prefix}_papers.jsonl", flat)



    for split in TARGET:

        write_jsonl(

            ROOT / f"{prefix}_{split}.jsonl",

            [r for r in flat if r["split"] == split]

        )



    split_counts = Counter(p["split"] for p in aligned_pairs)

    summary["cohorts"][name] = {

        "pairs": len(aligned_pairs),

        "splits_pairs": dict(split_counts)

    }



# Global validation: no paper receives conflicting splits.

observed = {}

for name in NAMES:

    path = ROOT / f"matched_{name}_aligned_papers.jsonl"

    for r in read_jsonl(path):

        pid = r["paper_id"]

        split = r["split"]

        assert pid not in observed or observed[pid] == split

        observed[pid] = split



assert len(observed) == total



out = ROOT / "matched_aligned_split_summary.json"

out.write_text(json.dumps(summary, indent=2))



print("\n===== ALIGNED SPLIT SUMMARY =====")

print(json.dumps(summary, indent=2))

print("\nGlobal split conflicts: 0")

print("All original matching pairs preserved.")

