import subprocess, sys, hashlib, re, json, os
B="/home/odoo-dbsl/poco f4 5g 8gb 256gb munch"
D=B+"/tools/erofs/root/usr/bin/dump.erofs"
IMGS={"m14":(B+"/stock_rom_miui14/images/vendor.img","ext4"),
      "h1":(B+"/stock_rom_1.0.9/images/vendor.img","erofs"),
      "pt":(B+"/audit/port/vendor.img","erofs")}
def ls(img,path):
    f,t=IMGS[img]
    out=[]
    if t=="erofs":
        r=subprocess.run([D,"--ls","--path="+path,f],capture_output=True,text=True).stdout
        started=False
        for l in r.splitlines():
            if "NID TYPE" in l: started=True; continue
            if not started: continue
            p=l.split(None,2)
            if len(p)<3 or p[2] in(".",".."): continue
            out.append((p[2], {"1":"f","2":"d","7":"l"}.get(p[1],p[1])))
    else:
        r=subprocess.run(["/usr/sbin/debugfs","-R","ls -p "+path,f],capture_output=True,text=True).stdout
        for l in r.splitlines():
            p=l.split("/")[1:]
            if len(p)<5 or p[4] in(".",".."): continue
            m=int(p[1],8)
            ty="d" if (m&0o170000)==0o040000 else "l" if (m&0o170000)==0o120000 else "f"
            out.append((p[4],ty))
    return out
def cat(img,path):
    f,t=IMGS[img]
    if t=="erofs": cmd=[D,"--cat","--path="+path,f]
    else: cmd=["/usr/sbin/debugfs","-R","cat "+path,f]
    return subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
def hashf(img,path):
    p=cat(img,path); h=hashlib.sha1(); n=0
    while True:
        b=p.stdout.read(1<<20)
        if not b: break
        h.update(b); n+=len(b)
    p.wait(); return n,h.hexdigest()
def walk(img,path,recurse=True,filt=None):
    res=[]
    for name,ty in ls(img,path):
        full=path.rstrip("/")+"/"+name
        if ty=="d":
            if recurse: res+=walk(img,full,True,filt)
        elif ty=="f":
            if filt is None or re.search(filt,name): res.append(full)
        else:
            res.append(full+" ->link")
    return res
if __name__=="__main__":
    cmd=sys.argv[1]
    if cmd=="cat":
        p=cat(sys.argv[2],sys.argv[3]); sys.stdout.buffer.write(p.stdout.read())
    elif cmd=="ls":
        for x in ls(sys.argv[2],sys.argv[3]): print(x[1],x[0])
