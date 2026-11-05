#!/usr/bin/env python
"""Stage 13 X5 "layer order", VERSION 2 (2026-11-05, V56): v1 (stage13_x5_layer_order.py, outputs without _v2) is kept
untouched; v2 adds the pre-registered row "paper identity retrievable across tasks (M3, top-1 retrieval)" from
summary_x5/x5_retrieval.csv (stage13_v56_retrieval.py). Everything else is the v1 code.

Stage 13 X5 "layer order": summarise, from EXISTING results only, the earliest
layer at which each kind of information appears (prereg.json X5; addenda 1-5).

CPU only, reads CSVs, no model runs. Each source keeps its own rule
("first layer whose interval excludes 0" or the source's pre-registered
threshold). Grids differ by source; when the first measured layer already
passes, the earliest layer is reported as "<= L<first>".

Outputs (never overwritten; a timestamp suffix is added if a file exists):
  381_stage13/summary_x5/x5_layer_order.csv
  381_stage13/reports/x5_layer_order.png / .svg
  381_stage13/reports/x5_report.md
"""
import os, sys, json, time
import numpy as np
import pandas as pd

R10 = "/scratch/zhang.zhiqi2/jlens/351_stage10"
R12 = "/scratch/zhang.zhiqi2/jlens/371_stage12"
R13 = "/scratch/zhang.zhiqi2/jlens/381_stage13"
OROOT = os.environ.get("X5_OUT_ROOT", R13)  # test runs: point at a scratch dir
OUT_CSV = f"{OROOT}/summary_x5/x5_layer_order_v2.csv"
OUT_PNG = f"{OROOT}/reports/x5_layer_order_v2.png"
OUT_SVG = f"{OROOT}/reports/x5_layer_order_v2.svg"
OUT_MD = f"{OROOT}/reports/x5_report_v2.md"

F = dict(
    m2=f"{R13}/summary_cpu_teamci/M2_teamci.csv",
    m2c=f"{R13}/summary_cpu_group/M2c_bert_baseline.csv",
    e4b_all=f"{R13}/summary_cpu_trainstd/compare_E4b_allpapers.csv",
    e4b=f"{R13}/summary_cpu_trainstd/E4b_4configs.csv",
    x4=f"{R13}/summary_x1x4/x4_decodability.csv",
    x4e=f"{R13}/summary_x1x4/x4_earliest.csv",
    x3=f"{R13}/summary_x3/x3_gap.csv",
    x3v=f"{R13}/summary_x3/x3_identity_verdict.csv",
    m3=f"{R13}/summary_m3/m3_identity.csv",
    m3v=f"{R13}/summary_m3/m3_verdict_addendum2.csv",
    s10=f"{R13}/summary_cpu_group/cluster_ci_all.csv",
    f2=f"{R12}/summary/F2_author_lens.csv",
    x6=f"{R13}/summary_x6/x6_recovery.csv",
    x7=f"{R13}/summary_x7/x7_knockout.csv",
    ret=f"{R13}/summary_x5/x5_retrieval.csv",
    rete=f"{R13}/summary_x5/x5_retrieval_earliest.csv",
)
WARN = []


def safe_path(p):
    if not os.path.exists(p):
        return p
    b, e = os.path.splitext(p)
    q = f"{b}.{time.strftime('%Y%m%d_%H%M%S')}{e}"
    WARN.append(f"{p} exists; wrote {q} instead (no overwrite)")
    return q


def L(x):
    return f"L{int(x)}"


def ci(v, lo, hi, d=3):
    if lo is None or (isinstance(lo, float) and np.isnan(lo)):
        return f"{v:+.{d}f}"
    return f"{v:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]"


def grid_str(layers):
    ls = sorted(int(x) for x in layers)
    return ",".join(str(x) for x in ls)


def earliest(layers, passes, first_label=True):
    """first measured layer that passes; '<= Lx' if it is the first measured."""
    ls = list(layers)
    for i, (l, p) in enumerate(zip(ls, passes)):
        if p:
            return l, (f"<= L{l}" if (i == 0 and first_label) else f"L{l}")
    return None, "none"


