# usage: run in a folder holding live.dtb and <tag>.merged.dtb (cpp + dtc -@ + fdtoverlay of kona-v2.1 and the munch overlay), tags E and R
import struct,sys,collections,re
def parse(fn):
    b=open(fn,'rb').read(); m,ts,os_,oss=struct.unpack('>4I',b[:16])
    so=struct.unpack('>I',b[12:16])[0]; st=struct.unpack('>I',b[8:12])[0]; sb=struct.unpack('>I',b[12:16])[0]
    off_struct=struct.unpack('>I',b[8:12])[0]; off_str=struct.unpack('>I',b[12:16])[0]
    i=off_struct; path=[]; nodes={}
    while True:
        t=struct.unpack('>I',b[i:i+4])[0]; i+=4
        if t==1:
            e=b.index(b'\0',i); n=b[i:e].decode(); i=(e+4)&~3; path.append(n); nodes['/'.join(path) or '/']={}
        elif t==2: path.pop()
        elif t==3:
            l,no=struct.unpack('>II',b[i:i+8]); i+=8; v=b[i:i+l]; i=(i+l+3)&~3
            e=b.index(b'\0',off_str+no); nodes['/'.join(path) or '/'][b[off_str+no:e].decode()]=v
        elif t==4: pass
        elif t==9: break
    return nodes
live=parse('live.dtb'); 
for tag in ('E','R'):
    n=parse(tag+'.merged.dtb')
    for x in list(n):
        if x.startswith(('/__symbols__','/__fixups__','/__local_fixups__')): del n[x]
    L={k:v for k,v in live.items() if not k.startswith(('/__symbols__','/__fixups__','/__local_fixups__'))}
    only_live=sorted(set(L)-set(n)); only_src=sorted(set(n)-set(L)); both=set(L)&set(n)
    print(f'== {tag}: live nodes {len(L)}, source nodes {len(n)}, only in live {len(only_live)}, only in source {len(only_src)}')
    diffv=[];missp=[];extrap=[]
    sk=('phandle','linux,phandle')
    for k in both:
        for p in set(L[k])|set(n[k]):
            if p in sk: continue
            if p not in n[k]: missp.append((k,p))
            elif p not in L[k]: extrap.append((k,p))
            elif L[k][p]!=n[k][p]: diffv.append((k,p))
    print(' props: only live',len(missp),'only source',len(extrap),'value differs',len(diffv))
    def top(xs,d=3): return collections.Counter('/'.join(x.split('/')[:d]) for x in xs).most_common(16)
    print(' only-live nodes:',top(only_live,3)); print(' only-source nodes:',top(only_src,3))
    print(' sample only-live:',only_live[:25])
    txt=lambda v:v.rstrip(b'\0').decode('latin1') if all(c<128 for c in v) else v.hex()[:40]
    interesting=[x for x in diffv if x[1] in('compatible','status','reg','qcom,mdss-dsi-panel-name','memory-region','size')]
    print(' key value diffs',len(interesting)); 
    for k,p in sorted(interesting)[:40]: print('   ',k[-58:],p,'L=',txt(L[k][p])[:40],'S=',txt(n[k][p])[:40])
    print(' miss-live props sample:',[f"{k.split('/')[-1]}:{p}" for k,p in sorted(missp)[:30]])
    # thermal
    tz=lambda d:{k.split('/')[-1] for k in d if re.match(r'^/?thermal-zones/[^/]+$',k.lstrip('/'))}
    a,b_=tz(L),tz(n); print(' thermal zones live',len(a),'source',len(b_),'only live',sorted(a-b_)[:30],'only source',sorted(b_-a)[:30])
    for p in ('qcom,msm-id','qcom,board-id','qcom,pmic-id','model'):
        print('  root',p,'live',L.get('/',{}).get(p,b'').hex()[:40],'src',n.get('/',{}).get(p,b'').hex()[:40])
