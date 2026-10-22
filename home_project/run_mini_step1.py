import re

import random

import pandas as pd

import torch

import transformers



from dua.probing.stages.stage1_generate import build_prompt, SYSTEM_MSG





MODEL = "Qwen/Qwen3-32B"



MASTER = "data/interim/probing_prompts_9108.csv"

OUT = "/scratch/zhang.zhiqi2/jlens/mini_step1_pilot30.csv"



N_PER_GROUP = 10

MAX_NEW_TOKENS_OPEN = 96

MAX_NEW_TOKENS_MC = 8



SEED = 42

random.seed(SEED)





# --------------------------------------------------

# Helpers

# --------------------------------------------------



def normalize_name(x):

    x = x.lower().strip()

    x = re.sub(r"[^\w\s]", " ", x)

    x = re.sub(r"\s+", " ", x)

    return x.strip()





def parse_author_list(text):

    """

    Convert:

        'A. Smith; B. Jones'

    into normalized author strings.

    """

    parts = re.split(r";|\n|,", text)

    out = []



    for p in parts:

        p = normalize_name(p)

        if p:

            out.append(p)



    return out





def author_overlap(pred, gold):

    """

    Simple pilot metric:

    fraction of gold authors approximately recovered.



    This is deliberately simple for mini Step 1;

    later replace with the full benchmark scorer.

    """

    pred_names = parse_author_list(pred)

    gold_names = parse_author_list(gold)



    if not gold_names:

        return 0.0



    matched = 0



    for g in gold_names:

        if any(g == p or g in p or p in g for p in pred_names):

            matched += 1



    return matched / len(gold_names)





def make_chat_prompt(tok, user_text):

    messages = [

        {

            "role": "system",

            "content": SYSTEM_MSG

        },

        {

            "role": "user",

            "content": user_text

        },

    ]



    try:

        return tok.apply_chat_template(

            messages,

            tokenize=False,

            add_generation_prompt=True,

            enable_thinking=False,

        )

    except TypeError:

        return tok.apply_chat_template(

            messages,

            tokenize=False,

            add_generation_prompt=True,

        )





@torch.no_grad()

def generate(model, tok, prompt, max_new_tokens):

    enc = tok(

        prompt,

        return_tensors="pt",

        add_special_tokens=False,

    )



    enc = {

        k: v.to(model.device)

        for k, v in enc.items()

    }



    out = model.generate(

        **enc,

        max_new_tokens=max_new_tokens,

        do_sample=False,

        pad_token_id=tok.eos_token_id,

    )



    new_tokens = out[0, enc["input_ids"].shape[1]:]



    return tok.decode(

        new_tokens,

        skip_special_tokens=True,

    ).strip()





def extract_title_year(question):

    m = re.search(

        r"paper titled '(.+?)' which was published in (\d{4})",

        question,

        flags=re.IGNORECASE | re.DOTALL,

    )



    if not m:

        raise ValueError(

            f"Could not parse title/year from question:\n{question}"

        )



    return m.group(1), m.group(2)





def parse_mc_answer(text):

    """

    Prefer an isolated A/B/C/D.

    """

    m = re.search(r"\b([ABCD])\b", text.upper())



    if m:

        return m.group(1)



    return ""





# --------------------------------------------------

# 1. Load 9,108 prompt dataset

# --------------------------------------------------



df = pd.read_csv(MASTER)



print("Master shape:", df.shape)

print("Columns:", list(df.columns))



df["citation"] = pd.to_numeric(

    df["citation"],

    errors="coerce"

)



df = df.dropna(

    subset=["citation", "question", "answer"]

).copy()



df = df.sort_values("citation").reset_index(drop=True)





# --------------------------------------------------

# 2. Sample 30:

#    10 low / 10 mid / 10 high citation

# --------------------------------------------------



n = len(df)



