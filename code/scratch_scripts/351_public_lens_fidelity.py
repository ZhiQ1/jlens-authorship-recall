#!/usr/bin/env python3
"""Unsteered Qwen3-32B: public Jacobian Lens vs vanilla lens vs final logits.
No fitting; resume-safe JSONL; fixed, authored generic prompts distinct from WikiText.
"""
import argparse
import json
import math
import os
import time
from pathlib import Path

import torch
import transformers
import jlens

PROMPTS = [
    'Explain why a bicycle remains easier to balance while moving than while standing still.\nAnswer:',
    'A library is organizing returned books by subject and author. Describe a sensible procedure.\nAnswer:',
    'In a distributed computing system, a request may wait for one slow server. Explain the resulting latency problem.\nAnswer:',
    'A farmer observes that tomatoes grow poorly when the soil stays waterlogged. Give a biological explanation.\nAnswer:',
    'Describe the role of a checksum when transferring a file between two computers.\nAnswer:',
    'Why does a metal spoon feel colder than a wooden spoon at the same room temperature?\nAnswer:',
    'A train arrives every fifteen minutes. Explain how a traveler could estimate the expected waiting time.\nAnswer:',
    'Summarize how sediment accumulates at the bottom of a river delta.\nAnswer:',
    'Explain the distinction between a database transaction and a database query.\nAnswer:',
    'In an orchestra, why must musicians coordinate rhythm even when playing different notes?\nAnswer:',
    'Describe a method for testing whether a new algorithm is faster on large datasets.\nAnswer:',
    'How do ocean currents influence coastal temperatures?\nAnswer:',
    'Explain what happens to network throughput when packet loss becomes frequent.\nAnswer:',
    'Describe the basic purpose of error-correcting codes in digital communication.\nAnswer:',
    'Why might a desert become cold shortly after sunset despite being very hot during the day?\nAnswer:',
    'A city adds dedicated bus lanes. Explain one possible effect on traffic patterns.\nAnswer:',
    'Compare the roles of producers and consumers in an ecosystem.\nAnswer:',
    'How does a compiler differ from an interpreter when processing source code?\nAnswer:',
    'Explain why repeated measurements are useful in a scientific experiment.\nAnswer:',
    'Describe how a telescope collects light from distant astronomical objects.\nAnswer:',
]

