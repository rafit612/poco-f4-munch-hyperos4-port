#!/usr/bin/env python3
"""Fix: loudspeaker button sometimes only changes the screen (docs/hardware/subsystems/CALL_SPEAKER_BUG.md).

Telecom (Telecom.apk) compares the route the user asks for with a cached copy of the last communication device. After another app
used the speaker the cache is stale, so Telecom believes the speaker is already active and never calls setCommunicationDevice().
The Xiaomi 17 reference re-reads the real device from AudioManager first. This script copies the reference's
CallAudioRouteController.isCurrentCommunicationDevice(AudioRoute) into the port's Telecom.apk.

The APK's signing block and every other entry are kept byte for byte (the app shares the system UID, so its certificate must not
change; the stale signature digest is accepted because the file sits on a read-only system partition, see
tools/re/fix_framework_signatures.py). Only classes.dex is replaced.
Usage: fix_telecom_speaker.py <port Telecom.apk> <reference Telecom.apk> <workdir> <out Telecom.apk>
"""
import os, re, shlex, shutil, struct, subprocess, sys, zipfile, zlib

HOME = os.path.expanduser("~")
JAVA_HOME = os.environ.get("JAVA_HOME", HOME + "/.local/opt/jdk-17.0.20+8")
JAR = os.environ.get("JAR", HOME + "/re_tools/jadx/jadx-headless-mcp-0.7.1-all.jar")
q = shlex.quote
CLS = "com/android/server/telecom/CallAudioRouteController"
SIG = "isCurrentCommunicationDevice(Lcom/android/server/telecom/AudioRoute;)Z"
METHOD = re.compile(r"^\.method ([^\n]*)\n(.*?)^\.end method", re.S | re.M)

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FAILED: {cmd}\n{r.stdout[-600:]}\n{r.stderr[-600:]}")

def find(s):
    for m in METHOD.finditer(s):
        if m.group(1).rstrip().endswith(SIG):
            return m
    sys.exit("method not found")

def replace_entry_keep_everything(apk_in, name, new_bytes, apk_out):
    b = open(apk_in, "rb").read()
    eocd = b.rfind(b"PK\x05\x06")
    n_entries, cd_size, cd_off = struct.unpack("<HII", b[eocd + 10:eocd + 20])
    pos = cd_off; cds = []
    for _ in range(n_entries):
        assert b[pos:pos + 4] == b"PK\x01\x02"
        nlen, elen, clen = struct.unpack("<HHH", b[pos + 28:pos + 34])
        rec = bytearray(b[pos:pos + 46 + nlen + elen + clen])
        cds.append((struct.unpack("<I", rec[42:46])[0], rec, b[pos + 46:pos + 46 + nlen].decode()))
        pos += len(rec)
    assert pos == cd_off + cd_size
    order = sorted(cds, key=lambda t: t[0])
    magic = b"APK Sig Block 42"
    sig_start = sig_end = None
    if b[cd_off - 16:cd_off] == magic:
        blk = struct.unpack("<Q", b[cd_off - 24:cd_off - 16])[0]
        sig_start, sig_end = cd_off - (blk + 8), cd_off
    data_end = sig_start if sig_start is not None else cd_off
    out = bytearray(); new_off = {}
    for i, (off, rec, nm) in enumerate(order):
        end = order[i + 1][0] if i + 1 < len(order) else data_end
        new_off[nm] = len(out)
        if nm == name:
            comp = zlib.compressobj(9, zlib.DEFLATED, -15); cdata = comp.compress(new_bytes) + comp.flush()
            crc = zlib.crc32(new_bytes) & 0xffffffff
            nb = nm.encode()
            out += struct.pack("<IHHHHHIIIHH", 0x04034b50, 20, 0, 8, 0, 0x21, crc, len(cdata), len(new_bytes), len(nb), 0) + nb + cdata
            rec[8:10] = struct.pack("<H", 0)               # flags: no data descriptor
            rec[10:12] = struct.pack("<H", 8)
            rec[16:24] = struct.pack("<II", crc, len(cdata))
            rec[24:28] = struct.pack("<I", len(new_bytes))
        else:
            out += b[off:end]
    sig_new = len(out)
    if sig_start is not None:
        out += b[sig_start:sig_end]
    cd_new = len(out)
    for off, rec, nm in cds:                                # original central directory order
        rec[42:46] = struct.pack("<I", new_off[nm])
        out += rec
    e = bytearray(b[eocd:])
    e[16:20] = struct.pack("<I", cd_new)
    e[12:16] = struct.pack("<I", len(out) - cd_new)
    out += e
    open(apk_out, "wb").write(out)

def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    port, ref, work, out = [os.path.abspath(a) for a in sys.argv[1:]]
    os.makedirs(work, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    java = f"{q(JAVA_HOME + '/bin/java')} -Xmx2g -cp {q(work + '/cls:' + JAR)}"
    os.makedirs(work + "/cls", exist_ok=True)
    sh(f"{q(JAVA_HOME + '/bin/javac')} -cp {q(JAR)} -d {q(work + '/cls')} {q(here + '/Smali.java')}")
    for tag, apk in (("port", port), ("ref", ref)):
        os.makedirs(f"{work}/{tag}", exist_ok=True)
        open(f"{work}/{tag}/classes.dex", "wb").write(zipfile.ZipFile(apk).read("classes.dex"))
        if os.path.isdir(f"{work}/sm_{tag}"): shutil.rmtree(f"{work}/sm_{tag}")
        sh(f"{java} Smali d {q(work + '/' + tag + '/classes.dex')} {q(work + '/sm_' + tag)}")
    pf, rf = f"{work}/sm_port/{CLS}.smali", f"{work}/sm_ref/{CLS}.smali"
    ps, rs = open(pf, encoding="utf-8").read(), open(rf, encoding="utf-8").read()
    pm, rm = find(ps), find(rs)
    new = f".method {pm.group(1)}\n{rm.group(2)}.end method"
    open(pf, "w", encoding="utf-8").write(ps[:pm.start()] + new + ps[pm.end():])
    sh(f"{java} Smali a {q(work + '/sm_port')} {q(work + '/new.dex')} 34")
    replace_entry_keep_everything(port, "classes.dex", open(f"{work}/new.dex", "rb").read(), out)
    z = zipfile.ZipFile(out); assert z.testzip() is None
    print("patched isCurrentCommunicationDevice ->", out)

if __name__ == "__main__":
    main()
