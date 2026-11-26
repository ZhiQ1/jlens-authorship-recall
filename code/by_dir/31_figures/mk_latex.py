# grey LaTeX-style lines rendered with matplotlib mathtext -> PNG (embedded in the SVG figures)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, sys
GREY="#8a8f98"
def render(tex, out, size=15):
    fig=plt.figure(figsize=(0.01,0.01)); fig.text(0,0,tex,fontsize=size,color=GREY,math_fontfamily="cm")
    fig.savefig(out,dpi=200,transparent=True,bbox_inches="tight",pad_inches=0.02); plt.close(fig)
if __name__=="__main__":
    render(r"$\mathrm{spec}=\mathrm{nlr}(\mathrm{true})-\frac{1}{5}\sum_{k}\mathrm{nlr}(\mathrm{false}_k),\quad \mathrm{nlr}=\log_{10}(1/\mathrm{rank})$","tex_main_f.png")
    render(r"$n=9{,}108\ \mathrm{papers\ (readouts)}\ \cdot\ 1{,}186\ \mathrm{(put\ back)}\ \cdot\ 600\ \mathrm{(route,\ MLP,\ writing)}\ \cdot\ 6{,}048\ \mathrm{(surname\ test)}$","tex_main_n.png")
    render(r"$\varphi=\sum A/\sum G,\quad R=S_{\mathrm{true}}-S_{\mathrm{made\ up}},\quad \Delta=\mathrm{rare\ swap}-\mathrm{common\ swap}$","tex_stage_f.png")
    render(r"$n=566\ \mathrm{target}+561\ \mathrm{control\ (made\ up\ title)}\ \cdot\ 9{,}108\ \mathrm{(variance\ split)}\ \cdot\ 836\ \mathrm{(rare\ words)}$","tex_stage_n.png")
