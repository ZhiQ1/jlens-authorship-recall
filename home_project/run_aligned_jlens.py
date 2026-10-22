import torch

import transformers

import jlens



from dua.probing.stages.stage1_generate import build_prompt



MODEL = "Qwen/Qwen3-32B"

LENS_PATH = "/scratch/zhang.zhiqi2/jlens/qwen32b_fit_test/jacobian_lens.pt"



title = "The Use of Tallow Fatty Acids in Rubber"

year = "1975"

gold = "W. Klingensmith"



print("Loading model...")



hf = transformers.AutoModelForCausalLM.from_pretrained(

    MODEL,

    dtype=torch.bfloat16,

    device_map="cuda",

    low_cpu_mem_usage=True,

)



tok = transformers.AutoTokenizer.from_pretrained(MODEL)

model = jlens.from_hf(hf, tok)



print("Loading lens...")

lens = jlens.JacobianLens.load(LENS_PATH)



base_prompt = build_prompt(

    tok,

    title=title,

    year=year,

    chat_style="qwen3",

)



# Gold answer tokens under exact continuation context

prompt_ids = tok(

    base_prompt,

    add_special_tokens=False,

)["input_ids"]



full_ids = tok(

    base_prompt + gold,

    add_special_tokens=False,

)["input_ids"]



common = 0

for a, b in zip(prompt_ids, full_ids):

    if a != b:

        break

    common += 1



gold_ids = full_ids[common:]



print("\n===== GOLD TOKENIZATION =====")

print("gold author:", gold)

print("gold ids:", gold_ids)

print("gold tokens:", [tok.decode([i]) for i in gold_ids])



rows = []



for step, target_id in enumerate(gold_ids):

    prefix_ids = gold_ids[:step]

    prefix_text = tok.decode(prefix_ids)



    current_prompt = base_prompt + prefix_text



    print("\n" + "=" * 70)

    print(f"STEP {step + 1}/{len(gold_ids)}")

    print("gold prefix:", repr(prefix_text))

    print("target token:", repr(tok.decode([target_id])))

    print("=" * 70)



    lens_logits, model_logits, _ = lens.apply(

        model,

        current_prompt,

        layers=[62],

        positions=[-1],

        max_seq_len=512,

        use_jacobian=True,

    )



    jl = lens_logits[62][0].float().cpu()

    ml = model_logits[0].float().cpu()



    jl_score = jl[target_id].item()

    jl_rank = int((jl > jl[target_id]).sum().item()) + 1



    ml_score = ml[target_id].item()

    ml_rank = int((ml > ml[target_id]).sum().item()) + 1



    print("J-Lens score:", jl_score)

    print("J-Lens rank :", jl_rank)



    print("Model score :", ml_score)

    print("Model rank  :", ml_rank)



    rows.append({

        "step": step + 1,

        "prefix": prefix_text,

        "target": tok.decode([target_id]),

        "target_id": target_id,

        "jl_score": jl_score,

        "jl_rank": jl_rank,

        "model_score": ml_score,

        "model_rank": ml_rank,

    })



print("\n\n===== SUMMARY =====")

print(

    f"{'step':<5} "

    f"{'target':<12} "

    f"{'J-Lens rank':<15} "

    f"{'Model rank':<12}"

)



for r in rows:

    print(

        f"{r['step']:<5} "

        f"{repr(r['target']):<12} "

        f"{r['jl_rank']:<15} "

        f"{r['model_rank']:<12}"

    )



print("\nDONE")
