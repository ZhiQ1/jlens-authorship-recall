import sys
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/talk/src'); out = Path(sys.argv[1])
src = (D / 'build.py').read_text().replace("HERE = Path(__file__).parent", f"HERE = Path({str(D)!r})")
src = src.replace("out = HERE / 'Stage10_author_readout_talk.pptx'", f"out = Path({str(out)!r})")
exec(compile(src, 'build.py', 'exec'), {'__name__': 'b'})