def sustained(layers, passes):
    ls, ps = list(layers), list(passes)
    for i in range(len(ls)):
        if all(ps[i:]):
            return f"L{ls[i]}"
    return "-"


ROWS = []


def add(kind, measure, source, position, layers, passes, rule, values, src,
        stronger=None, note="", earliest_override=None, markers_strong=None,
        ci_type=""):
    """values: dict layer -> (v, lo, hi)."""
    layers = [int(x) for x in layers]
    if earliest_override is not None:
        el, es = earliest_override
    else:
        el, es = earliest(layers, passes)
    v = values.get(el) if el is not None else None
    ROWS.append(dict(
        kind=kind, measure=measure, source=source, position=position,
        grid=grid_str(layers), rule=rule,
        earliest_rule=es,
        earliest_stronger=(stronger or "n/a"),
        sustained_from=sustained(layers, passes),
        value_at_earliest=(ci(*v) + (f" ({ci_type})" if ci_type else "")) if v else "-",
        note=note, source_file=src,
        _layers=layers, _passes=list(map(bool, passes)), _el=el,
        _strong=markers_strong or [],
    ))


# ---------------- title-position probes (M2, team CI) -------------------------
m2 = pd.read_csv(F["m2"])
m2 = m2[(m2.condition == "true") & (m2.position == "title")]
bert = pd.read_csv(F["m2c"]).groupby("target").value.max()
for tgt, lab, met in [("year", "year (R2)", "r2"),
                      ("log citations", "log citations (R2)", "r2"),
                      ("field", "field (accuracy)", "acc")]:
    d = m2[m2.target == tgt].sort_values("layer")
    passes = (d.lo_team > d.null).values
    vals = {int(r.layer): (r.value_new, r.lo_team, r.hi_team) for r in d.itertuples()}
    strong, sm = None, []
    if tgt in bert.index:
        b = bert[tgt]
        sp = (d.value_new - b >= 0.10).values
        sl, ss = earliest(d.layer, sp)
        strong = (f"{ss} (Qwen - best BERT layer >= 0.10; BERT best {b:.3f}; "
                  "reference only, addendum 2)")
        if sl is not None:
            sm = [(sl, "")]
    rule = ("first layer with team-cluster CI above " +
            ("0" if met == "r2" else "the shuffled-label null (%.3f)" % d.null.iloc[0]))
    add("Title-position readouts", f"M2 probe: {lab}", "Stage 13 M2 (team CI)",
        "last title token", d.layer, passes, rule, vals, F["m2"],
        stronger=strong, markers_strong=sm, ci_type="team",
        note="grid starts at L16; title-text BERT baseline (M2c) shown as reference only")

# ---------------- X4 patchscope year / field (title) ---------------------------
x4 = pd.read_csv(F["x4"])
x4e = pd.read_csv(F["x4e"])


def x4row(ans, pos, kind, lab):
    t = x4[(x4.answer == ans) & (x4.pos == pos) & (x4.split == "tune")].sort_values("layer")
    s = x4[(x4.answer == ans) & (x4.pos == pos) & (x4.split == "test")].sort_values("layer")
    passes = ((t.lo.values > 0) & (s.lo.values > 0))
    vals = {int(r.layer): (r.D, r.lo, r.hi) for r in s.itertuples()}
    e = x4e[(x4e.answer == ans) & (x4e.pos == pos)].iloc[0]
    if np.isnan(e.earliest_tune):
        eo, note = (None, "none on tune"), "no layer with D's CI above 0 on tune"
    else:
        el = int(e.earliest_tune)
        first = int(t.layer.min())
        lab_e = (f"<= L{el}" if el == first else f"L{el}")
        if bool(e.confirmed_on_test):
            eo, note = (el, lab_e), "chosen on tune, confirmed on test"
        else:
            eo = (None, f"{lab_e} on tune, NOT confirmed on test")
            note = (f"tune L{el}; test D {e.D_test:+.3f} [{e.lo_test:+.3f}, {e.hi_test:+.3f}]")
    add(kind, f"X4 patchscope: {lab}", "Stage 13 X4", pos.replace("title", "title (last token)"),
        t.layer, passes, "first layer with D CI > 0 on tune, confirmed on test (prereg X4)",
        vals, F["x4e"], earliest_override=eo, ci_type="team, test",
        note=note + "; bar = layers with CI > 0 on both tune and test")


