import sys,os,re,collections
# usage: path_audit.py <dir holding kcmp/paths2.txt> <lineage> <liyafe> <rohman>
SP,*trees=sys.argv[1:]
names=['Lineage','liyafe','rohman']
need=collections.defaultdict(set)
for l in open(SP+'/kcmp/paths2.txt',errors='ignore'):
    p=l.split()
    if len(p)<3 or p[0]!='E':continue
    leaf=p[1].rstrip('/').split('/')[-1]
    if len(leaf)<4 or re.fullmatch(r'[0-9.]+',leaf): continue
    if p[1].startswith('/proc/') and re.match(r'/proc/\d',p[1]):continue
    need[leaf].add((p[1],p[2]))
leaves=set(need); pat=re.compile(rb'[A-Za-z0-9_.,-]{4,}')
found=[set() for _ in trees]
for i,r in enumerate(trees):
    for d,ds,fs in os.walk(r):
        ds[:]=[x for x in ds if x not in('.git','Documentation','tools','samples','out')and not(d==r+'/arch' and x!='arm64')]
        for f in fs:
            if f in leaves: found[i].add(f)
            if f.endswith(('.c','.h','.dtsi','.dts','Kconfig')):
                try:b=open(os.path.join(d,f),'rb').read()
                except:continue
                found[i]|=leaves&{m.decode() for m in pat.findall(b)}
print('leaves existing on phone',len(leaves))
for i,n in enumerate(names):print(n,'has',len(found[i]))
for i,n in enumerate(names):
    m=sorted(leaves-found[i]-(found[(i+1)%3]&found[(i+2)%3]&set()))
    print('==missing',n,len(m))
    only=[x for x in m]
    print(' '.join(only)[:6000])
for x in sorted(leaves-found[0]):
    print('L-missing',x,sorted(need[x])[:2])
