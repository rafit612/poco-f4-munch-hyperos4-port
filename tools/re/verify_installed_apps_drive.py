# Pull every APK of the apps installed under /data/app in batches, verify each with the real apksig library (tools/re/ApkVerifyAll.java compiled into ./cls) and delete it again.
# Needs files.txt ("<apk path on phone> <package>" per line, from `pm path`), adb, JDK 17. Output: results.tsv; compare with verify_installed_apps_compare.py
import subprocess,os,sys
A=os.path.expanduser('~/Android/Sdk/platform-tools/adb')
JB=os.path.expanduser('~/.local/opt/jdk-17.0.20+8/bin/java'); AS=os.path.expanduser('~/Android/Sdk/build-tools/37.0.0/lib/apksigner.jar')
rows=[l.split() for l in open('files.txt')]
out=open('results.tsv','w')
BATCH=14; n=0
for i in range(0,len(rows),BATCH):
    chunk=rows[i:i+BATCH]; local=[]
    for k,(path,pkg) in enumerate(chunk):
        dst=f'b/{i+k:04d}__{pkg}__{os.path.basename(path)}'
        r=subprocess.run([A,'pull',path,dst],capture_output=True,text=True)
        if r.returncode==0 and os.path.exists(dst): local.append(dst)
        else: out.write(f'PULLFAIL\t\t\t{dst}\t{r.stderr.strip()[:80]}\n')
    open('batch.txt','w').write('\n'.join(local)+'\n')
    r=subprocess.run([JB,'-Xmx1500m','-cp','cls:'+AS,'ApkVerifyAll','batch.txt'],capture_output=True,text=True)
    out.write(r.stdout); out.flush()
    for f in local:
        try: os.remove(f)
        except OSError: pass
    n+=len(chunk); print(n,'/',len(rows),flush=True)
out.close(); print('DONE')