def metrics(candidate, final):
    a = candidate.float().flatten().cpu()
    b = final.float().flatten().cpu()
    if a.shape != b.shape or not bool(torch.isfinite(a).all()) or not bool(torch.isfinite(b).all()):
        raise ValueError('Nonfinite/mismatched logits')
    k = min(10, a.numel())
    ta = torch.topk(a, k).indices
    tb = torch.topk(b, k).indices
    pa = torch.log_softmax(a, -1)
    pb = torch.log_softmax(b, -1)
    # D_KL(P_final || P_candidate), in nats; measured on entire vocabulary.
    kl = torch.sum(pb.exp() * (pb - pa)).item()
    return {'top1_agree': int(ta[0] == tb[0]), 'top10_overlap': len(set(ta.tolist()) & set(tb.tolist())) / k, 'kl_final_to_lens_nats': float(kl), 'final_top1_rank': int((a > a[tb[0]]).sum().item()) + 1}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=3)
    ap.add_argument('--layers', default='16,24,32,40,48,56,62')
    ap.add_argument('--output', default='/scratch/{user}/jlens/351_all/351_public_fidelity.jsonl'.format(user=os.environ.get('USER', 'unknown')))
    ap.add_argument('--model', default='Qwen/Qwen3-32B')
    ap.add_argument('--model-revision', default='9216db5781bf21249d130ec9da846c4624c16137')
    ap.add_argument('--lens', default='/scratch/{user}/jlens/public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt'.format(user=os.environ.get('USER', 'unknown')))
    args = ap.parse_args()
    if not (1 <= args.n <= len(PROMPTS)):
        ap.error('n must be 1..20')
    layers = [int(x) for x in args.layers.split(',')]
    if len(set(layers)) != len(layers):
        ap.error('duplicate layers')
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    done = {}
    if output.exists():
        for line in output.read_text().splitlines():
            if line.strip():
                item = json.loads(line)
                if item.get('layers') != layers or item.get('model_revision') != args.model_revision or item.get('lens_path') != args.lens:
                    raise ValueError('Existing output has incompatible configuration; specify a new --output')
                done[item['prompt_index']] = item
    print('Existing complete prompts:', sorted(done), flush=True)
    print('Loading public lens (CPU)...', flush=True)
    lens = jlens.JacobianLens.load(args.lens)
    assert set(layers) <= set(lens.source_layers)
    assert lens.d_model == 5120
    print('Loading model...', flush=True)
    tok = transformers.AutoTokenizer.from_pretrained(args.model, revision=args.model_revision)
    hf = transformers.AutoModelForCausalLM.from_pretrained(args.model, revision=args.model_revision, dtype=torch.bfloat16, device_map='cuda', low_cpu_mem_usage=True).eval()
    model = jlens.from_hf(hf, tok)
    if not torch.cuda.is_available():
        raise RuntimeError('No GPU; this runner requires allocated A100/H200')
    for i, prompt in enumerate(PROMPTS[:args.n]):
        if i in done:
            print('Skipping completed prompt', i, flush=True)
            continue
        torch.cuda.reset_peak_memory_stats()
        t0 = time.perf_counter()
        # Both calls use same string, same layer list and last-token position.
        jlog, final, ids = lens.apply(model, prompt, layers=layers, positions=[-1], max_seq_len=128, use_jacobian=True)
        vlog, final_again, ids_again = lens.apply(model, prompt, layers=layers, positions=[-1], max_seq_len=128, use_jacobian=False)
        if not torch.equal(ids.cpu(), ids_again.cpu()):
            raise RuntimeError('Input token mismatch')
        final_delta = (final.float() - final_again.float()).abs().max().item()
        if not math.isfinite(final_delta) or final_delta > 0.1:
            raise RuntimeError('Unexpected different final logits between the paired forwards: {}'.format(final_delta))
        results = {}
        for layer in layers:
            results[str(layer)] = {'jlens': metrics(jlog[layer][-1], final[-1]), 'vanilla': metrics(vlog[layer][-1], final[-1])}
        row = {'prompt_index': i, 'prompt': prompt, 'model': args.model, 'model_revision': args.model_revision, 'lens_path': args.lens, 'n_fit_prompts': lens.n_prompts, 'layers': layers, 'token_count': int(ids.numel()), 'seconds': round(time.perf_counter()-t0,3), 'peak_gpu_gib': round(torch.cuda.max_memory_allocated()/1024**3,3), 'final_forward_max_delta': final_delta, 'metrics': results}
        with output.open('a') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
            f.flush()
            os.fsync(f.fileno())
        print('Prompt {}/{}: {:.1f}s, peak {:.2f}GiB, L32 J top1={}, vanilla top1={}'.format(i+1,args.n,row['seconds'],row['peak_gpu_gib'], results.get('32',results[str(layers[0])])['jlens']['top1_agree'],results.get('32',results[str(layers[0])])['vanilla']['top1_agree']), flush=True)
        del jlog, vlog, final, final_again
    valid = [json.loads(x) for x in output.read_text().splitlines() if x.strip() and json.loads(x)['prompt_index'] < args.n]
    print('===== FIDELITY SUMMARY =====', flush=True)
    print('Completed:',len(valid),'of',args.n,flush=True)
    for layer in layers:
        for mode in ('jlens','vanilla'):
            xs=[r['metrics'][str(layer)][mode] for r in valid]
            if not xs: continue
            print('L{:02d} {:7s} Top1={:.3f} Top10Overlap={:.3f} KL={:.3f} AvgFinalTop1Rank={:.1f}'.format(layer,mode,sum(q['top1_agree'] for q in xs)/len(xs),sum(q['top10_overlap'] for q in xs)/len(xs),sum(q['kl_final_to_lens_nats'] for q in xs)/len(xs),sum(q['final_top1_rank'] for q in xs)/len(xs)),flush=True)
    print('Output:',output,flush=True)

if __name__ == '__main__':
    main()
