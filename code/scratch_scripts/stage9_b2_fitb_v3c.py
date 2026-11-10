"""Item 2-1 continuation after the D12-4 WARN decision (2026-11-09). Runs ONLY if the locked deviation record
381_stage13/config/prereg_addendum12_deviations_D12-4.json exists (mode 444, sha256 == its .sha256 file, decision WARN_continue).

The D12-1 gate (stage9_b2_fitb_v2/v3, job 11753858) FAILED only on prompt-66 max||J||/sqrt(d) (4.378043 vs logged 4.367, threshold
0.004867 < bf16 spacing 0.03125 at this magnitude). Its outputs stay untouched in 381_stage13/b2_fitb/ (gate.json, gate_v2.json,
HARD_CHECK_FAILED). The continuation uses a NEW root 381_stage13/b2_fitb_d124/ that holds a verified copy of the 66-prompt backup and a
gate file with status PASS + warn D12-4 (written by `setup`, its sha256 is in the record). All work is the unchanged v1/v2 code
(stage9_b2_fitb_v2.py main with --root <new root>): frozen Fit B resume to 100/100, holdout, 168 read units, analysis.
Commands: setup | verify | status | gpu <v2 gpu args> | analyze
"""
import hashlib, importlib.util, json, os, shutil, stat, sys
from datetime import datetime
from pathlib import Path

H = Path.home() / 'jlens_work'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
OLD = R13 / 'b2_fitb'; ROOT2 = R13 / 'b2_fitb_d124'
REC = R13 / 'config/prereg_addendum12_deviations_D12-4.json'; REC_SHA = R13 / 'config/prereg_addendum12_deviations_D12-4.json.sha256'
GATE_FILES = ('summary/gate.json', 'summary/gate_v2.json')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''): h.update(b)
    return h.hexdigest()


def gate_doc(src, rec_path):
    d = json.loads((OLD / src).read_text())
    return dict(status='PASS', status_basis=f'D12-4 WARN (record {rec_path}): original gate status FAIL kept in {OLD / src}',
                warn='D12-4', original_status=d['status'], original_file=str(OLD / src), original_sha256=sha(OLD / src),
                rows=d['rows'], rule=d.get('rule'), at=datetime.now().isoformat(timespec='seconds'))


def setup():
    """CPU, once, before the record is locked: new root with backup copy + PASS-with-WARN gate files. Returns their sha256."""
    (ROOT2 / 'summary').mkdir(parents=True, exist_ok=True)
    m = json.loads((OLD / 'checkpoint_B066.json').read_text())
    for f in ('checkpoint_B066.pt', 'checkpoint_B066.json'):
        if not (ROOT2 / f).exists(): shutil.copy2(OLD / f, ROOT2 / f)
    if sha(ROOT2 / 'checkpoint_B066.pt') != m['sha256']: raise SystemExit('backup copy sha256 differs')
    out = {}
    for g in GATE_FILES:
        p = ROOT2 / g
        if not p.exists(): p.write_text(json.dumps(gate_doc(g, REC), indent=1, default=float))
        out[g] = sha(p)
    return dict(root=str(ROOT2), backup_copy_sha256=m['sha256'], gate_files_sha256=out)


def verify():
    if not REC.exists(): return False, 'no D12-4 record'
    if stat.S_IMODE(os.stat(REC).st_mode) & 0o222: return False, 'record not locked (writable)'
    if sha(REC) != REC_SHA.read_text().split()[0]: return False, 'record sha256 differs from .sha256'
    r = json.loads(REC.read_text())
    if r.get('decision') != 'WARN_continue': return False, f'record decision {r.get("decision")}'
    for g, h in r['continuation']['gate_files_sha256'].items():
        if sha(ROOT2 / g) != h: return False, f'{g} changed since the record'
    if (ROOT2 / 'HARD_CHECK_FAILED').exists(): return False, 'HARD_CHECK_FAILED in the new root'
    return True, 'D12-4 record verified'


def v2():
    sp = importlib.util.spec_from_file_location('fitb_v2', H / '09_stage9/stage9_b2_fitb_v2.py'); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def status():
    sp = importlib.util.spec_from_file_location('b2c_status', H / '13_stage13/b2c_status.py'); st = importlib.util.module_from_spec(sp); sp.loader.exec_module(st)
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): st.status_21(root=ROOT2)
    d = json.loads(buf.getvalue().strip().splitlines()[-1])
    if d.get('next') == 'analyze' and (ROOT2 / 'reports/b2_fitb_report.md').exists(): d.update(next='done', reason='report written (new root)')
    ok, why = verify()
    if not ok: d.update(next='failed', reason=why)
    print(json.dumps(d), flush=True)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'setup': print(json.dumps(setup())); return 0
    if cmd == 'verify': ok, why = verify(); print('VERIFY', ok, why); return 0 if ok else 3
    if cmd == 'status': status(); return 0
    if cmd in ('gpu', 'analyze'):
        ok, why = verify()
        if not ok: raise SystemExit(f'D12-4 continuation refused: {why}')
        V2 = v2(); sys.argv = ['stage9_b2_fitb_v2.py'] + sys.argv[1:] + ['--root', str(ROOT2)]; V2.main(); return 0
    raise SystemExit('usage: stage9_b2_fitb_v3c.py setup|verify|status|gpu ...|analyze')


if __name__ == '__main__':
    sys.exit(main())
