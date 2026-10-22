import re

import pandas as pd

import torch

import transformers

import jlens



from dua.probing.stages.stage1_generate import build_prompt



MODEL = "Qwen/Qwen3-32B"

LENS_PATH = "/scratch/zhang.zhiqi2/jlens/qwen32b_multilayer_test.pt"

STEP1_CSV = "/scratch/zhang.zhiqi2/jlens/mini_step1_pilot30.csv"

OUT = "/scratch/zhang.zhiqi2/jlens/group_jlens_raw.csv"



LAYERS = [24, 32, 40, 48, 56, 62]



def first_author_surname(answer):

    first = str(answer).split(",")[0].strip()



    # examples:

    # "W. Klingensmith" -> Klingensmith

    # "Alexandre Rachkov" -> Rachkov

    # "Arndt" -> Arndt

    parts = first.split()



    if not parts:

        return None



    return parts[-1]



def rank_of(logits, token_id):

    logits = logits.float().cpu()

    return int((logits > logits[token_id]).sum().item()) + 1



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



    title = row["title"]

    year = str(row["year"])

    gold = row["gold_answer"]

    group = row["behavior_group"]



    surname = first_author_surname(gold)



    if not surname:

        print("SKIP no surname:", row["paperId"])

        continue



    # Score surname onset after supplying first-author prefix before surname.

    # Example:

    # gold = "W. Klingensmith"

    # prefix = "W."

    # target = " Kling"

    first_author = str(gold).split(",")[0].strip()

    author_parts = first_author.split()



    if len(author_parts) <= 1:

        prefix_text = ""

    else:

        prefix_text = " ".join(author_parts[:-1])



    target_text = " " + surname



    target_ids = tok.encode(

        target_text,

        add_special_tokens=False,

    )



    if not target_ids:

        print("SKIP tokenization:", row["paperId"], surname)

        continue



    # first subword of surname

    target_id = target_ids[0]

    target_token = tok.decode([target_id])



    base_prompt = build_prompt(

        tok,

        title=title,

        year=year,

        chat_style="qwen3",

    )



    current_prompt = base_prompt + prefix_text



    print("\n" + "=" * 70)

    print(f"[{i+1}/{len(clean)}]")

    print("group :", group)

    print("title :", title)

    print("gold  :", gold)

    print("first author:", first_author)

    print("prefix:", repr(prefix_text))

    print("surname:", surname)

    print("target token:", repr(target_token), target_id)



    lens_logits, model_logits, _ = lens.apply(

        model,

        current_prompt,

        layers=LAYERS,

        positions=[-1],

        max_seq_len=512,

        use_jacobian=True,

    )



    result = {

        "paperId": row["paperId"],

        "behavior_group": group,

        "citation": row["citation"],

        "citation_group": row["citation_group"],

        "field": row.get("field", ""),

        "title": title,

        "year": year,

        "gold_answer": gold,

        "first_author": first_author,

        "surname": surname,

        "prefix_text": prefix_text,

        "target_token": target_token,

        "target_token_id": target_id,

    }



    ranks = []



    for layer in LAYERS:

        x = lens_logits[layer][0]

        r = rank_of(x, target_id)



        result[f"rank_L{layer}"] = r

        ranks.append((layer, r))



        print(f"L{layer}: rank={r}")



    final_rank = rank_of(

        model_logits[0],

        target_id,

    )



    result["final_rank"] = final_rank



    best_layer, best_rank = min(

        ranks,

        key=lambda x: x[1],

    )



    result["best_rank"] = best_rank

    result["best_layer"] = best_layer



    # first layer where Top-K is achieved

    for k in [10, 100, 1000]:

        first = None



        for layer, r in ranks:

            if r <= k:

                first = layer

                break



        result[f"first_top{k}_layer"] = first



    print("FINAL:", final_rank)

    print("BEST :", best_rank, "@ L", best_layer)



    rows.append(result)



    # save after every paper

    pd.DataFrame(rows).to_csv(

        OUT,

        index=False,

    )



print("\n===== COMPLETE =====")



res = pd.DataFrame(rows)



print("\nRows:", len(res))



print("\nGroup counts:")

print(res["behavior_group"].value_counts())



print("\nMedian best rank:")

print(

    res.groupby("behavior_group")["best_rank"]

    .median()

)



print("\nMedian final rank:")

print(

    res.groupby("behavior_group")["final_rank"]

    .median()

)



print("\nSaved:")

print(OUT)