x4row("year", "title", "Title-position readouts", "year")
x4row("field", "title", "Title-position readouts", "field")

# ---------------- paraphrase / identity (X3, M3) -------------------------------
x3 = pd.read_csv(F["x3"])
x3v = pd.read_csv(F["x3v"])
for pos in ["title_last", "colon"]:
    q = x3[(x3.set == "primary") & (x3.subset == "all") & (x3.comparison == "lex") &
           (x3.pos == pos) & (x3.layer > 4)]
    t = q[q.split == "tune"].sort_values("layer")
    s = q[q.split == "test"].sort_values("layer")
    passes = (t.dL4_lo.values > 0) & (t.lo.values > 0) & (s.dL4_lo.values > 0) & (s.lo.values > 0)
    vals = {int(r.layer): (r.gap_minus_L4, r.dL4_lo, r.dL4_hi) for r in s.itertuples()}
    vp = x3v[(x3v.set == "primary") & (x3v.subset == "all") & (x3v.comparison == "lex") & (x3v.pos == pos)].iloc[0]
    vs = x3v[(x3v.set == "sensitivity") & (x3v.subset == "all") & (x3v.comparison == "lex") & (x3v.pos == pos)].iloc[0]
    el = int(vp.layer_tune)
    eo = (el, (f"<= L{el}" if el == 8 else f"L{el}") + (" (confirmed)" if vp.confirmed else " (not confirmed)"))
    sl = int(vs.layer_tune)
    add("Paraphrase / paper identity", "X3 paraphrase identity G' - G'(L4)", "Stage 13 X3 (primary set)",
        pos.replace("title_last", "last title token"), t.layer, passes,
        "first layer with G' > 0 and G' - G'(L4) > 0 (team CI) on tune, confirmed on test (addendum 4)",
        vals, F["x3v"], earliest_override=eo, ci_type="team, test",
        stronger=f"sensitivity set (addendum 5): L{sl}" + (" -> not robust" if sl != el else ""),
        markers_strong=[(sl, "")] if sl != el else [],
        note="L4 is the reference, first testable layer L8; cannot separate meaning from paper identity; bar = tune and test both pass")

m3 = pd.read_csv(F["m3"])
m3v = pd.read_csv(F["m3v"])
for pos in ["title_last", "colon"]:
    d = m3[(m3.pos == pos) & (m3.layer > 4)].sort_values("layer")
    passes = (d.d_lo.values > 0)
    vals = {int(r.layer): (r.I_minus_L4, r.d_lo, r.d_hi) for r in d.itertuples()}
    mx = d.loc[d.I_minus_L4.idxmax()]
    add("Paraphrase / paper identity", "M3 identity index I - I(L4) (never above L4)", "Stage 13 M3",
        pos.replace("title_last", "last title token"), d.layer, passes,
        "first layer with I(l) - I(L4) CI above 0 (addendum 2); top-1 retrieval: see the V56 row",
        vals, F["m3v"], ci_type="team",
        note=f"never above L4 (max I - I(L4) = {mx.I_minus_L4:+.3f} at L{int(mx.layer)}); M3 does not support H2")

