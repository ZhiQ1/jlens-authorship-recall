import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
deck = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html'); out = {}
SP = Path(sys.argv[1])
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 772}, device_scale_factor=2)
    pg.goto(deck.as_uri(), wait_until='networkidle', timeout=180000)
    pg.add_style_tag(content='.nav{display:none!important} .stage{box-shadow:none!important}')
    pg.evaluate("document.getElementById('stage').style.setProperty('--s', 1)")
    for k in (51, 52, 49):
        pg.evaluate(f"document.querySelectorAll('.slide').forEach((el,j)=>el.classList.toggle('on',j==={k-1}))"); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
        boxes = pg.evaluate("""(()=>{const st=document.getElementById('stage').getBoundingClientRect(); const s=document.querySelector('.slide.on'); const r={};
          const box=e=>{ // untransformed box: offset-based via clearing transform temporarily
             const t=e.style.transform; e.style.transform='none'; const b=e.getBoundingClientRect(); e.style.transform=t;
             return {x:b.left-st.left,y:b.top-st.top,w:b.width,h:b.height,tf:getComputedStyle(e).transform}};
          for (const [n,sel] of [['tag','.tag'],['h2','h2'],['sub','.sub'],['card','figure.card'],['img','figure.card img'],['cap','figcaption'],['note','.note'],['pg','.pg']]){const e=s.querySelector(sel); if(e) r[n]=box(e);}
          return r})()""")
        out[k] = boxes
        if k in (51, 52):
            pg.add_style_tag(content=f'.slide:nth-of-type({k}) > *{{visibility:hidden!important}}')
            pg.locator('#stage').screenshot(path=str(SP / f'bg_{k}.png'))
    b.close()
json.dump(out, open(SP / 'dom_boxes.json', 'w'), indent=1); print(json.dumps(out, indent=0)[:3000])
