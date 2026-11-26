import sys, fitz
d = fitz.open(sys.argv[1])
print('pages', len(d))
for p in [int(x) for x in sys.argv[2].split(',')]:
    d[p-1].get_pixmap(dpi=110).save(f'/home/zhang.zhiqi2/jlens_work/34_v75/lo/p{p}.png')