# ---------------- V56: pre-registered cross-task top-1 retrieval (M3 cache) -----
ret = pd.read_csv(F["ret"])
rete = pd.read_csv(F["rete"])
for pos in ["title_last", "colon"]:
    t = ret[(ret.set == "tune") & (ret.pos == pos) & (ret.layer > 4)].sort_values("layer")
    s = ret[(ret.set == "test") & (ret.pos == pos) & (ret.layer > 4)].sort_values("layer")
    a = ret[(ret.set == "all") & (ret.pos == pos)].sort_values("layer")
    passes = (t.dL4_lo_team.values > 0) & (s.dL4_lo_team.values > 0)
    vals = {int(r.layer): (r.top1_minus_L4, r.dL4_lo_team, r.dL4_hi_team) for r in s.itertuples()}
    e = rete[rete.pos == pos].iloc[0]
    if pd.isna(e.earliest_tune):
        eo = (None, "none on tune")
    else:
        el = int(e.earliest_tune)
        eo = (el, f"L{el}") if bool(e.confirmed_on_test) else (None, f"L{el} on tune, NOT confirmed on test")
    l4 = a[a.layer == 4].iloc[0]
    mn = a.loc[a.top1.idxmin()]
    add("Paraphrase / paper identity", "M3 top-1 cross-task retrieval - L4 (prereg X5 curve)", "Stage 13 V56 (M3 cache)",
        pos.replace("title_last", "last title token"), t.layer, passes,
        "first layer with retrieval(l) - retrieval(L4) team CI > 0 on tune, confirmed on test (addendum 2 logic)",
        vals, F["rete"], earliest_override=eo, ci_type="team, test",
        note=(f"all 9,108 papers: top-1 at L4 {l4.top1:.4f} (chance {l4.chance:.5f}); lowest {mn.top1:.4f} at L{int(mn.layer)}; "
              "retrieval is at or near ceiling at L4 from the identical title tokens, so it cannot rise above L4"))

# ---------------- author readouts ---------------------------------------------
ea = pd.read_csv(F["e4b_all"])
ea = ea[(ea.split == "group") & (ea["excl"] == "title-reuse")].sort_values("layer")


def parse_ci(s):
    a, b = s.strip("[]").split(",")
    return float(a), float(b)


lohi = [parse_ci(s) for s in ea.spec_all_new_ci]
passes = np.array([lo > 0 for lo, _ in lohi])
vals = {int(l): (v, lo, hi) for l, v, (lo, hi) in zip(ea.layer, ea.spec_all_new, lohi)}
e4 = pd.read_csv(F["e4b"])
e4 = e4[(e4.split == "group") & (e4["excl"] == "title-reuse")].sort_values("layer")
sl, ss = earliest(e4.layer, (e4.tc_pooled_lo > 0).values)
r = e4[e4.layer == sl].iloc[0]
add("Author readouts", "E4b probe: first-author token, title-specific", "Stage 11 E4b, trainstd rerun",
    "title position", ea.layer, passes,
    "first layer with all-paper title-specific signal CI > 0 (confirmatory: team folds + title-reuse dropped)",
    vals, F["e4b_all"], ci_type="paper bootstrap",
    stronger=f"{ss}: target - control within bin > 0, {ci(r.tc_pooled, r.tc_pooled_lo, r.tc_pooled_hi)}",
    markers_strong=[(sl, "")], note="grid starts at L16")

x4row("author", "title", "Author readouts", "first author")
x4row("author", "colon", "Author readouts", "first author")

s10 = pd.read_csv(F["s10"])
for tab, ro, lab in [("6.3 title-specific mean, target", "logit", "Stage 10 logit lens: name, target papers"),
                     ("6.4 title-specific target-control", "logit", "Stage 10 logit lens: name, target - control"),
                     ("6.4 title-specific target-control", "jlens_public", "Stage 10 public J-lens: name, target - control")]:
    d = s10[(s10.table == tab) & (s10.readout == ro)].sort_values("layer")
    passes = (d.lo_team > 0).values
    vals = {int(r.layer): (r.est, r.lo_team, r.hi_team) for r in d.itertuples()}
    sp = (d.est >= 0.05).values
    sl, ss = earliest(d.layer, sp)
    add("Author readouts", lab, "Stage 10 (team CI, Stage 13 cluster_ci)", "author-name tokens",
        d.layer, passes, "first layer with title-specific log10(1/rank) team CI > 0",
        vals, F["s10"], ci_type="team",
        stronger=f"{ss} (estimate >= 0.05, the Stage 10 'about 0' bound)",
        markers_strong=[(sl, "")] if sl is not None else [],
        note="prereg H2 placed name-by-lens at L57-61; grid L24,32,40,48,50-62")

