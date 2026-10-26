#!/usr/bin/env python3
"""Print the SHA-256 of the signing certificate of an APK (v3, v2, or v1).

Parses the file only; nothing in the APK is executed.
Usage: apk_cert.py <file.apk>   ->  prints "SCHEME FINGERPRINT" or "none"
"""
import hashlib
import struct
import subprocess
import sys
import zipfile

V2_ID = 0x7109871A
V3_ID = 0xF05368C0


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def seq(b):
    """Split a sequence of uint32-length-prefixed items."""
    out, o = [], 0
    while o + 4 <= len(b):
        n = u32(b, o)
        out.append(b[o + 4:o + 4 + n])
        o += 4 + n
    return out


def sig_block(data):
    eocd = data.rfind(b"PK\x05\x06")
    if eocd < 0:
        return None
    cd_off = u32(data, eocd + 16)
    if data[cd_off - 16:cd_off] != b"APK Sig Block 42":
        return None
    size = struct.unpack_from("<Q", data, cd_off - 24)[0]
    start = cd_off - size - 8
    pairs, o = {}, start + 8
    end = cd_off - 24
    while o < end:
        n = struct.unpack_from("<Q", data, o)[0]
        pid = u32(data, o + 8)
        pairs[pid] = data[o + 12:o + 8 + n]
        o += 8 + n
    return pairs


def first_cert(block):
    signer = seq(seq(block)[0])[0]          # signers -> first signer
    signed_data = seq(signer)[0]             # signed data is the signer's first field
    certs = seq(seq(signed_data)[1])         # [digests, certificates, ...]
    return certs[0] if certs else None


def v1_cert(path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.startswith("META-INF/") and n.upper().endswith((".RSA", ".DSA", ".EC"))]
        if not names:
            return None
        der = z.read(names[0])
    pem = subprocess.run(["openssl", "pkcs7", "-inform", "DER", "-print_certs"], input=der, capture_output=True).stdout
    out = subprocess.run(["openssl", "x509", "-noout", "-fingerprint", "-sha256"], input=pem, capture_output=True).stdout.decode()
    return out.strip().split("=", 1)[1] if "=" in out else None


def java_hash(der):
    """Android's Signature.hashCode(): Java Arrays.hashCode(byte[]), as dumpsys prints it."""
    h = 1
    for b in der:
        h = (31 * h + (b - 256 if b > 127 else b)) & 0xFFFFFFFF
    return format(h, "x")


def colon(h):
    return ":".join(h[i:i + 2] for i in range(0, len(h), 2)).upper()


def main(path):
    with open(path, "rb") as f:
        data = f.read()
    pairs = sig_block(data) or {}
    for pid, name in ((V3_ID, "v3"), (V2_ID, "v2")):
        if pid in pairs:
            try:
                cert = first_cert(pairs[pid])
                if cert:
                    print(name, colon(hashlib.sha256(cert).hexdigest()), java_hash(cert))
                    return
            except Exception:
                pass
    fp = v1_cert(path)
    print("v1", fp) if fp else print("none")


if __name__ == "__main__":
    main(sys.argv[1])
