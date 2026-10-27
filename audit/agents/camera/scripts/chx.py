import struct,sys,hashlib,collections
def parse(fn):
    b=open(fn,'rb').read()
    assert b[:20]==b'QTI Chromatix Header'
    fsize,=struct.unpack_from('<I',b,0x1c)
    tbl_off,nsec=struct.unpack_from('<QQ',b,0x98)
    secs=[struct.unpack_from('<QQQ',b,tbl_off+8+i*24) for i in range(nsec)]  # (id?,off,size)?
    return b,secs
def syms(fn):
    b,secs=parse(fn)
    # section0 symbols at 0xe8
    s0off=0xe8; s0size=struct.unpack_from('<Q',b,0xb0)[0]; dataoff=struct.unpack_from('<Q',b,0xc0)[0]
    out=[]
    for o in range(s0off,s0off+s0size,0x48):
        sid,=struct.unpack_from('<Q',b,o); name=b[o+8:o+48].split(b'\0')[0].decode('latin1')
        off,sz=struct.unpack_from('<QQ',b,o+56)
        out.append((sid,name,off,sz,b[dataoff+off:dataoff+off+sz]))
    return out,b
if __name__=="__main__":
    fns=sys.argv[1:]
    S={}
    for f in fns:
        s,b=syms(f); S[f]=s
        print(f,len(s),"datasum",sum(x[3] for x in s), "hdr", b[0x20:0x28].hex())
    def ms(s): return collections.Counter((n,hashlib.sha1(d).hexdigest()) for _,n,_,_,d in s)
    M={f:ms(S[f]) for f in fns}
    for i in range(len(fns)):
        for j in range(i+1,len(fns)):
            a,c=M[fns[i]],M[fns[j]]; com=sum((a&c).values()); tot=max(sum(a.values()),sum(c.values()))
            # bytes differing at blob level
            ab=sum(len(S[fns[i]][0][4]) for _ in [0])
            print(fns[i],fns[j],"identical blobs %d/%d = %.2f%%"%(com,tot,100*com/tot))
