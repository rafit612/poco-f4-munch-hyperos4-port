# Per-package granted permissions of a `dumpsys package packages` dump -> json. Usage: package_permissions.py <dump.txt> <out.json>
# Compare two json files (before/after a change) to see which packages lost or gained permissions.
import re,sys,collections
txt=open(sys.argv[1],errors='ignore').read()
out={}
for m in re.finditer(r'^  Package \[([^\]]+)\].*?(?=^  Package \[|\Z)',txt,re.S|re.M):
    name=m.group(1); body=m.group(0)
    granted=set(re.findall(r'^\s+([\w.]+): granted=true',body,re.M))
    flags=re.search(r'^\s+pkgFlags=\[ ([^\]]*)\]',body,re.M)
    sig=re.search(r'signatures=PackageSignatures\{[^}]*signatures:\[([^\]]*)\]',body)
    out[name]=(granted,flags.group(1) if flags else '',sig.group(1) if sig else '')
import json
json.dump({k:[sorted(v[0]),v[1],v[2]] for k,v in out.items()},open(sys.argv[2],'w'))
print(len(out),'packages;',sum(len(v[0]) for v in out.values()),'granted permission entries; system:',sum(1 for v in out.values() if 'SYSTEM' in v[1]))
