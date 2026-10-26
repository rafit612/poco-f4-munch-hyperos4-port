#!/usr/bin/env python3
"""Print the signing certificate subject of an APK (v3/v2 block, falling back to v1)."""
import subprocess, sys, zipfile
sys.path.insert(0, sys.argv[0].rsplit("/", 1)[0])
from apk_cert import sig_block, first_cert, V2_ID, V3_ID

def subject_der(der):
    r = subprocess.run(["openssl", "x509", "-inform", "DER", "-noout", "-subject"], input=der, capture_output=True)
    return r.stdout.decode().strip().replace("subject=", "")

path = sys.argv[1]
data = open(path, "rb").read()
pairs = sig_block(data) or {}
for pid in (V3_ID, V2_ID):
    if pid in pairs:
        try:
            c = first_cert(pairs[pid])
            if c:
                print(subject_der(c)); sys.exit()
        except Exception:
            pass
with zipfile.ZipFile(path) as z:
    n = [x for x in z.namelist() if x.startswith("META-INF/") and x.upper().endswith((".RSA", ".DSA", ".EC"))]
    if n:
        p7 = z.read(n[0])
        pem = subprocess.run(["openssl", "pkcs7", "-inform", "DER", "-print_certs"], input=p7, capture_output=True).stdout
        print(subprocess.run(["openssl", "x509", "-noout", "-subject"], input=pem, capture_output=True).stdout.decode().strip().replace("subject=", ""))
    else:
        print("UNSIGNED")
