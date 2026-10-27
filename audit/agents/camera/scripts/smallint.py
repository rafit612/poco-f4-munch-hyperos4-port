import sys,struct,collections,array
sys.path.insert(0,sys.argv[1])
from chx import syms
def prof(fn):
    s,b=syms(fn); lo=collections.Counter(); mid=collections.Counter(); nrefpos=0
    blob=collections.Counter()
    for sid,name,off,sz,d in s:
        q=array.array('Q'); q.frombytes(d[:len(d)//8*8])
        for k,v in enumerate(q):
            # treat qword as ref if preceded by a count and is a valid forward id
            if k and 1<=q[k-1]<=100000 and 1<=v<=len(s) and v>sid: nrefpos+=1; lo[(name,"REF")]+=1; continue
            if v<64: lo[(name,v)]+=1
            elif v<=0xFFFF: mid[(name,v)]+=1
        blob[(name,sz)]+=1
    return lo,mid,blob,nrefpos
fns=sys.argv[2:]; P={f:prof(f) for f in fns}
for i in range(len(fns)):
  for j in range(i+1,len(fns)):
    A=P[fns[i]];B=P[fns[j]]
    for k,lab in ((0,"small<64 + REF"),(1,"64..65535"),(2,"(name,size) blobs")):
        d=sum((A[k]-B[k]).values()); print(fns[i],fns[j],lab,"total",sum(A[k].values()),"diff",d)
