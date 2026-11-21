"""find a free 1280x720-stage spot for a formula/n box on given slides. usage: fxpos.py deck.html out.json n:w:h,..."""
import sys, json
from playwright.sync_api import sync_playwright
f = 'file://' + sys.argv[1]; out = sys.argv[2]
req = [tuple(int(v) for v in x.split(':')) for x in sys.argv[3].split(',')]
JS = """([W,H])=>{const s=document.querySelector('.slide.on');const q=document.getElementById('stage').getBoundingClientRect();const sc=q.width/1280;
 const R=[];for(const e of s.querySelectorAll('*')){if(e.children.length&&!(e instanceof SVGTextElement))continue;const r=e.getBoundingClientRect();if(!r.width||!r.height)continue;
  const x0=(r.left-q.left)/sc,y0=(r.top-q.top)/sc,x1=(r.right-q.left)/sc,y1=(r.bottom-q.top)/sc; if((x1-x0)*(y1-y0)>1280*720*0.35)continue; if(e.closest('.pg'))continue; R.push([x0,y0,x1,y1]);}
 let charts=[...s.querySelectorAll('g[data-name="axes"],img,svg g polyline')].map(e=>{const r=e.getBoundingClientRect();return [(r.left-q.left)/sc,(r.top-q.top)/sc,(r.right-q.left)/sc,(r.bottom-q.top)/sc]});
 const cb=charts.length?Math.max(...charts.map(c=>c[3])):420, cl=charts.length?Math.min(...charts.map(c=>c[0])):70;
 const free=(x,y)=>R.every(r=>x+W<=r[0]-2||x>=r[2]+2||y+H<=r[1]-2||y>=r[3]+2);
 let best=null;for(let y=100;y<=680-H;y+=4){for(let x=60;x<=1220-W;x+=10){if(!free(x,y))continue;const d=Math.abs(y-cb)+0.3*Math.abs(x-cl);if(!best||d<best[2])best=[x,y,d];}}
 return {best, chart_bottom:cb, chart_left:cl};}"""
res = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=['--disable-dev-shm-usage']); pg = b.new_page(viewport={'width': 1280, 'height': 772})
    for n, w, h in req:
        pg.goto('about:blank'); pg.goto(f + f'#s{n}'); pg.wait_for_timeout(700)
        res[n] = pg.evaluate(JS, [w, h]); print(n, res[n], flush=True)
    b.close()
json.dump(res, open(out, 'w'), indent=1)
