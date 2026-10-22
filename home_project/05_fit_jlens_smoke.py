
import json

import hashlib

import logging

from pathlib import Path



import torch

import transformers

import jlens



ROOT = Path("/scratch/zhang.zhiqi2/jlens")

CORPUS = ROOT / "fitting_corpus/wikitext103_qwen32b_1000.jsonl"

MANIFEST = ROOT / "fitting_corpus/manifest.json"



OUT = ROOT / "qwen32b_jlens_smoke_2.pt"

CKPT = ROOT / "qwen32b_jlens_smoke_2_ckpt.pt"

RUN_CONFIG = ROOT / "qwen32b_jlens_smoke_2_config.json"



MODEL = "Qwen/Qwen3-32B"

LAYERS = [24, 32, 40, 48, 56, 62]

TARGET = 63

N_PROMPTS = 2



logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s %(levelname)s %(message)s"

)



def sha256(path):

    h = hashlib.sha256()

    with path.open("rb") as f:

        for block in iter(lambda: f.read(1024 * 1024), b""):

            h.update(block)

    return h.hexdigest()



meta = json.loads(MANIFEST.read_text())

actual_hash = sha256(CORPUS)



assert actual_hash == meta["corpus_sha256"]



rows = [

    json.loads(line)

    for line in CORPUS.open(encoding="utf-8")

    if line.strip()

]



assert len(rows) == 1000

assert [r["index"] for r in rows] == list(range(1000))



prompts = [r["text"] for r in rows[:N_PROMPTS]]



config = {

    "model": MODEL,

    "model_revision": meta["model_revision"],

    "corpus_sha256": actual_hash,

    "selected_prompt_indices": list(range(N_PROMPTS)),

    "source_layers": LAYERS,

    "target_layer": TARGET,

    "dim_batch": 8,

    "max_seq_len": 128,

    "skip_first": 16

}



# Protect checkpoint against accidental configuration changes.

if CKPT.exists():

    assert RUN_CONFIG.exists(), "Checkpoint has no config manifest"

    saved_config = json.loads(RUN_CONFIG.read_text())

    assert saved_config == config, "Checkpoint configuration mismatch"

else:

    assert not RUN_CONFIG.exists(), (

        "Config exists without checkpoint; inspect before proceeding"

    )

    RUN_CONFIG.write_text(json.dumps(config, indent=2))



print("===== J-LENS SMOKE TEST =====", flush=True)

print("Prompts:", len(prompts), flush=True)

print("Layers:", LAYERS, flush=True)

print("Corpus hash verified:", actual_hash, flush=True)



assert torch.cuda.is_available(), "GPU not allocated"

print("GPU:", torch.cuda.get_device_name(0), flush=True)



print("Loading Qwen3-32B...", flush=True)



hf = transformers.AutoModelForCausalLM.from_pretrained(

    MODEL,

    revision=meta["model_revision"],

    dtype=torch.bfloat16,

    device_map="cuda",

    low_cpu_mem_usage=True

)



tok = transformers.AutoTokenizer.from_pretrained(

    MODEL,

    revision=meta["model_revision"]

)



model = jlens.from_hf(hf, tok)



print("Model loaded. Starting Jacobian fitting.", flush=True)



lens = jlens.fit(

    model,

    prompts=prompts,

    source_layers=LAYERS,

    target_layer=TARGET,

    dim_batch=8,

    max_seq_len=128,

    skip_first=16,

    checkpoint_path=str(CKPT),

    checkpoint_every=1,

    resume=True

)



lens.save(str(OUT))



print("===== FIT COMPLETE =====", flush=True)

print("Valid fitted prompts:", lens.n_prompts, flush=True)

print("Saved lens:", OUT, flush=True)

print("Saved checkpoint:", CKPT, flush=True)

