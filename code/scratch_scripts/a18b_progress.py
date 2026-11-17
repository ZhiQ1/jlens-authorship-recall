#!/usr/bin/env python
"""append one line to the addendum-18b section of ~/jlens_work/PROGRESS.md (section created at the top on first use)."""
import sys, time
from pathlib import Path
P = Path.home() / 'jlens_work/PROGRESS.md'; HDR = '## 2026-11-17 — [Stage 13] addendum 18b (shelf map) GPU items: log'
s = P.read_text(); line = f'- {time.strftime("%m-%d %H:%M")} ' + ' '.join(sys.argv[1:])
if HDR not in s:
    i = s.index('\n## '); s = s[:i] + '\n' + HDR + '\n' + line + '\n' + s[i:]
else:
    i = s.index(HDR) + len(HDR); j = s.find('\n## ', i); j = len(s) if j < 0 else j
    s = s[:j].rstrip('\n') + '\n' + line + '\n' + s[j:]
P.write_text(s)
