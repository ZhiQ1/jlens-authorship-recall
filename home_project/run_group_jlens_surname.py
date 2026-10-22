import pandas as pd

import torch

import transformers

import jlens



from dua.probing.stages.stage1_generate import build_prompt



MODEL = "Qwen/Qwen3-32B"

LENS_PATH = "/scratch/zhang.zhiqi2/jlens/qwen32b_multilayer_test.pt"

STEP1_CSV = "/scratch/zhang.zhiqi2/jlens/mini_step1_pilot30.csv"

OUT = "/scratch/zhang.zhiqi2/jlens/group_jlens_surname.csv"



LAYERS = [24, 32, 40, 48, 56, 62]



def rank_of(logits, token_id):

    x = logits.float().cpu()

    return int((x > x[token_id]).sum().item()) + 1



def first_author_parts(answer):

    first = str(answer).split(",")[0].strip()

    parts = first.split()



    if not parts:

        return None, None, None



    surname = parts[-1]



    if len(parts) == 1:

        prefix = ""

    else:

        prefix = " ".join(parts[:-1])



    return first, prefix, surname





df = pd.read_csv(STEP1_CSV)



clean = df[

    df["behavior_group"].isin(

        ["Known-but-not-recalled", "Recognition-fail"]

    )

].copy()



print("Clean cohort:")

print(clean["behavior_group"].value_counts())

print("Total:", len(clean))



print("\nLoading model...")



tok = transformers.AutoTokenizer.from_pretrained(MODEL)



hf = transformers.AutoModelForCausalLM.from_pretrained(

    MODEL,

    dtype=torch.bfloat16,

    device_map="cuda",

    low_cpu_mem_usage=True,

)



model = jlens.from_hf(hf, tok)



print("Loading lens...")

lens = jlens.JacobianLens.load(LENS_PATH)



print("Lens layers:", sorted(lens.jacobians.keys()))



rows = []



for i, row in clean.reset_index(drop=True).iterrows():



    first_author, prefix_text, surname = first_author_parts(

        row["gold_answer"]

    )



    if surname is None:

        continue



    # Leading space matters because surname follows the given-name/initial prefix.

    surname_text = " " + surname



    surname_ids = tok.encode(

        surname_text,

        add_special_tokens=False,

    )



    if not surname_ids:

        continue



    print("\n" + "=" * 72)

    print(f"[{i+1}/{len(clean)}]")

    print("group :", row["behavior_group"])

    print("title :", row["title"])

    print("gold  :", row["gold_answer"])

    print("first author:", first_author)

    print("prefix:", repr(prefix_text))

    print("surname:", surname)

    print(

        "surname tokens:",

        [repr(tok.decode([t])) for t in surname_ids]

    )



    base_prompt = build_prompt(

        tok,

        title=row["title"],

        year=str(row["year"]),

        chat_style="qwen3",

    )



    # Store all token ranks for each layer.

    per_layer_ranks = {

        layer: []

        for layer in LAYERS

    }



    final_ranks = []



    # Teacher forcing across surname tokens.

    for step, target_id in enumerate(surname_ids):



        previous_surname_ids = surname_ids[:step]

        previous_surname_text = tok.decode(previous_surname_ids)



        current_prompt = (

            base_prompt

            + prefix_text

            + previous_surname_text

        )



        target_token = tok.decode([target_id])



        lens_logits, model_logits, _ = lens.apply(

            model,

            current_prompt,

            layers=LAYERS,

            positions=[-1],

            max_seq_len=512,

            use_jacobian=True,

        )



        print(

            f"  token {step+1}/{len(surname_ids)}:",

            repr(target_token)

        )



        for layer in LAYERS:

            r = rank_of(

                lens_logits[layer][0],

                target_id

            )



            per_layer_ranks[layer].append(r)



        fr = rank_of(

            model_logits[0],

            target_id

        )



        final_ranks.append(fr)



    result = {

        "paperId": row["paperId"],

        "behavior_group": row["behavior_group"],

        "citation": row["citation"],

        "citation_group": row["citation_group"],

        "field": row.get("field", ""),

        "title": row["title"],

        "year": row["year"],

        "gold_answer": row["gold_answer"],

        "first_author": first_author,

        "prefix_text": prefix_text,

        "surname": surname,

        "surname_n_tokens": len(surname_ids),

    }



    # Per-layer surname MRR.

    layer_mrrs = []



    for layer in LAYERS:



        ranks = per_layer_ranks[layer]



        mrr = sum(

            1.0 / r

            for r in ranks

        ) / len(ranks)



        mean_rank = sum(ranks) / len(ranks)



        max_rank = max(ranks)



        result[f"mrr_L{layer}"] = mrr

        result[f"mean_rank_L{layer}"] = mean_rank

        result[f"worst_rank_L{layer}"] = max_rank



        layer_mrrs.append(

            (layer, mrr)

        )



        print(

            f"L{layer}: "

            f"MRR={mrr:.6f} "

            f"mean_rank={mean_rank:.1f} "

            f"worst_rank={max_rank}"

        )



    final_mrr = sum(

        1.0 / r

        for r in final_ranks

    ) / len(final_ranks)



    final_mean_rank = (

        sum(final_ranks) / len(final_ranks)

    )



    final_worst_rank = max(final_ranks)



    result["mrr_final"] = final_mrr

    result["mean_rank_final"] = final_mean_rank

    result["worst_rank_final"] = final_worst_rank



    best_layer, best_mrr = max(

        layer_mrrs,

        key=lambda x: x[1]

    )



    result["best_mrr"] = best_mrr

    result["best_layer"] = best_layer



    print(

        "FINAL:",

        f"MRR={final_mrr:.6f}",

        f"mean_rank={final_mean_rank:.1f}",

        f"worst_rank={final_worst_rank}"

    )



    print(

        "BEST J-Lens:",

        f"L{best_layer}",

        f"MRR={best_mrr:.6f}"

    )



    rows.append(result)



    pd.DataFrame(rows).to_csv(

        OUT,

        index=False

    )



print("\n===== COMPLETE =====")



res = pd.DataFrame(rows)



print("\nRows:", len(res))



print("\nGroup counts:")

print(

    res["behavior_group"]

    .value_counts()

)



print("\nMedian best MRR:")

print(

    res.groupby("behavior_group")["best_mrr"]

    .median()

)



print("\nMedian final MRR:")

print(

    res.groupby("behavior_group")["mrr_final"]

    .median()

)



print("\nSaved:")

print(OUT)
