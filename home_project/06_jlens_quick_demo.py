
import json

from pathlib import Path

import torch

import transformers

import jlens



ROOT = Path("/scratch/zhang.zhiqi2/jlens")

MODEL = "Qwen/Qwen3-32B"

LENS = ROOT / "qwen32b_jlens_smoke_2.pt"



print("Loading fitted J-Lens...", flush=True)

lens = jlens.JacobianLens.load(str(LENS))

print("Lens:", lens, flush=True)



print("Loading Qwen3-32B...", flush=True)

tok = transformers.AutoTokenizer.from_pretrained(MODEL)

hf = transformers.AutoModelForCausalLM.from_pretrained(

    MODEL,

    dtype=torch.bfloat16,

    device_map="cuda",

    low_cpu_mem_usage=True,

).eval()

model = jlens.from_hf(hf, tok)



# First confirm that factual readout works end-to-end.

examples = [

    ("capital", "The capital of France is", " Paris"),

    ("scientist", "The theory of general relativity was developed by", " Albert"),

    ("author", "The novel Pride and Prejudice was written by", " Jane"),

]



output = []



for name, prompt, expected in examples:

    print(f"\n===== {name} =====", flush=True)



    with torch.inference_mode():

        lens_logits, model_logits, _ = lens.apply(

            model,

            prompt,

            layers=[24, 32, 40, 48, 56, 62],

            positions=[-1],

            max_seq_len=128,

        )



    target_ids = tok.encode(expected, add_special_tokens=False)

    gold_id = target_ids[0]



    for layer in sorted(lens_logits):

        scores = lens_logits[layer][0]

        top_ids = scores.topk(5).indices.tolist()

        top_words = [tok.decode([i]) for i in top_ids]

        gold_rank = int((scores > scores[gold_id]).sum().item()) + 1



        result = {

            "example": name,

            "layer": layer,

            "gold_first_token": tok.decode([gold_id]),

            "gold_rank": gold_rank,

            "top5": top_words,

        }

        output.append(result)

        print(

            f"L{layer}: gold_rank={gold_rank}, top5={top_words}",

            flush=True,

        )



    final_scores = model_logits[0]

    final_rank = int(

        (final_scores > final_scores[gold_id]).sum().item()

    ) + 1

    print(f"Final-model gold rank: {final_rank}", flush=True)



path = ROOT / "jlens_quick_demo_results.json"

path.write_text(json.dumps(output, indent=2, ensure_ascii=False))



print("\nRESULTS SAVED:", path, flush=True)

