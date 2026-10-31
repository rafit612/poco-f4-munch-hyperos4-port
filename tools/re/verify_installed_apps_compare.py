# Compare results.tsv with the certificates stored in packages.xml (adb shell su -c "abx2xml /data/system/packages.xml -" > packages.xml).
# Reports files that fail real verification and packages whose APK certificate differs from the stored one.
import re,hashlib,collections
import xml.etree.ElementTree as ET
root=ET.parse('packages.xml').getroot()
keys={}   # cert index -> sha256
def walk(e):
    for c in e.iter('cert'):
        if c.get('key'): keys[c.get('index')]=hashlib.sha256(bytes.fromhex(c.get('key'))).hexdigest()
walk(root)
stored={}
for p in root.iter('package'):
    s=p.find('sigs')
    if s is None: continue
    stored[p.get('name')]={keys.get(c.get('index'),'?') for c in s.findall('cert')}
res=collections.defaultdict(list)
for l in open('results.tsv'):
    f=l.rstrip('\n').split('\t')
    if len(f)<4: continue
    status,schemes,sha,path=f[0],f[1],f[2],f[3]; err=f[4] if len(f)>4 else ''
    m=re.match(r'b/\d+__(.+?)__(.*)$',path)
    pkg,fn=(m.group(1),m.group(2)) if m else (path,'')
    res[pkg].append((fn,status,schemes,set(sha.split(',')) if sha else set(),err))
bad_sig=[];mismatch=[];ok=0;nosig=[]
for pkg,items in sorted(res.items()):
    base=[i for i in items if i[0]=='base.apk']
    for fn,st,sch,sh,err in items:
        if st!='OK': bad_sig.append((pkg,fn,st,err[:90]))
    if base and base[0][3] and pkg in stored and base[0][3]!=stored[pkg]: mismatch.append((pkg,sorted(base[0][3])[:1],sorted(stored[pkg])[:1]))
    elif base and base[0][1]=='OK': ok+=1
print('packages checked:',len(res),'| files:',sum(len(v) for v in res.values()))
print('packages whose files all verify and cert matches the database:',ok)
print('\nFILES THAT DO NOT PASS REAL VERIFICATION:',len(bad_sig))
for b in bad_sig: print('  ',b)
print('\nSTORED CERT != APK CERT (base.apk):',len(mismatch))
for m in mismatch: print('  ',m[0],'apk',m[1][0][:12] if m[1] else '-','stored',m[2][0][:12] if m[2] else '-')