f2 = pd.read_csv(F["f2"])
for pos in ["name", "title"]:
    d = f2[f2.position == pos].sort_values("layer")
    passes = (d.tc_lo > 0).values
    vals = {int(r.layer): (r.tc, r.tc_lo, r.tc_hi) for r in d.itertuples()}
    add("Author readouts", f"Stage 12 F2 author-prompt lens: {pos}, target - control",
        "Stage 12 F2", "author-name tokens" if pos == "name" else "title position",
        d.layer, passes, "first layer with target - control CI > 0",
        vals, F["f2"], ci_type="Stage 12 bootstrap",
        note=("negative at L32, L44-52" if pos == "name" else "only L56 passes (lower bound +0.0004)"))

# ---------------- causal patching (X6) ----------------------------------------
x6 = pd.read_csv(F["x6"])
d = x6[(x6.group == "all") & (x6.false_title == "average")].sort_values("layer")
d = d[d.layer < 63]  # L63 is the exact-recovery check (R = 1 by construction)
passes = (d.lo > 0).values
vals = {int(r.layer): (r.R, r.lo, r.hi) for r in d.itertuples()}
s5, t5 = earliest(d.layer, (d.R >= 0.5).values)
s95, t95 = earliest(d.layer, (d.R >= 0.95).values)
tg = x6[(x6.group == "target") & (x6.false_title == "average")]
ct = x6[(x6.group == "control") & (x6.false_title == "average")]
f95 = lambda g: L(g[g.R >= 0.95].layer.min())
f50 = lambda g: L(g[g.R >= 0.5].layer.min())
add("Causal patching", "X6 tail patching: recovery R (avg 5 false titles)", "Stage 13 X6 (Stage 11 E1)",
    "post-title tail", d.layer, passes, "first layer with R team CI > 0",
    vals, F["x6"], ci_type="team",
    stronger=f"{t5} (R >= 0.5, {vals[s5][0]:.3f}); {t95} (R >= 0.95, {vals[s95][0]:.3f})",
    markers_strong=[(s5, "0.5"), (s95, "0.95")],
    note=f"target / control: R>=0.5 at {f50(tg)} / {f50(ct)}, R>=0.95 at {f95(tg)} / {f95(ct)}; grid starts at L24; L63 (=1 by construction) left out")

# ---------------- knockout (X7) ------------------------------------------------
x7 = pd.read_csv(F["x7"])
d = x7[x7.group == "all"].sort_values("start_layer")
passes = (d.S_lo > 0).values
vals = {int(r.start_layer): (r.S, r.S_lo, r.S_hi) for r in d.itertuples()}
last = int(d[d.S_lo > 0].start_layer.max())
sl, ss = earliest(d.start_layer, (d.S <= 0.05).values)
lt = lambda g: L(x7[(x7.group == g) & (x7.S_lo > 0)].start_layer.max())
st = lambda g: L(x7[(x7.group == g) & (x7.S <= 0.05)].start_layer.min())
add("Knockout", "X7 knockout: paper-specific loss S(l), block title from l", "Stage 13 X7 (Stage 11 E2)",
    "post-title tail -> title", d.start_layer, passes,
    "LAST block-from layer with S team CI > 0 (title still needed up to here)",
    vals, F["x7"], earliest_override=(last, f"L{last} (last with S > 0)"), ci_type="team",
    stronger=f"{ss} (first S <= 0.05, {vals[sl][0]:+.3f})", markers_strong=[(sl, "")],
    note=f"target / control: last S > 0 at {lt('target')} / {lt('control')}, S <= 0.05 from {st('target')} / {st('control')}")

# ---------------- table -------------------------------------------------------
tab = pd.DataFrame(ROWS)
cols = ["kind", "measure", "source", "position", "grid", "rule", "earliest_rule",
        "earliest_stronger", "sustained_from", "value_at_earliest", "note", "source_file"]
