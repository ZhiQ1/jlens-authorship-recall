"""Run DIR/build_v18.py with charts from the talk src dir; background and pptx written only into DIR."""
from pathlib import Path
DIR = Path(__file__).resolve().parent
SRC = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/talk/src')
out = DIR / 'talk_v18.pptx'
src = (DIR / 'build_v18.py').read_text()
for old, new in [("HERE = Path(__file__).parent", f"HERE = Path({str(SRC)!r})"),
                 ("bg = HERE / 'paper.png'", f"bg = Path({str(DIR / 'paper.png')!r})"),
                 ("out = HERE / 'Stage10_author_readout_talk.pptx'", f"out = Path({str(out)!r})")]:
    assert src.count(old) == 1, old
    src = src.replace(old, new)
exec(compile(src, 'build_v18.py', 'exec'), {'__name__': 'b'})