low_pool = df.iloc[: n // 3]

mid_pool = df.iloc[n // 3 : 2 * n // 3]

high_pool = df.iloc[2 * n // 3 :]



low = low_pool.sample(

    N_PER_GROUP,

    random_state=SEED

).copy()



mid = mid_pool.sample(

    N_PER_GROUP,

    random_state=SEED + 1

).copy()



high = high_pool.sample(

    N_PER_GROUP,

    random_state=SEED + 2

).copy()



low["citation_group"] = "low"

mid["citation_group"] = "mid"

high["citation_group"] = "high"



pilot = pd.concat(

    [low, mid, high],

    ignore_index=True

)



pilot = pilot.sample(

    frac=1,

    random_state=SEED

).reset_index(drop=True)



print("\nPilot citation groups:")

print(

    pilot.groupby("citation_group")["citation"]

    .agg(["count", "min", "median", "max"])

)





# --------------------------------------------------

# 3. Load Qwen3-32B once

# --------------------------------------------------



print("\nLoading Qwen3-32B...")



tok = transformers.AutoTokenizer.from_pretrained(

    MODEL

)



model = transformers.AutoModelForCausalLM.from_pretrained(

    MODEL,

    dtype=torch.bfloat16,

    device_map="cuda",

    low_cpu_mem_usage=True,

)



model.eval()



print("Model loaded.")





# --------------------------------------------------

# 4. Run mini Step 1

# --------------------------------------------------



results = []



all_answers = pilot["answer"].tolist()





for i, row in pilot.iterrows():



    paper_id = row["paperId"]

    question = row["question"]

    gold = row["answer"]



    title, year = extract_title_year(question)



    print("\n" + "=" * 80)

    print(f"[{i+1}/{len(pilot)}]")

    print("paperId :", paper_id)

    print("citation:", row["citation"])

    print("group   :", row["citation_group"])

    print("title   :", title)

    print("gold    :", gold)



    # ----------------------------------------------

    # A. OPEN RECALL

    # Exact same prompt builder as Stage 1

    # ----------------------------------------------



    open_prompt = build_prompt(

        tok,

        title=title,

        year=year,

        chat_style="qwen3",

    )



    open_output = generate(

        model,

        tok,

        open_prompt,

        MAX_NEW_TOKENS_OPEN,

    )



    overlap = author_overlap(

        open_output,

        gold

    )



    # Pilot definition:

    # > 0.5 = recall-correct enough

    open_correct = overlap > 0.5



    print("open output :", open_output)

    print("open overlap:", overlap)



    # ----------------------------------------------

    # B. Build recognition options

    # ----------------------------------------------



    other_answers = [

        a for a in all_answers

        if a != gold

    ]



    distractors = random.sample(

        other_answers,

        3

    )



    options = distractors + [gold]



    random.shuffle(options)



    letters = ["A", "B", "C", "D"]



    correct_idx = options.index(gold)

    correct_letter = letters[correct_idx]



    option_text = "\n".join(

        f"{letters[j]}. {options[j]}"

        for j in range(4)

    )



    # ----------------------------------------------

    # B1. Recognition WITH title

    # ----------------------------------------------



    recognition_user = (

        f"Which of the following author lists belongs to the paper "

        f"titled '{title}', published in {year}?\n\n"

        f"{option_text}\n\n"

        "Answer with only A, B, C, or D."

    )



    recognition_prompt = make_chat_prompt(

        tok,

        recognition_user

    )



    recognition_output = generate(

        model,

        tok,

        recognition_prompt,

        MAX_NEW_TOKENS_MC,

    )



    recognition_choice = parse_mc_answer(

        recognition_output

    )



    recognition_correct = (

        recognition_choice == correct_letter

    )



    print(

        "recognition:",

        recognition_output,

        "| gold =", correct_letter,

        "| correct =", recognition_correct

    )



    # ----------------------------------------------

    # B2. TITLE-HIDDEN CONTROL

    #

    # SAME OPTIONS, but remove title.

    # ----------------------------------------------



    hidden_user = (

        f"A paper was published in {year}. "

        f"Which of the following author lists belongs to it?\n\n"

        f"{option_text}\n\n"

        "Answer with only A, B, C, or D."

    )



    hidden_prompt = make_chat_prompt(

        tok,

        hidden_user

    )



    hidden_output = generate(

        model,

        tok,

        hidden_prompt,

        MAX_NEW_TOKENS_MC,

    )



    hidden_choice = parse_mc_answer(

        hidden_output

    )



    hidden_correct = (

        hidden_choice == correct_letter

    )



    print(

        "title-hidden:",

        hidden_output,

        "| gold =", correct_letter,

        "| correct =", hidden_correct

    )



    # ----------------------------------------------

    # 5. Assign behavioral pilot group

    # ----------------------------------------------



    if open_correct:



        behavior_group = "Recall-correct"



    elif recognition_correct and not hidden_correct:



        behavior_group = "Known-but-not-recalled"



    elif not recognition_correct:



        behavior_group = "Recognition-fail"



    else:



        # Recognition right AND title-hidden right.

        # Ambiguous: could be option/prior leakage.

        behavior_group = "Ambiguous-control"



    print("LABEL:", behavior_group)



    results.append({

        "paperId": paper_id,

        "citation": row["citation"],

        "citation_bin": row.get("citation_bin", ""),

        "citation_group": row["citation_group"],

        "field": row.get("field", ""),

        "title": title,

        "year": year,



        "gold_answer": gold,



        "open_output": open_output,

        "open_overlap": overlap,

        "open_correct": open_correct,



        "correct_option": correct_letter,



        "recognition_output": recognition_output,

        "recognition_choice": recognition_choice,

        "recognition_correct": recognition_correct,



        "title_hidden_output": hidden_output,

        "title_hidden_choice": hidden_choice,

        "title_hidden_correct": hidden_correct,



        "behavior_group": behavior_group,

    })



    # Save after every paper so time-limit interruption

    # does not destroy completed work.

    pd.DataFrame(results).to_csv(

        OUT,

        index=False

    )





# --------------------------------------------------

# 6. Summary

# --------------------------------------------------



result_df = pd.DataFrame(results)



print("\n\n===== MINI STEP 1 COMPLETE =====")



print("\nBehavior groups:")

print(

    result_df["behavior_group"]

    .value_counts(dropna=False)

)



print("\nCitation x behavior:")

print(

    pd.crosstab(

        result_df["citation_group"],

        result_df["behavior_group"]

    )

)



print("\nSaved:")

print(OUT)