os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
p_csv = safe_path(OUT_CSV)
tab[cols].to_csv(p_csv, index=False)
print("wrote", p_csv)

# ---------------- figure ------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

COL = {"Title-position readouts": "#2a78d6", "Paraphrase / paper identity": "#e87ba4",
       "Author readouts": "#eb6834", "Causal patching": "#1baf7a", "Knockout": "#c98500"}
INK, MUTED, GRID = "#1f1f1e", "#5f5e58", "#d9d8d2"
SHORT = {
    "M2 probe: year (R2)": "M2 probe: year",
    "M2 probe: log citations (R2)": "M2 probe: log citations",
    "M2 probe: field (accuracy)": "M2 probe: field",
    "M3 top-1 cross-task retrieval - L4 (prereg X5 curve)": "M3 top-1 retrieval − L4 (prereg)",
    "M3 identity index I - I(L4) (never above L4)": "M3 identity index I − I(L4)",
}
order = ["Title-position readouts", "Paraphrase / paper identity", "Author readouts",
         "Causal patching", "Knockout"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13})
fig = plt.figure(figsize=(16, 9), dpi=120, facecolor="#fbfbf9")
ax = fig.add_axes([0.30, 0.10, 0.60, 0.80], facecolor="#fbfbf9")
y, yt, ylab, heads = 0, [], [], []
for k in order:
    sub = [r for r in ROWS if r["kind"] == k]
    heads.append((y, k))
    y += 1
    for r in sub:
        c = COL[k]
        ls, ps = r["_layers"], r["_passes"]
        ax.plot([min(ls), max(ls)], [y, y], color=GRID, lw=1.2, zorder=1)
        ax.scatter(ls, [y] * len(ls), s=10, color="#a8a79f", zorder=2, lw=0)
        # bars over runs of consecutive passing measured layers
        i = 0
        while i < len(ls):
            if ps[i]:
                j = i
                while j + 1 < len(ls) and ps[j + 1]:
                    j += 1
                a, b = ls[i] - 0.5, ls[j] + 0.5
                ax.plot([a, b], [y, y], color=c, lw=7, alpha=0.45, solid_capstyle="round", zorder=3)
                i = j + 1
            else:
                i += 1
        el = r["_el"]
        strong = [(sl, t) for (sl, t) in r["_strong"] if sl != el]
        for k2, (sl, t) in enumerate(strong):
            ax.scatter([sl], [y], s=110, facecolor="white", edgecolor=c, lw=2.2, zorder=4, marker="D")
            ha = "center"
            if len(strong) > 1:
                ha = "right" if k2 == 0 else "left"
            ax.annotate(f"L{sl}" + (f" R\u2265{t}" if t else ""), (sl, y), xytext=(0, 8),
                        textcoords="offset points", ha=ha, va="bottom", fontsize=10, color=MUTED, zorder=6)
        if el is not None:
            ax.scatter([el], [y], s=120, color=c, edgecolor="white", lw=1.5, zorder=5, marker="o")
            lab = r["earliest_rule"].replace("<= ", "\u2264").split(" (")[0]
            right = any(el - 7 <= sl < el for sl, _ in strong)
            ax.annotate(lab, (el, y), xytext=((11, 0) if right else (-11, 0)), textcoords="offset points",
                        ha=("left" if right else "right"), va="center", fontsize=11, color=INK,
                        fontweight="bold", zorder=6)
        else:
            ax.text(max(ls) + 1.0, y, "none confirmed" if "NOT confirmed" in r["earliest_rule"] else "none",
                    va="center", fontsize=11, color=MUTED, style="italic")
        name = SHORT.get(r["measure"], r["measure"])
        name = name.replace(": recovery R (avg 5 false titles)", ": recovery R")
        name = name.replace(": paper-specific loss S(l), block title from l", ": title still needed (S>0)")
        name = name.replace(", target - control", ", tgt−ctl").replace(" - control", "−ctl")
        name = name.replace("target papers", "target").replace("first-author token, title-specific", "first author")
        pos = {"last title token": "title", "title (last token)": "title", "title position": "title",
               "author-name tokens": "names", "post-title tail": "tail",
               "post-title tail -> title": "tail→title"}.get(r["position"], r["position"])
        if pos not in name:
            name = f"{name}  [{pos}]"
        yt.append(y); ylab.append(name)
        y += 1
    y += 0.4
