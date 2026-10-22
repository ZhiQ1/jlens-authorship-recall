
import os

import json

import statistics

from pathlib import Path



import torch

import transformers

import jlens



root = Path("/scratch") / os.environ["USER"] / "jlens"

data = root / "matched_moderate_aligned_test.jsonl"

output = root / "jlens_authorship_29pairs.jsonl"



records = [json.loads(s) for s in data.open() if s.strip()]

pairs = {}



for r in records:

    pairs.setdefault(r["pair_id"], {})[r["group"]] = r



selected = [

    (pid, pair)

    for pid, pair in sorted(pairs.items())

    if "G_known" in pair and "G_unknown" in pair

][:29]



assert len(selected) == 29, "Could not find 29 complete pairs"

completed = set()

if output.exists():

    for line in output.open():

        old = json.loads(line)

        completed.add((old["pair_id"], old["group"]))

print("Already completed:", len(completed), flush=True)



print("Selected pairs:", len(selected), flush=True)



lens = jlens.JacobianLens.load(

    str(root / "qwen32b_jlens_smoke_2.pt")

)



model_id = "Qwen/Qwen3-32B"

tok = transformers.AutoTokenizer.from_pretrained(model_id)



hf = transformers.AutoModelForCausalLM.from_pretrained(

    model_id,

    dtype=torch.bfloat16,

    device_map="cuda",

    low_cpu_mem_usage=True,

).eval()



model = jlens.from_hf(hf, tok)



results = []



for pid, pair in selected:

    for group in ("G_known", "G_unknown"):

        if (pid, group) in completed:

            continue

        r = pair[group]



        prompt = (

            f'Who are the authors of the paper titled '

            f'"{r["title"]}" ({r["year"]})?\nAuthors:'

        )



        gold = r["ground_truth_authors"][0]

        gold_ids = tok.encode(

            " " + gold, add_special_tokens=False

        )

        assert gold_ids

        gold_id = gold_ids[0]



        with torch.inference_mode():

            layer_logits, final_logits, _ = lens.apply(

                model,

                prompt,

                layers=[24, 32, 40, 48, 56, 62],

                positions=[-1],

                max_seq_len=128,

            )



        ranks = {}

        top5 = {}



        for layer, logits in layer_logits.items():

            scores = logits[0].float()

            ranks[str(layer)] = (

                int((scores > scores[gold_id]).sum().item()) + 1

            )

            top5[str(layer)] = [

                tok.decode([i])

                for i in scores.topk(5).indices.tolist()

            ]



        final_scores = final_logits[0].float()

        final_rank = (

            int((final_scores > final_scores[gold_id]).sum().item()) + 1

        )



        result = {

            "pair_id": pid,

            "group": group,

            "paper_id": r["paper_id"],

            "title": r["title"],

            "year": r["year"],

            "gold_author": gold,

            "gold_token": tok.decode([gold_id]),

            "ranks": ranks,

            "final_rank": final_rank,

            "top5": top5,

        }



        results.append(result)



        with output.open("a", encoding="utf-8") as f:

            f.write(json.dumps(result, ensure_ascii=False) + "\n")



        print(

            pid, group,

            "gold:", repr(gold),

            "token:", repr(result["gold_token"]),

            "ranks:", ranks,

            "final:", final_rank,

            flush=True,

        )



print("\n===== GROUP COMPARISON =====")

for group in ("G_known", "G_unknown"):

    subset = [r for r in results if r["group"] == group]

    for layer in ("24", "32", "40", "48", "56", "62"):

        values = [r["ranks"][layer] for r in subset]

        print(group, "L" + layer, "median rank:", statistics.median(values))



print("RESULTS SAVED:", output)

