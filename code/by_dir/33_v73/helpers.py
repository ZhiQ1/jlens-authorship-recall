def on_text(sec, fn):
    hid = []
    def keep(m): hid.append(m.group(0)); return f'\x00{len(hid)-1}\x00'
    s = re.sub(r'<svg class="tx".*?</svg>', keep, sec, flags=re.S)
    parts = re.split(r'(<[^>]+>)', s)
    s = ''.join(p if p.startswith('<') else fn(p) for p in parts)
    return re.sub(r'\x00(\d+)\x00', lambda m: hid[int(m.group(1))], s)
REF = re.compile(r'\b(slides?|Slides?)(\s+)(\d{1,3}(?:\s*(?:–|-|,|and|&amp;|&)\s*\d{1,3})*)')
def expand(spec):
    nums = []
    for p in re.split(r'\s*(?:,|and|&amp;|&)\s*', spec):
        if re.search(r'[–-]', p):
            a, b = [int(x) for x in re.split(r'\s*[–-]\s*', p)]
            nums.extend(range(a, b + 1) if b - a < 15 else [a, b])
        elif p.strip(): nums.append(int(p))
    return nums
def fmt(nums):
    nums = sorted(set(nums)); out = []; a = prev = nums[0]
    for x in nums[1:] + [None]:
        if x is not None and x == prev + 1: prev = x; continue
        out.append(str(a) if a == prev else (f'{a}–{prev}' if prev > a + 1 else f'{a}, {prev}'))
        if x is not None: a = prev = x
    return ', '.join(out)
REFLOG = []
def renum_text(txt):
    def rep(m):
        nums = expand(m.group(3))
        if any(x < 1 or x > NOLD for x in nums): return m.group(0)
        new = [REN[x] for x in nums]
        w = m.group(1)
        if len(set(new)) > 1 and not w.endswith('s'): w += 's'
        out = w + m.group(2) + fmt(new)
        if out != m.group(0): REFLOG.append((m.group(0), out))
        return out
    return REF.sub(rep, txt)

