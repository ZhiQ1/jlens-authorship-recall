D='/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/180809d4-e5ec-4f13-97be-7ef90a42d8be/scratchpad/banners_20261108'
for s in ['experiment_walkthrough_zh','experiment_walkthrough_methods_zh','stage13_script_zh_en','keys_and_shelves_script_zh_en','methods_handbook_guide_plain_zh','process_report','scoring_audit','methods_addendum']:
    a=open(f'{D}/dewrapped/{s}.html','rb').read(); b=open(f'{D}/{s}.html','rb').read()
    i=b.index(b'<div role="note" style="margin:0 0 16px'); j=b.index(b'</div>',i)+6
    ok = b[:i]+b[j:]==a and b.count(b'role="note" style="margin:0 0 16px')==1
    print(s, 'OK' if ok else 'FAIL', 'banner', j-i, 'bytes at', i, 'next:', b[j:j+12].decode(errors='replace'))
