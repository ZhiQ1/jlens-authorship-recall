"""2026-11-21: screenshots of selected slides (relaunches the browser if it dies). usage: shots_20261121.py <deck.html> <outdir> <n:n:...>"""
import sys, os, re
from playwright.sync_api import sync_playwright
f='file://'+sys.argv[1]; out=sys.argv[2]; os.makedirs(out,exist_ok=True)
ns=[int(x) for x in re.split('[,:]',sys.argv[3])]
todo=[n for n in ns if not os.path.exists(f'{out}/s{n:02d}.png') or os.environ.get('FORCE')]
with sync_playwright() as p:
    for attempt in range(6):
        if not todo: break
        try:
            b=p.chromium.launch(args=['--disable-dev-shm-usage','--disable-gpu']); pg=b.new_page(viewport={'width':1280,'height':772})
            while todo:
                n=todo[0]
                pg.goto('about:blank'); pg.goto(f+f'#s{n}'); pg.wait_for_timeout(1000)
                pg.locator('#stage').screenshot(path=f'{out}/s{n:02d}.png'); todo.pop(0)
            b.close()
        except Exception as e:
            print('attempt',attempt,'error at',todo[:1],str(e)[:200])
print('missing',todo)