ax.axvspan(56.5, 61.5, color="#ecebe6", zorder=0)
ax.text(59, -0.9, "H2-predicted\nname-by-lens L57–61", ha="center", va="bottom", fontsize=10, color=MUTED)
ax.set_yticks(yt)
ax.set_yticklabels(ylab, fontsize=12, color=INK)
for (yy, k) in heads:
    ax.text(-0.5, yy, k.upper(), transform=ax.get_yaxis_transform(), ha="left", va="center",
            fontsize=12, fontweight="bold", color=COL[k])
    ax.text(-0.505, yy, "■", transform=ax.get_yaxis_transform(), ha="right", va="center",
            fontsize=12, color=COL[k])
ax.set_ylim(y - 0.2, -1.3)
ax.set_xlim(-1, 64)
ax.set_xticks(range(0, 65, 8))
ax.set_xlabel("Layer (Qwen3-32B, 0–63)", fontsize=13, color=INK)
ax.tick_params(axis="y", length=0)
ax.tick_params(axis="x", colors=MUTED)
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
fig.text(0.03, 0.955, "Stage 13 X5 (v2): earliest layer at which each kind of information appears",
         fontsize=19, fontweight="bold", color=INK)
fig.text(0.03, 0.925, "Existing results only; each source keeps its own rule. Grids differ by source "
         "(grey dots = measured layers); ≤Lx = already present at the first measured layer.",
         fontsize=12, color=MUTED)
leg = [Line2D([], [], marker="o", ls="", color="#5f5e58", markeredgecolor="white", markersize=11,
              label="earliest layer (source rule; X7: last layer)"),
       Line2D([], [], marker="D", ls="", markerfacecolor="white", markeredgecolor="#5f5e58", mew=2,
              markersize=9, label="stronger threshold / sensitivity"),
       Line2D([], [], color="#5f5e58", lw=7, alpha=0.45, label="measured layers where the rule passes"),
       Line2D([], [], marker="o", ls="", color="#a8a79f", markersize=4, label="measured layer")]
fig.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.03, 0.005), ncol=4, frameon=False, fontsize=11)
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
p_png, p_svg = safe_path(OUT_PNG), safe_path(OUT_SVG)
fig.savefig(p_png, dpi=120, facecolor=fig.get_facecolor())
fig.savefig(p_svg, facecolor=fig.get_facecolor())
print("wrote", p_png, p_svg)

# ---------------- report ------------------------------------------------------
def md_table(df):
    h = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
    return h + "\n".join("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |" for r in df.values)


show = tab[["kind", "measure", "position", "grid", "earliest_rule", "earliest_stronger",
            "sustained_from", "value_at_earliest"]].copy()
show.columns = ["kind", "measure", "position", "grid (layers)", "earliest (rule)",
                "stronger threshold", "passes at every later layer from", "value at earliest [95% CI]"]
