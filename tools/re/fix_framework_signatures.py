#!/usr/bin/env python3
"""Restore APK signature verification in the port's framework.jar (finding C2, see docs/hardware/AUDIT_STATUS.md).

The port replaced seven checks with `invoke-static {}, Lcom/xBuild;->isOne()Z` (always true). This script
  1. restores the original `Signature.verify([B)Z` / `MessageDigest.isEqual([B[B)Z` calls (registers taken from the
     Xiaomi 17 reference, where the same methods are byte-identical apart from these seven lines),
  2. adds `com.xBuild.isSystemPath(String)` and makes `ParsingPackageUtils.getSigningDetails(...)` skip the full
     verification only for APKs under /system, /system_ext, /product, /vendor, /odm and /mi_ext (read-only OS
     partitions; the porter modified 12 of those apps after signing). Anything under /data is verified for real.
4. (needs the reference framework.jar as 4th argument) restores the methods the port reduced to `return true` / empty, copying the bodies
     from the Xiaomi 17 reference: SigningDetails and PackageParser$SigningDetails .checkCapability/.checkCapabilityRecover/
     .hasAncestorOrSelf/.hasCommonAncestor (certificate continuity, shared-uid and signature-permission checks) and
     ApkSigningBlockUtils.verifyIntegrityForVerityBasedAlgorithm.
It works on copies only: usage  fix_framework_signatures.py <framework.jar> <workdir> <out framework.jar> [<reference framework.jar>]
Needs: JDK 17 on PATH or JAVA env, JADX/smali "all" jar in JAR env (default ~/re_tools/jadx/jadx-headless-mcp-0.7.1-all.jar),
and tools/re/Smali.java compiled into <workdir>/cls (this script compiles it).
"""
import os, re, shlex, shutil, subprocess, sys, zipfile

HOME = os.path.expanduser("~")
JAVA_HOME = os.environ.get("JAVA_HOME", HOME + "/.local/opt/jdk-17.0.20+8")
JAR = os.environ.get("JAR", HOME + "/re_tools/jadx/jadx-headless-mcp-0.7.1-all.jar")
API = "34"          # assembler writes dex version 040; ART on Android 17 reads it

# (dex, smali file, method signature fragment, [replacement instructions in order of appearance])
SITES = [
    ("classes4.dex", "android/util/apk/ApkSignatureSchemeV4Verifier.smali", "verifySigner(Landroid/os/incremental/V4Signature$SigningInfo;[B)",
     ["invoke-virtual {v9, v1}, Ljava/security/Signature;->verify([B)Z"]),
    ("classes4.dex", "android/util/apk/ApkSignatureSchemeV2Verifier.smali", "verifySigner(Ljava/nio/ByteBuffer;Ljava/util/Map;",
     ["invoke-virtual {v13, v7}, Ljava/security/Signature;->verify([B)Z",
      "invoke-static {v8, v4}, Ljava/security/MessageDigest;->isEqual([B[B)Z"]),
    ("classes4.dex", "android/util/apk/ApkSignatureSchemeV3Verifier.smali", "verifySigner(Ljava/nio/ByteBuffer;Ljava/security/cert/CertificateFactory;)",
     ["invoke-virtual {v4, v6}, Ljava/security/Signature;->verify([B)Z"]),
    ("classes4.dex", "android/util/apk/ApkSignatureSchemeV3Verifier.smali", "verifyV32Signers(",
     ["invoke-static {v5, v4}, Ljava/security/MessageDigest;->isEqual([B[B)Z"]),
    ("classes4.dex", "android/util/apk/ApkSigningBlockUtils.smali", "verifyIntegrityFor1MbChunkBasedAlgorithm(",
     ["invoke-static {v5, v6}, Ljava/security/MessageDigest;->isEqual([B[B)Z"]),
    ("classes4.dex", "android/util/apk/ApkSigningBlockUtils.smali", "verifyProofOfRotationStruct(",
     ["invoke-virtual {v14, v11}, Ljava/security/Signature;->verify([B)Z"]),
]
ISONE = "invoke-static {}, Lcom/xBuild;->isOne()Z"

PREFIXES = ["/system/", "/system_ext/", "/product/", "/vendor/", "/odm/", "/mi_ext/"]
HELPER = """
.method public static isSystemPath(Ljava/lang/String;)Z
    .registers 3

    const/4 v0, 0x0

    if-nez p0, :cond_have

    return v0

    :cond_have
    const-string v1, ".."

    invoke-virtual {p0, v1}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v1

    if-eqz v1, :cond_nodots

    return v0

    :cond_nodots
""" + "".join(f"""    const-string v1, "{p}"

    invoke-virtual {{p0, v1}}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v1

    if-nez v1, :cond_yes

""" for p in PREFIXES) + """    return v0

    :cond_yes
    const/4 v0, 0x1

    return v0
.end method
"""

