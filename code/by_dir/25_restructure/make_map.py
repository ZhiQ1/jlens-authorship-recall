# Mechanism map sketch (static SVG) for the summary section — draft 2026-11-23
toks = (["Who","·are","·the","·authors","·of","·the","·paper","·titled",'·"'] +
        ["A","ffect","·dynamics",",","·bere","av","ement","·and","·resilience","·to","·loss"] +
        ['"',"·(","2","0","0","7",")?↵","Authors",":"] + ["·Kar","in","·G",".","·Co","if"] + ["man"])
grp = [0]*9+[1]*11+[2]*9+[3]*6+[4]
CW, X0, Y0, LH = 30, 120, 150, 7.4          # column width, left margin, top of layer axis, px per layer
W = X0 + CW*len(toks) + 260; H = Y0 + 64*LH + 120
def X(i): return X0 + i*CW
def Y(l): return Y0 + (63-l)*LH            # L63 at top
C = dict(settled="#2E7D46", locked="#3C78B4", fsolid="#1F6F8B", desc="#B54708", expl="#6A7385",
         target="#3C78B4", control="#8a8f98", concl="#D9772B", ink="#22304A", grey="#8a8f98")
grpcol = ["#EEF1F5","#FFF1DE","#E8F0FA","#EAF6EC","#FBE3E1"]; grpname=["question words","title (11 tokens)","after the title (9)","name fed in (6)","scored"]
o = []; a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Patrick Hand, Comic Sans MS, sans-serif">')
a('<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#22304A"/></marker>'
  '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#3C78B4" stroke-width="2" opacity=".45"/></pattern></defs>')