md = f"""# Stage 13 X5: layer order (existing results only), version 2

Version 2 (2026-11-05): adds the pre-registered "paper identity retrievable across tasks" row (M3 cache, cross-task top-1 retrieval, V56; details `reports/x5_retrieval.md`). v1 files (`x5_report.md`, `x5_layer_order.png/.svg/.csv`) are unchanged.
Script `~/jlens_work/13_stage13/stage13_x5_layer_order_v2.py`, run {time.strftime('%Y-%m-%d %H:%M')}. CPU only; no model runs.
Definition: prereg.json X5 ("for each layer: paper identity retrievable across tasks (M3, top-1 retrieval among the test papers), first-author token by probe (M2/E4b), name by lens (Stage 10)"); rules per source as in prereg.json and addenda 1-5.
Each source keeps its own rule: first layer whose interval excludes 0 (or above the null / the pre-registered threshold). Grids differ by source; "<= Lx" means the first measured layer already passes.
Table: `summary_x5/x5_layer_order_v2.csv` (with rule, note and source file per row). Figure: `reports/x5_layer_order_v2.png` / `.svg`.

![X5 layer order](x5_layer_order_v2.png)

{md_table(show)}

## Notes per row

{chr(10).join(f"- **{r['measure']}** [{r['position']}]: rule = {r['rule']}. {r['note']}. Source `{r['source_file']}`." for r in ROWS)}

## Summary of the order

- At the last title token, year, log citations and field are probe-decodable at the first measured layer (<= L16, M2), and the first-author token is decodable by patchscope at <= L8 (X4) and by probe at <= L16 (E4b); the patchscope year appears at L40 and the patchscope field is never confirmed.
- Paraphrase identity (X3 G' - G'(L4)) appears at <= L8 in the primary set but at L24 in the sensitivity set (not robust). The M3 identity index never rises above its L4 level, and the pre-registered cross-task top-1 retrieval (V56) is {{RET_SUMMARY}}; so M3 gives no identity layer.
- Causally, patching the post-title tail recovers > 0 from <= L24, half the gap by L48 and >= 0.95 by L52 (X6); blocking the title stops costing paper-specific signal from L52 (S <= 0.05), with the last significant loss at L54 (X7).
- At the name positions the lens signal passes the CI rule already at L24 but stays tiny (< 0.01) until L50; it exceeds 0.05 at L53 (logit, target) and target - control exceeds 0.05 at L56 (logit) / L58 (public J-lens); the author-prompt lens (F2) shows target - control > 0 only at L62.
- Order (by the stronger thresholds): title-position facts and author token (<= L8-L16) -> tail carries the paper signal (L48-L52) -> name-position lens readout (L53-L62).

## Caveats

- M3 does not support H2: neither the transfer ratio, the identity index nor the cross-task top-1 retrieval is above the L4 text level at the title; X5's "identity first" leg therefore has no M3 layer. Retrieval at the title is at ceiling already at L4 (identical title tokens), so "above L4" is impossible for it there; this is a limit of the measure, not evidence against identity.
- X3 cannot separate meaning from paper identity (a paraphrase keeps the meaning); its <= L8 onset is not robust (sensitivity set: L24).
- The X4 L8 first-author signal at the title may be explainable by the title text (see x4_textbase reports); X4 colon author is not confirmed on test.
- The strict "CI excludes 0" rule gives very early but tiny effects for the Stage 10 lens (L24, about 0.004-0.007); the stronger 0.05 bound is the Stage 10 "about 0" convention, not a pre-registered threshold. M2 vs BERT is a reference only (addendum 2).
- Intervals: team-cluster for M2, X3, X4, M3, Stage 10 (cluster_ci_all), X6, X7; E4b all-paper is a paper bootstrap; F2 is the Stage 12 bootstrap.
- This summary adds no conclusion beyond the ordering.
"""
if WARN:
    md += "\n## WARN\n\n" + "\n".join(f"- {w}" for w in WARN) + "\n"
_a = ret[ret.set == "all"]
RS = "; ".join(f"{p}: top-1 at L4 {_a[(_a.pos == p) & (_a.layer == 4)].top1.iloc[0]:.3f}, range {_a[_a.pos == p].top1.min():.3f}-{_a[_a.pos == p].top1.max():.3f}, earliest above L4: "
               + (f"L{int(rete[rete.pos == p].earliest_tune.iloc[0])} on tune" + (" (confirmed)" if bool(rete[rete.pos == p].confirmed_on_test.iloc[0]) else " (not confirmed)") if pd.notna(rete[rete.pos == p].earliest_tune.iloc[0]) else "none")
               for p in ["title_last", "colon"])
md = md.replace("{RET_SUMMARY}", RS)
p_md = safe_path(OUT_MD)
open(p_md, "w").write(md)
print("wrote", p_md)
for w in WARN:
    print("WARN", w)
print(tab[["measure", "position", "earliest_rule", "earliest_stronger", "sustained_from", "value_at_earliest"]].to_string())
