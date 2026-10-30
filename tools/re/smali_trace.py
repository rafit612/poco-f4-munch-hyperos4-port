#!/usr/bin/env python3
import re,sys
# usage: trace.py <file.smali> <Lclass;> <method name>... : add one register + label/fall-through logs (tag MunchNight)
p,cls=sys.argv[1],sys.argv[2]; names=sys.argv[3:]; s=open(p).read()
def nparams(sig,static):
    a=re.match(r"\((.*)\)",sig).group(1); n=0 if static else 1; i=0
    while i<len(a):
        c=a[i]
        if c in "JD": n+=2; i+=1
        elif c=="L": n+=1; i=a.index(";",i)+1
        elif c=="[":
            while a[i]=="[": i+=1
            if a[i]=="L": i=a.index(";",i)+1
            else: i+=1
            n+=1
        else: n+=1; i+=1
    return n
for nm in names:
    m=re.search(r"\.method ([^\n]*?)\b"+re.escape(nm)+r"(\([^\n]*)\n",s); assert m,nm
    start=m.start(); end=s.index(".end method",start); body=s[start:end].split("\n")
    static=" static " in " "+m.group(1)+" "; npar=nparams(m.group(2),static)
    r=re.match(r"\s*\.registers (\d+)",body[1]); n=int(r.group(1)); loc=n-npar; R=f"v{loc}"
    assert not re.search(rf"\bv{loc}\b|\bv{loc+1}\b"," ".join(body)), "register clash in "+nm
    body[1]=f"    .registers {n+1}"
    log=lambda t:[f'    const-string {R}, "{nm} {t}"', f"    invoke-static/range {{{R} .. {R}}}, {cls}->munchLog(Ljava/lang/String;)V"]
    out=[]; first=True; k=0
    for i,l in enumerate(body):
        t=l.strip()
        if first and i>1 and t and t[0] not in ".:#": out+=log("entry"); first=False
        out.append(l)
        nxt=next((x.strip() for x in body[i+1:] if x.strip()),"")
        if re.match(r":(cond|goto)_[0-9a-f]+$",t) and not nxt.startswith(("move-exception","move-result")): out+=log("at "+t)
        if re.match(r"if-[a-z]+ ",t): k+=1; out+=log(f"ft{k} {t[:38]}")
    s=s[:start]+"\n".join(out)+s[end:]
    print(nm,"regs",n,"->",n+1,"params",npar,"ifs",k)
s+='\n.method public static munchLog(Ljava/lang/String;)V\n    .registers 2\n\n    const-string v0, "MunchNight"\n\n    invoke-static {v0, p0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I\n\n    return-void\n.end method\n'
open(p,"w").write(s)
