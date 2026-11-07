"""Group C batch-2 status (for b2_orch.py): pure file checks, stdlib only (no torch / numpy), one JSON line per call.
Used by `status` in stage9_b2_fitb_v2.py (2-1), stage12_b2_f1team_v2.py (2-2), stage13_b2_gennames_v2.py (2-11)."""
import json
from pathlib import Path

B = Path('/scratch/zhang.zhiqi2/jlens'); R13 = B / '381_stage13'; R12 = B / '371_stage12'; R9 = B / '351_stage9'
LOGS13, LOGS12 = R13 / 'logs', R12 / 'logs'


def _j(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return None


def _tiny_pass(logdir, pat):
    for f in sorted(Path(logdir).glob(pat)):
        try:
            if 'TINY v2 PASS' in f.read_text(errors='replace'): return True
        except Exception: pass
    return False


def _out(item, nxt, reason, progress):
    s = json.dumps(dict(item=item, next=nxt, reason=reason, progress=progress)); print(s, flush=True); return s


def status_211(root=R13 / 'b2_gennames_v2', n_shards=48):
    n = len(list((root / 'raw/resid').glob('shard_*.npz'))); pr = f'{n}/{n_shards}'
    if (root / 'HARD_CHECK_FAILED').exists(): return _out('2-11', 'failed', 'HARD_CHECK_FAILED (greedy first-name reproduction < 90%)', pr)
    rc = _j(root / 'summary/repro_check.json')
    if rc and rc.get('status') != 'PASS': return _out('2-11', 'failed', f'repro_check {rc.get("status")} {rc.get("share")}', pr)
    if not _tiny_pass(LOGS13, 'b2_gennames_v2_tiny_*.log'): return _out('2-11', 'wait_tests', 'no "TINY v2 PASS" in logs/b2_gennames_v2_tiny_*.log', pr)
    if not (root / 'build.json').exists() or not (root / 'names.parquet').exists(): return _out('2-11', 'wait_tests', 'build.json / names.parquet missing (CPU build)', pr)
    if not rc or not (root / 'raw/resid/shard_000.npz').exists(): return _out('2-11', 'gate', 'repro check + shard 0 not done', pr)
    if n < n_shards: return _out('2-11', 'rest', f'{n_shards - n} shards left', pr)
    if not (R13 / 'reports/b2_gennames_report.md').exists() or not (root / 'summary/probe_within.csv').exists(): return _out('2-11', 'probe', 'all shards done; probe/report missing', pr)
    return _out('2-11', 'done', 'report written', pr)


def status_22(root=R12, n_units=144):
    hc = _j(root / 'summary/b2_f1team_hardcheck.json'); prog = _j(root / 'alens_team_joint/progress.json') or {}
    k = int(prog.get('done', 0)); reads = len(list((root / 'raw/alens_team_read').glob('*/shard_*.npz')))
    if (root / 'summary/B2_F1TEAM_HARD_CHECK_FAILED').exists() or (hc and hc.get('status') != 'PASS'):
        return _out('2-2', 'failed', 'D12-2 hard check FAIL (B2_F1TEAM_HARD_CHECK_FAILED / hardcheck json)', f'{k}/40')
    if not _tiny_pass(LOGS12, 'b2_f1team_v2_tiny_*.log'): return _out('2-2', 'wait_tests', 'no "TINY v2 PASS" in 371_stage12/logs/b2_f1team_v2_tiny_*.log', f'{k}/40')
    lens = all((root / f'alens_team_{h}/lens.pt').exists() for h in 'AB')
    if not lens or not hc: return _out('2-2', 'fit', 'joint fit < 40/40 or hard check not yet run (one fit job at a time)', f'{k}/40')
    if reads == 0: return _out('2-2', 'read_gate', 'hard check PASS; no read unit yet', f'{reads}/{n_units}')
    if reads < n_units: return _out('2-2', 'rest', f'{n_units - reads} read units left', f'{reads}/{n_units}')
    if not (R13 / 'reports/b2_f1team_report.md').exists(): return _out('2-2', 'analyze', 'all read units done; report missing', f'{reads}/{n_units}')
    return _out('2-2', 'done', 'report written', f'{reads}/{n_units}')


def status_21(root=R13 / 'b2_fitb', n_units=168):
    run = R9 / 'runner_runs/full_B_100_7layers'; g = _j(root / 'summary/gate_v2.json')
    rl = []
    try: rl = [json.loads(x) for x in (root / 'resume_log.jsonl').read_text().splitlines() if x.strip()]
    except Exception: pass
    k = rl[-1]['after'] if rl else 66
    if (root / 'HARD_CHECK_FAILED').exists() or (g and g.get('status') != 'PASS'): return _out('2-1', 'failed', 'D12-1 gate_v2 FAIL / HARD_CHECK_FAILED', f'{k}/100')
    if rl and (rl[-1].get('check_rc') != 0 or rl[-1].get('after', 0) < rl[-1].get('before', 0)): return _out('2-1', 'failed', f'resume check failed: {rl[-1]}', f'{k}/100')
    if not _tiny_pass(LOGS13, 'b2_fitb_v2_tiny_*.log'): return _out('2-1', 'wait_tests', 'no "TINY v2 PASS" in logs/b2_fitb_v2_tiny_*.log', f'{k}/100')
    if not _j(root / 'checkpoint_B066.json'): return _out('2-1', 'failed', 'no verified 66-prompt backup (run stage9_b2_fitb_backup.sbatch)', f'{k}/100')
    if not g: return _out('2-1', 'gate_v2', 'D12-1 gate not run', f'{k}/100')
    if not (run / 'fit_status.json').exists(): return _out('2-1', 'resume', 'Fit B < 100/100 (one resume job at a time)', f'{k}/100')
    reads = len(list((root / 'raw/read').glob('*/shard_*.npz'))) + int((root / 'holdout/holdout_stats.npz').exists())
    if reads < n_units + 1: return _out('2-1', 'holdout_and_rest', f'{n_units + 1 - reads} units left (holdout + 7 conds x 24 shards)', f'{reads}/{n_units + 1}')
    if not (R13 / 'reports/b2_fitb_report.md').exists(): return _out('2-1', 'analyze', 'all units done; report missing', f'{reads}/{n_units + 1}')
    return _out('2-1', 'done', 'report written', f'{reads}/{n_units + 1}')