a(f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>')
a(f'<text x="20" y="40" font-size="30" font-weight="700" fill="{C["ink"]}">Read early, said late: where each step happens</text>')
a(f'<text x="20" y="66" font-size="15" fill="{C["grey"]}">x: the prompt as Qwen3 tokens (real example) · y: layer L0–L63 · badges: evidence strength · ▲ intervention (replace / block / inject) · ◉ readout (lens / probe)</text>')
# group header bands + tokens
for i,(t,g) in enumerate(zip(toks,grp)):
    a(f'<rect x="{X(i)+1}" y="{Y0-46}" width="{CW-2}" height="40" rx="4" fill="{grpcol[g]}" stroke="#c9ced6"/>')
    a(f'<text x="{X(i)+CW/2}" y="{Y0-21}" font-size="10.5" text-anchor="middle" fill="{C["ink"]}" transform="rotate(-35 {X(i)+CW/2} {Y0-21})">{t.replace("<","&lt;")}</text>')
starts=[0,9,20,29,35]; ends=[9,20,29,35,36]
for g in range(5):
    a(f'<text x="{(X(starts[g])+X(ends[g]))/2}" y="{Y0-54}" font-size="12" text-anchor="middle" fill="{C["grey"]}">{grpname[g]}</text>')
# layer axis
for l in range(0,64,8):
    a(f'<line x1="{X0-6}" x2="{X(36)}" y1="{Y(l)}" y2="{Y(l)}" stroke="#e1e5ea"/>'); a(f'<text x="{X0-10}" y="{Y(l)+4}" font-size="12" text-anchor="end" fill="{C["grey"]}">L{l}</text>')
a(f'<text x="{X0-10}" y="{Y(63)+4}" font-size="12" text-anchor="end" fill="{C["grey"]}">L63</text>')
def badge(x,y,txt,col,dash=False):
    w=8+7.2*len(txt); d=' stroke-dasharray="4 3"' if dash else ''
    a(f'<rect x="{x}" y="{y-13}" width="{w}" height="18" rx="9" fill="#fff" stroke="{col}" stroke-width="1.6"{d}/><text x="{x+w/2}" y="{y+1}" font-size="12" text-anchor="middle" fill="{col}">{txt}</text>')
def step(n,x,y,col):
    a(f'<circle cx="{x}" cy="{y}" r="11" fill="{col}"/><text x="{x}" y="{y+5}" font-size="14" font-weight="700" text-anchor="middle" fill="#fff">{n}</text>')
# ① question read until late at ':'
a(f'<rect x="{X(0)}" y="{Y(56)}" width="{CW*9}" height="{Y(0)-Y(56)}" fill="#EEF1F5" opacity=".7"/>')
a(f'<path d="M{X(8)+CW} {Y(30)} C {X(14)} {Y(36)}, {X(22)} {Y(40)}, {X(28)+CW/2} {Y(52)}" fill="none" stroke="{C["locked"]}" stroke-width="2.4" marker-end="url(#ar)"/>')
a(f'<rect x="{X(28)+3}" y="{Y(56)}" width="{CW-6}" height="{Y(0)-Y(56)}" fill="none" stroke="{C["locked"]}" stroke-width="2" stroke-dasharray="5 3"/>')
step(1,X(4),Y(58),C["locked"]); badge(X(0),Y(61)+2,"locked L56 = likely sink artefact",C["expl"],True)
a(f'<text x="{X(0)+4}" y="{Y(46)}" font-size="13" fill="{C["ink"]}">question read</text><text x="{X(0)+4}" y="{Y(43)}" font-size="13" fill="{C["ink"]}">at “:” (format layer</text><text x="{X(0)+4}" y="{Y(40)}" font-size="13" fill="{C["ink"]}">not pinned down) ▲</text>')
# ② title read L24–L52
a(f'<rect x="{X(9)}" y="{Y(52)}" width="{CW*11}" height="{Y(24)-Y(52)}" fill="#FFE2B8" opacity=".85" stroke="{C["concl"]}" stroke-width="1.5"/>')
step(2,X(9)+14,Y(54),C["settled"]); badge(X(9)+30,Y(54)+4,"settled ▲",C["settled"])
a(f'<text x="{X(10)}" y="{Y(44)}" font-size="13" fill="{C["ink"]}">title read L24 → done by L52</text>')
# ③ what is read
step(3,X(9)+14,Y(20),C["locked"]); a(f'<text x="{X(10)+4}" y="{Y(19)}" font-size="13" fill="{C["ink"]}">meaning + specific words, not identity</text>'); badge(X(10),Y(15),"locked ▲◉ · identity: weakened",C["locked"])
# ④ delivery title -> name positions L40–L50
a(f'<rect x="{X(20)}" y="{Y(50)}" width="{CW*16}" height="{Y(40)-Y(50)}" fill="#DCEAF7" opacity=".7"/>')
a(f'<path d="M{X(19)+CW} {Y(46)} C {X(24)} {Y(52)}, {X(30)} {Y(50)}, {X(31)} {Y(47)}" fill="none" stroke="{C["fsolid"]}" stroke-width="3" marker-end="url(#ar)"/>')
step(4,X(24),Y(54),C["fsolid"]); badge(X(25)-6,Y(54)+4,"fairly solid ▲",C["fsolid"])
a(f'<text x="{X(21)}" y="{Y(36)}" font-size="13" fill="{C["ink"]}">arrives at the names L40–L50;</text><text x="{X(21)}" y="{Y(33)}" font-size="13" fill="{C["ink"]}">name ← title edge (not the only route)</text>')
# ⑤ held, not in vocabulary directions
a(f'<rect x="{X(29)}" y="{Y(56)}" width="{CW*7}" height="{Y(40)-Y(56)}" fill="url(#hatch)" stroke="{C["locked"]}" stroke-width="1.2"/>')
step(5,X(36)+16,Y(46),C["locked"]); a(f'<text x="{X(36)+32}" y="{Y(47)}" font-size="13" fill="{C["ink"]}">author info held, but not</text><text x="{X(36)+32}" y="{Y(44)}" font-size="13" fill="{C["ink"]}">in vocabulary directions</text>'); badge(X(36)+32,Y(40),"locked ◉ (correlational)",C["locked"])
# ⑥ written L57–L61 by MLPs
a(f'<rect x="{X(29)}" y="{Y(61)}" width="{CW*7}" height="{Y(57)-Y(61)}" fill="{C["concl"]}" opacity=".9"/>')
step(6,X(36)+16,Y(55),C["settled"]); a(f'<text x="{X(36)+32}" y="{Y(55)+4}" font-size="13" fill="{C["ink"]}">MLPs write the name, L57–L61</text>'); badge(X(36)+32,Y(52),"settled ▲",C["settled"])
# target vs control differ only at the output
a(f'<rect x="{X(29)}" y="{Y(63)-4}" width="{CW*3.5}" height="10" fill="{C["target"]}"/><rect x="{X(29)+CW*3.5}" y="{Y(63)-4}" width="{CW*3.5}" height="10" fill="{C["control"]}"/>')
a(f'<text x="{X(29)-6}" y="{Y(63)+5}" font-size="13" text-anchor="end" fill="{C["ink"]}">◉ lens: target ≠ control from ~L50, most at the output →</text>')
for (xx,ll,lab) in [(X(19)+CW/2,24,"◉ probe T≠C (title, L24)"),(X(31),40,"◉ probe T≠C"),(X(31),48,"◉ probe T≠C")]:
    a(f'<circle cx="{xx}" cy="{Y(ll)}" r="7" fill="#fff" stroke="{C["target"]}" stroke-width="2.4"/><circle cx="{xx}" cy="{Y(ll)}" r="3" fill="{C["target"]}"/>')
    a(f'<text x="{xx+10}" y="{Y(ll)-6}" font-size="11.5" fill="{C["target"]}">{lab}</text>')
a(f'<path d="M{X(28)+CW/2} {Y(56)} C {X(28)+CW/2} {Y(60)}, {X(29)} {Y(60)}, {X(29)+6} {Y(59)}" fill="none" stroke="{C["locked"]}" stroke-width="2" stroke-dasharray="4 3" marker-end="url(#ar)"/>')
a(f'<text x="{X(20)}" y="{Y(58)+2}" font-size="12" fill="{C["locked"]}">①→⑥ format gates the author signal at L56 (locked)</text>')
# ⑦ stuck at writing the first token
a(f'<rect x="{X(35)+2}" y="{Y(63)-4}" width="{CW-4}" height="{Y(56)-Y(63)+4}" fill="#FBE3E1" stroke="#C84A3E" stroke-width="2"/>')
a(f'<text x="{X(35)+CW/2}" y="{Y(60)+6}" font-size="22" font-weight="700" text-anchor="middle" fill="#C84A3E">✕</text>')
step(7,X(36)+16,Y(63)+2,"#C84A3E"); a(f'<text x="{X(36)+32}" y="{Y(63)+6}" font-size="13" fill="{C["ink"]}">stalls at writing the name (first token);</text><text x="{X(36)+32}" y="{Y(61)+6}" font-size="13" fill="{C["ink"]}">a stronger arrived signal does not help</text>')
badge(X(36)+32,Y(58)+8,"locked ▲ + exploratory",C["locked"])
# legend
ly=H-70
for k,(lab,col,dash) in enumerate([("settled",C["settled"],0),("locked",C["locked"],0),("fairly solid",C["fsolid"],0),("descriptive",C["desc"],0),("exploratory",C["expl"],0),("pending",C["expl"],1)]):
    badge(20+k*140,ly,lab,col,bool(dash))
a(f'<text x="20" y="{ly+34}" font-size="13" fill="{C["grey"]}">Step 1: the locked rule gives L56; supplementary checks (exploratory): the dip appears only when the attention sink is cut. Running: X4 surname test (step 3). Probes see target ≠ control early, lenses only late.</text>')
a('</svg>')
open('/home/zhang.zhiqi2/jlens_work/25_restructure/mechanism_map.svg','w').write('\n'.join(o)); print('ok',W,H)
