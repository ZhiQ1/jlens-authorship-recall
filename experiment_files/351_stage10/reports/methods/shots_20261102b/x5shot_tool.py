from playwright.sync_api import sync_playwright
H='/scratch/zhang.zhiqi2/jlens/351_stage10/reports/methods/methods_handbook.html'
O='/scratch/zhang.zhiqi2/jlens/351_stage10/reports/methods/shots_20261102b/'
src=open(H).read()
doc='<!doctype html><html lang="zh"><head><meta charset="utf-8">'+src.split('<div class="wrap">',1)[0]+'</head><body><div class="wrap">'+src.split('<div class="wrap">',1)[1]+'</body></html>'
open(O+'_wrapped.html','w').write(doc)
with sync_playwright() as p:
    b=p.chromium.launch()
    for w in (1100,390):
        pg=b.new_page(viewport={'width':w,'height':900})
        pg.goto('file://'+O+'_wrapped.html'); pg.wait_for_timeout(1500)
        sw=pg.evaluate('document.documentElement.scrollWidth')
        box=pg.evaluate('''()=>{const a=document.getElementById('s13-x5').getBoundingClientRect();const b=document.getElementById('s13-x6').getBoundingClientRect();return [a.top+scrollY-10,b.top+scrollY]}''')
        print(w,'scrollWidth',sw)
        k=0;y=box[0]
        while y<box[1]:
            hh=min(2400,box[1]-y)
            pg.screenshot(path=f'{O}x5_{w}_{k}.png',clip={'x':0,'y':y,'width':w,'height':hh},full_page=True)
            y+=hh;k+=1
        print('chunks',k)
    b.close()