def sh(cmd, **kw):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.exit(f"FAILED: {cmd}\n{r.stdout[-800:]}\n{r.stderr[-800:]}")
    return r.stdout

def method_span(s, sig_fragment):
    for m in re.finditer(r"^\.method [^\n]*\n(.*?)^\.end method", s, re.S | re.M):
        head = s[m.start():s.index("\n", m.start())]
        if sig_fragment in head:
            return m.start(), m.end()
    sys.exit("method not found: " + sig_fragment)

def main():
    if len(sys.argv) not in (4, 5):
        sys.exit(__doc__)
    jar_in, work, jar_out = [os.path.abspath(a) for a in sys.argv[1:4]]
    ref_jar = os.path.abspath(sys.argv[4]) if len(sys.argv) == 5 else None
    os.makedirs(work, exist_ok=True)
    q = shlex.quote
    java = f"{q(JAVA_HOME + '/bin/java')} -Xmx3g -cp {q(work + '/cls:' + JAR)}"
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(f"{work}/cls", exist_ok=True)
    sh(f"{q(JAVA_HOME + '/bin/javac')} -cp {q(JAR)} -d {q(work + '/cls')} {q(here + '/Smali.java')}")
    dex = f"{work}/dex"; os.makedirs(dex, exist_ok=True)
    with zipfile.ZipFile(jar_in) as z:
        z.extractall(dex, [n for n in z.namelist() if re.fullmatch(r"classes\d*\.dex", n)])
    changed = {}
    smali = {}
    def get(dexname):
        if dexname not in smali:
            out = f"{work}/sm_{dexname}"
            if os.path.isdir(out): shutil.rmtree(out)
            sh(f"{java} Smali d {q(dex + '/' + dexname)} {q(out)}")
            smali[dexname] = out
        return smali[dexname]
    # 1. restore the seven checks
    for dexname, rel, sig, repl in SITES:
        p = f"{get(dexname)}/{rel}"
        s = open(p, encoding="utf-8").read()
        a, b = method_span(s, sig)
        body = s[a:b]
        assert body.count(ISONE) == len(repl), (rel, sig, body.count(ISONE), len(repl))
        for r in repl:
            body = body.replace(ISONE, r, 1)
        open(p, "w", encoding="utf-8").write(s[:a] + body + s[b:])
        changed[dexname] = True
    # 1b. methods stubbed to `return true`: copy the reference bodies
    if ref_jar:
        METH = re.compile(r"^\.method ([^\n]*)\n(.*?)^\.end method", re.S | re.M)
        rdex = f"{work}/refdex"; os.makedirs(rdex, exist_ok=True)
        with zipfile.ZipFile(ref_jar) as z:
            z.extractall(rdex, [n for n in z.namelist() if re.fullmatch(r"classes\d*\.dex", n)])
        def locate(dirpath, cls, tag):
            for n in sorted(os.listdir(dirpath)):
                if not n.endswith(".dex"): continue
                if f"L{cls};".encode() not in open(f"{dirpath}/{n}", "rb").read(): continue
                o = f"{work}/sm_{tag}_{n}"
                if not os.path.isdir(o): sh(f"{java} Smali d {q(dirpath + '/' + n)} {q(o)}")
                if os.path.exists(f"{o}/{cls}.smali"): return n, f"{o}/{cls}.smali"
            sys.exit("class not found: " + cls)
        TARGETS = [("android/content/pm/SigningDetails", ["checkCapability(", "checkCapabilityRecover(", "hasAncestorOrSelf(", "hasCommonAncestor("]),
                   ("android/content/pm/PackageParser$SigningDetails", ["checkCapability(", "checkCapabilityRecover(", "hasAncestorOrSelf(", "hasCommonAncestor("]),
                   ("android/util/apk/ApkSigningBlockUtils", ["verifyIntegrityForVerityBasedAlgorithm("])]
        for cls, wanted in TARGETS:
            pdx = pfile = None
            for n in sorted(os.listdir(dex)):          # same disassembled trees (get) as the other steps, so no edit is lost
                if n.endswith(".dex") and f"L{cls};".encode() in open(f"{dex}/{n}", "rb").read():
                    f = f"{get(n)}/{cls}.smali"
                    if os.path.exists(f): pdx, pfile = n, f; break
            assert pdx, "class not found in port: " + cls
            _, rfile = locate(rdex, cls, "r")
            ps, rs = open(pfile, encoding="utf-8").read(), open(rfile, encoding="utf-8").read()
            def named(src):
                return {re.search(r"(\S+\([^\n]*)$", m.group(1)).group(1): m for m in METH.finditer(src)}
            pm, rm = named(ps), named(rs)
            edits = []
            for name, m in pm.items():
                if not any(name.startswith(w) for w in wanted): continue
                assert name in rm, "signature missing in reference: " + cls + " " + name
                edits.append((m.start(), m.end(), ".method " + m.group(1) + "\n" + rm[name].group(2) + ".end method"))
            assert edits, cls
            for a, b, text in sorted(edits, reverse=True):
                ps = ps[:a] + text + ps[b:]
            open(pfile, "w", encoding="utf-8").write(ps)
            changed[pdx] = True
            print("restored", len(edits), "methods in", cls)
    # 2. system-path exemption in ParsingPackageUtils.getSigningDetails(ParseInput,String,boolean,boolean,SigningDetails,int)
    d5 = [n for n in os.listdir(dex) if n.endswith(".dex")]
    target = None
    for n in sorted(d5):
        if b"Lcom/android/internal/pm/pkg/parsing/ParsingPackageUtils;" in open(f"{dex}/{n}", "rb").read() and \
           subprocess.run(["grep", "-aq", "unsafeGetCertsWithoutVerification", f"{dex}/{n}"]).returncode == 0:
            # the defining dex also contains the class_def; the disassembly tells for sure
            out = get(n)
            if os.path.exists(f"{out}/com/android/internal/pm/pkg/parsing/ParsingPackageUtils.smali"):
                target = n; break
    assert target, "ParsingPackageUtils not found"
    p = f"{get(target)}/com/android/internal/pm/pkg/parsing/ParsingPackageUtils.smali"
    s = open(p, encoding="utf-8").read()
    a, b = method_span(s, "getSigningDetails(Landroid/content/pm/parsing/result/ParseInput;Ljava/lang/String;ZZLandroid/content/pm/SigningDetails;I)")
    body = s[a:b]
    m = re.search(r"\n    if-eqz p2, (:cond_\w+)\n", body)
    assert m and body.count("if-eqz p2,") == 1
    ins = ("\n    invoke-static {p1}, Lcom/xBuild;->isSystemPath(Ljava/lang/String;)Z\n\n    move-result v1\n\n"
           "    if-eqz v1, :cond_xsp\n\n    const/4 p2, 0x1\n\n    :cond_xsp\n")
    body = body[:m.start()] + ins + body[m.start():]
    assert re.search(r"\.registers (\d+)", body) and int(re.search(r"\.registers (\d+)", body).group(1)) >= 6
    open(p, "w", encoding="utf-8").write(s[:a] + body + s[b:])
    changed[target] = True
    # 3. helper in com.xBuild
    xd = None
    for n in sorted(os.listdir(dex)):
        if not n.endswith(".dex"): continue
        if subprocess.run(["grep", "-aq", "Lcom/xBuild;", f"{dex}/{n}"]).returncode == 0:
            out = get(n)
            if os.path.exists(f"{out}/com/xBuild.smali"):
                xd = n; break
    assert xd, "com.xBuild not found"
    p = f"{get(xd)}/com/xBuild.smali"
    s = open(p, encoding="utf-8").read()
    assert "isSystemPath" not in s
    open(p, "w", encoding="utf-8").write(s.rstrip("\n") + "\n" + HELPER)
    changed[xd] = True
    # 4. assemble the changed dex files, rebuild the jar (same entries, same order, only those dex replaced)
    newdex = {}
    for n in changed:
        out = f"{work}/new_{n}"
        sh(f"{java} Smali a {q(smali[n])} {q(out)} {API}")
        newdex[n] = out
    with zipfile.ZipFile(jar_in) as zi, zipfile.ZipFile(jar_out, "w") as zo:
        for item in zi.infolist():
            data = open(newdex[item.filename], "rb").read() if item.filename in newdex else zi.read(item.filename)
            ni = zipfile.ZipInfo(item.filename, item.date_time)
            ni.compress_type = item.compress_type
            ni.external_attr = item.external_attr
            zo.writestr(ni, data)
    print("patched dex:", ", ".join(sorted(changed)), "->", jar_out)

if __name__ == "__main__":
    main()
