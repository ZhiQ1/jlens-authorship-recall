
import json

import random

import hashlib

from pathlib import Path



import pyarrow.parquet as pq

from huggingface_hub import HfApi, hf_hub_download

from transformers import AutoTokenizer



ROOT = Path("/scratch/zhang.zhiqi2/jlens")

OUT = ROOT / "fitting_corpus"

OUT.mkdir(parents=True, exist_ok=True)



DATASET = "Salesforce/wikitext"

MODEL = "Qwen/Qwen3-32B"

CONFIG = "wikitext-103-raw-v1"

SEED = 42

SEQ_LEN = 128

N = 1000



rng = random.Random(SEED)

api = HfApi()



# Resolve immutable dataset and tokenizer revisions.

dataset_sha = api.repo_info(

    DATASET, repo_type="dataset"

).sha



model_sha = api.model_info(MODEL).sha



print("Dataset revision:", dataset_sha)

print("Model revision:", model_sha)



tok = AutoTokenizer.from_pretrained(

    MODEL,

    revision=model_sha

)



files = [

    f"{CONFIG}/train-00000-of-00002.parquet",

    f"{CONFIG}/train-00001-of-00002.parquet"

]



paths = []

for filename in files:

    print("Downloading:", filename)

    path = hf_hub_download(

        repo_id=DATASET,

        repo_type="dataset",

        filename=filename,

        revision=dataset_sha,

        local_dir=OUT / "source"

    )

    paths.append(Path(path))



def sha256(path):

    h = hashlib.sha256()

    with open(path, "rb") as f:

        for block in iter(lambda: f.read(1024 * 1024), b""):

            h.update(block)

    return h.hexdigest()



# Reservoir sample complete token sequences.

# Each 128-token chunk has an opportunity to enter

# the fixed-size sample. Preserve source metadata.

sample = []

seen = 0

buffer = []

origin = None



def offer(ids, source):

    global seen

    seen += 1

    item = {

        "token_ids": ids,

        "source_file": source

    }



    if len(sample) < N:

        sample.append(item)

    else:

        j = rng.randrange(seen)

        if j < N:

            sample[j] = item



for path in paths:

    parquet = pq.ParquetFile(path)



    for batch in parquet.iter_batches(

        batch_size=2048,

        columns=["text"]

    ):

        for raw in batch.column(0).to_pylist():

            if not raw or not raw.strip():

                continue



            ids = tok.encode(

                raw,

                add_special_tokens=False

            )



            if not ids:

                continue



            if origin is None:

                origin = path.name



            buffer.extend(ids)



            while len(buffer) >= SEQ_LEN:

                chunk = buffer[:SEQ_LEN]

                buffer = buffer[SEQ_LEN:]

                offer(chunk, origin)

                origin = path.name



assert len(sample) == N, (

    f"Only {len(sample)} sequences obtained"

)



rng.shuffle(sample)



prompts = [

    tok.decode(

        item["token_ids"],

        skip_special_tokens=False,

        clean_up_tokenization_spaces=False

    )

    for item in sample

]



# Confirm the actual text remains sufficiently long

# after decode/re-tokenization.

lengths = [

    len(tok.encode(t, add_special_tokens=False))

    for t in prompts

]



assert min(lengths) >= 18, (

    f"Too-short sequence: {min(lengths)} tokens"

)



corpus_path = OUT / "wikitext103_qwen32b_1000.jsonl"



with corpus_path.open("w", encoding="utf-8") as f:

    for i, (prompt, item) in enumerate(zip(prompts, sample)):

        f.write(json.dumps({

            "index": i,

            "text": prompt,

            "source_file": item["source_file"],

            "original_token_count": len(item["token_ids"])

        }, ensure_ascii=False) + "\n")



manifest = {

    "dataset": DATASET,

    "dataset_revision": dataset_sha,

    "dataset_config": CONFIG,

    "split": "train",

    "model_tokenizer": MODEL,

    "model_revision": model_sha,

    "seed": SEED,

    "sequence_length": SEQ_LEN,

    "sequences": N,

    "candidate_chunks_seen": seen,

    "min_retokenized_length": min(lengths),

    "max_retokenized_length": max(lengths),

    "source_shards_sha256": {

        p.name: sha256(p) for p in paths

    },

    "corpus_sha256": sha256(corpus_path)

}



(OUT / "manifest.json").write_text(

    json.dumps(manifest, indent=2)

)



print("\n===== CORPUS COMPLETE =====")

print("Sequences:", len(prompts))

print("Candidate chunks:", seen)

print("Token lengths:", min(lengths), max(lengths))

print("SHA256:", manifest["corpus_sha256"])

print("Saved:", corpus_path)

