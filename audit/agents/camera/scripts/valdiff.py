import sys,struct,collections,array
sys.path.insert(0,sys.argv[1])
from chx import syms
# order-independent comparison: per symbol-name, multiset of non-small 32-bit words (floats/large ints)
def prof(fn):
    s,b=syms(fn)
    per=collections.defaultdict(collections.Counter); allc=collections.Counter()
    names=collections.Counter()
    for sid,name,off,sz,d in s:
        names[name]+=1
        a=array.array('I'); a.frombytes(d[:len(d)//4*4])
        for v in a:
            if v>0xFFFF:
                per[name][v]+=1; allc[v]+=1
    return per,allc,names,len(s)
fns=sys.argv[2:]
P={f:prof(f) for f in fns}
for i in range(len(fns)):
    for j in range(i+1,len(fns)):
        A=P[fns[i]];B=P[fns[j]]
        tot=sum(A[1].values()); d=sum((A[1]-B[1]).values())+sum((B[1]-A[1]).values())
        changed=[n for n in set(A[0])|set(B[0]) if A[0].get(n,collections.Counter())!=B[0].get(n,collections.Counter())]
        print("%s vs %s: value-words %d, differing(sym) %d = %.3f%% ; symbol-name-sets equal: %s ; names with changed values: %d"%(fns[i],fns[j],tot,d,100*d/2/max(tot,1),A[2]==B[2],len(changed)))
        mods=sorted(changed)
        print("   changed:", " ".join(mods[:300]))
