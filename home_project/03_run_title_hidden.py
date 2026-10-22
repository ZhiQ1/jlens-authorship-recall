import json

import re

from pathlib import Path



import torch

from transformers import AutoTokenizer, AutoModelForCausalLM





MODEL = "Qwen/Qwen3-32B"



INPUT = Path(

    "/scratch/zhang.zhiqi2/jlens/"

    "recognition_primary_random_field_1000_results.jsonl"

)



OUTPUT = Path(

    "/scratch/zhang.zhiqi2/jlens/"

    "title_hidden_random_field_772_results.jsonl"

)



PROMPT_FILE = Path(

    "config/prompts/mc_recognition.txt"

)



BATCH_SIZE = 8



MAX_NEW_TOKENS = 4





LETTER_RE = re.compile(r"\b([A-D])\b")





def parse_choice(text):

    if not text:

        return None



    s = text.strip()



    if s and s[0].upper() in "ABCD":

        return s[0].upper()



    m = LETTER_RE.findall(s.upper())



    return m[0] if m else None





def load_done(path):

    done = set()



    if not path.exists():

        return done



    with open(path, encoding="utf-8") as f:

        for line in f:

            if not line.strip():

                continue



            r = json.loads(line)



            done.add(

                r["paper_id"]

            )



    return done





# ============================================================

# Load frozen recognition items

# ============================================================



records = []



with open(INPUT, encoding="utf-8") as f:

    for line in f:

        if line.strip():

            records.append(

                json.loads(line)

            )





records = [r for r in records if r["recognition_correct"] == 1]

print("Input items:", len(records))





# ============================================================

# Resume support

# ============================================================



done = load_done(OUTPUT)



print("Already completed:", len(done))



todo = [

    r for r in records

    if r["paper_id"] not in done

]



print("Remaining:", len(todo))





# ============================================================

# Load exact repo recognition template

# ============================================================



template = PROMPT_FILE.read_text(

    encoding="utf-8"

)





# ============================================================

# Load Qwen3-32B

# ============================================================



print("\nLoading tokenizer...")



tok = AutoTokenizer.from_pretrained(

    MODEL

)



tok.padding_side = "left"

if tok.pad_token_id is None:

    tok.pad_token = tok.eos_token





print("Loading model...")



model = AutoModelForCausalLM.from_pretrained(

    MODEL,

    dtype=torch.bfloat16,

    device_map="cuda",

    low_cpu_mem_usage=True,

)



model.eval()





# ============================================================

# Prompt construction

# ============================================================



def build_prompt(r):



    raw = template.format(

        title=r["title"],

        year=r["year"],

        option_a=r["option_a"],

        option_b=r["option_b"],

        option_c=r["option_c"],

        option_d=r["option_d"],

    )



    # Remove paper title only from the target question.

    # Keep year, options, option order and few-shot examples.

    original_question = (

        "Which of the following is the author list of the paper titled "

        f"'{r['title']}' which was published in {r['year']}?"

    )

    hidden_question = (

        "Which of the following is the author list of a paper "

        f"published in {r['year']}?"

    )



    assert original_question in raw, (

        f"Target question not found for {r['paper_id']}"

    )



    raw = raw.replace(

        original_question,

        hidden_question,

        1

    )



    messages = [

        {

            "role": "user",

            "content": raw,

        }

    ]



    prompt = tok.apply_chat_template(

        messages,

        tokenize=False,

        add_generation_prompt=True,

        enable_thinking=False,

    )



    return prompt





# ============================================================

# Batched inference

# ============================================================



OUTPUT.parent.mkdir(

    parents=True,

    exist_ok=True

)





with open(

    OUTPUT,

    "a",

    encoding="utf-8"

) as sink:



    for start in range(

        0,

        len(todo),

        BATCH_SIZE

    ):



        batch = todo[

            start:start + BATCH_SIZE

        ]



        prompts = [

            build_prompt(r)

            for r in batch

        ]



        enc = tok(

            prompts,

            return_tensors="pt",

            padding=True,

            truncation=True,

            max_length=2048,

        )



        enc = {

            k: v.to(model.device)

            for k,v in enc.items()

        }



        with torch.inference_mode():



            out = model.generate(

                **enc,

                max_new_tokens=MAX_NEW_TOKENS,

                do_sample=False,

                pad_token_id=tok.pad_token_id,

                eos_token_id=tok.eos_token_id,

            )





        input_len = enc[

            "input_ids"

        ].shape[1]





        for i, r in enumerate(batch):



            gen_ids = out[

                i,

                input_len:

            ]



            raw_output = tok.decode(

                gen_ids,

                skip_special_tokens=True

            ).strip()



            chosen = parse_choice(

                raw_output

            )



            correct = int(

                chosen

                == r["correct_label"]

            )



            result = {

                **r,



                "title_hidden_chosen_label":

                    chosen,



                "title_hidden_correct":

                    correct,



                "title_hidden_parse_failed":

                    int(

                        chosen is None

                    ),



                "title_hidden_raw_output":

                    raw_output,

            }



            sink.write(

                json.dumps(

                    result,

                    ensure_ascii=False

                )

                + "\n"

            )



            sink.flush()





        finished = min(

            start + len(batch),

            len(todo)

        )



        total_done = (

            len(done)

            + finished

        )





        print(

            f"{total_done}/{len(records)} complete"

        )





print("\n===== COMPLETE =====")

print("Saved:")

print(OUTPUT)
