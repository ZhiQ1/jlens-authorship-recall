#!/usr/bin/env python3
"""3.5.1 public Qwen3-32B J-Lens smoke readout; ONE paper, ONE gold first token.
Diagnostic only: no full-name scoring, no statistical inference, no steering.
"""
import argparse
import json
import os
import time
from pathlib import Path

import torch
import transformers
import jlens

DEFAULT_LENS = '/scratch/{user}/jlens/public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt'
DEFAULT_DATA = '/scratch/{user}/jlens/351_all/351_four_groups.jsonl'
DEFAULT_OUTPUT = '/scratch/{user}/jlens/351_all/351_public_smoke_result.json'
MODEL = 'Qwen/Qwen3-32B'
REVISION = '9216db5781bf21249d130ec9da846c4624c16137'  # Earlier local model revision
LAYERS = [16, 24, 32]


def choose_record(path):
    with open(path, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            # Prefer A and an explicit multiword author name, rather than initials.
            if row.get('group_351') != 'A':
                continue
            authors = [x.strip() for x in row.get('authors', '').split(';') if x.strip()]
            for name in authors:
                if len(name.split()) >= 2 and len(name) >= 10 and '.' not in name:
                    return row, name
    raise RuntimeError('No A-group paper with a suitable author found in input')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data', default=DEFAULT_DATA.format(user=os.environ['USER']))
    p.add_argument('--lens', default=DEFAULT_LENS.format(user=os.environ['USER']))
    p.add_argument('--output', default=DEFAULT_OUTPUT.format(user=os.environ['USER']))
    a = p.parse_args()
    assert torch.cuda.is_available(), 'This script requires an allocated CUDA GPU node'
    row, author = choose_record(a.data)
    prompt = f'Who are the authors of the paper titled "{row["title"]}" ({row["year"]})?\nAuthors:'
    # Crucial: score the first *new* token after the actual prompt tokenization.
    tokenizer = transformers.AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    candidate = ' ' + author
    prefix_ids = tokenizer.encode(prompt, add_special_tokens=False)
    combined_ids = tokenizer.encode(prompt + candidate, add_special_tokens=False)
    if combined_ids[:len(prefix_ids)] != prefix_ids or len(combined_ids) <= len(prefix_ids):
        raise RuntimeError('Tokenizer boundary resegmentation: cannot safely score first author token with this prompt; revise prompt protocol')
    gold_id = combined_ids[len(prefix_ids)]
    print('Paper:', row['paper_id'], 'group:', row['group_351'], flush=True)
    print('Author:', author, 'gold first token:', gold_id, repr(tokenizer.decode([gold_id])), flush=True)
    print('Loading public lens...', flush=True)
    t0 = time.monotonic()
    lens = jlens.JacobianLens.load(a.lens)
    assert all(layer in lens.source_layers for layer in LAYERS)
    print('Loading Qwen3-32B...', flush=True)
    hf = transformers.AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION, dtype=torch.bfloat16, device_map='cuda', low_cpu_mem_usage=True).eval()
    wrapped = jlens.from_hf(hf, tokenizer)
    torch.cuda.reset_peak_memory_stats()
    t1 = time.monotonic()
    print('Running lens.apply() ...', flush=True)
    lens_logits, model_logits, input_ids = lens.apply(wrapped, prompt, layers=LAYERS, positions=[-1], max_seq_len=512)
    result = {'paper_id': row['paper_id'], 'group_351': row['group_351'], 'title': row['title'], 'year': row['year'], 'gold_author': author, 'gold_first_token_id': gold_id, 'gold_first_token_text': tokenizer.decode([gold_id]), 'model': MODEL, 'model_revision': REVISION, 'lens_path': a.lens, 'n_lens_prompts': lens.n_prompts, 'layers': LAYERS, 'results': {}, 'load_seconds': round(t1-t0, 3), 'readout_seconds': round(time.monotonic()-t1, 3), 'peak_gpu_gib_since_reset': round(torch.cuda.max_memory_allocated()/1024**3, 3), 'protocol': 'single gold-author first token, no name-prefix; diagnostic smoke only'}
    for label, logits in [(f'L{layer}', lens_logits[layer]) for layer in LAYERS] + [('final_model', model_logits)]:
        vec = logits[0].float()
        if not torch.isfinite(vec).all().item():
            raise RuntimeError(f'Non-finite logits in {label}')
        gold_score = vec[gold_id]
        rank = int((vec > gold_score).sum().item()) + 1  # strict-greater ties
        result['results'][label] = {'rank': rank, 'reciprocal_rank': 1.0/rank, 'gold_logit': float(gold_score), 'vocab_size': vec.numel()}
    path = Path(a.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
    print('SAVED', path, flush=True)


if __name__ == '__main__':
    main()
