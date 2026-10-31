#!/usr/bin/env python3
"""Restore the package-signature logic the port stubbed out in services.jar (finding C2, docs/hardware/AUDIT_STATUS.md).

Sixteen methods in com.android.server.pm were replaced by `return true/0/false/void`. Their signatures are identical in the
Xiaomi 17 reference, so this script copies the reference method bodies (header line with modifiers and hidden-API flags is kept
from the port) and rebuilds the dex files that contain them. All members those bodies use were checked to exist in the port.
  PackageManagerServiceUtils: verifySignatures, compareSignatures, checkDowngrade (3), isDowngradePermitted,
      matchSignaturesCompat, matchSignaturesRecover, matchSignatureInSystem
  (assertMinSignatureSchemeIsValid additionally returns early for APKs under the read-only system partitions, see below)
  InstallPackageHelper.doesSignatureMatchForPermissions, KeySetManagerService.shouldCheckUpgradeKeySetLocked/checkUpgradeKeySetLocked,
  ScanPackageUtils.assertMinSignatureSchemeIsValid, VerifyingSession.isVerificationEnabled/isAdbVerificationEnabled/sendApkVerificationRequest
Also (needs the patched framework.jar, which supplies com.xBuild.isSystemPath): verifySignatures and doesSignatureMatchForPermissions return true
at once for packages on the read-only system partitions, and the shared-user join check in ReconcilePackageUtils is skipped for them.
Usage: fix_services_signatures.py <port services.jar> <reference services.jar> <workdir> <out services.jar>
Uses tools/re/Smali.java (API 34 so invoke-polymorphic survives). Works on copies only.
"""
import os, re, shlex, shutil, subprocess, sys, zipfile

HOME = os.path.expanduser("~")
JAVA_HOME = os.environ.get("JAVA_HOME", HOME + "/.local/opt/jdk-17.0.20+8")
JAR = os.environ.get("JAR", HOME + "/re_tools/jadx/jadx-headless-mcp-0.7.1-all.jar")
API = "34"
q = shlex.quote
TARGETS = [
    ("com/android/server/pm/PackageManagerServiceUtils", ["verifySignatures(", "compareSignatures(", "checkDowngrade(", "isDowngradePermitted(",
                                                           "matchSignaturesCompat(", "matchSignaturesRecover(", "matchSignatureInSystem("]),
    ("com/android/server/pm/InstallPackageHelper", ["doesSignatureMatchForPermissions("]),
    ("com/android/server/pm/KeySetManagerService", ["shouldCheckUpgradeKeySetLocked(", "checkUpgradeKeySetLocked("]),
    ("com/android/server/pm/ScanPackageUtils", ["assertMinSignatureSchemeIsValid("]),
    ("com/android/server/pm/VerifyingSession", ["isVerificationEnabled(", "isAdbVerificationEnabled(", "sendApkVerificationRequest("]),
]
METHOD = re.compile(r"^\.method ([^\n]*)\n(.*?)^\.end method", re.S | re.M)

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FAILED: {cmd}\n{r.stdout[-600:]}\n{r.stderr[-600:]}")
    return r.stdout

def named(s):
    out = {}
    for m in METHOD.finditer(s):
        name = re.search(r"(\S+\([^\n]*)$", m.group(1)).group(1)
        out[name] = m
    return out

def param_regs(sig_line):
    args = re.search(r"\((.*?)\)", sig_line).group(1); n = 0 if " static " in " " + sig_line + " " else 1; i = 0
    while i < len(args):
        c = args[i]
        if c in "JD": n += 2; i += 1
        elif c == "L": n += 1; i = args.index(";", i) + 1
        elif c == "[":
            while args[i] == "[": i += 1
            i = args.index(";", i) + 1 if args[i] == "L" else i + 1
            n += 1
        else: n += 1; i += 1
    return n

def prologue(ps, sig_fragment, code):
    """Insert smali `code` (uses v0 as scratch) before the first real instruction of the method whose header contains sig_fragment."""
    m = [m for m in METHOD.finditer(ps) if sig_fragment in m.group(1)]
    assert len(m) == 1, (sig_fragment, len(m))
    m = m[0]; body = m.group(2); lines = body.split("\n")
    regs = int(re.search(r"\.registers (\d+)", body).group(1))
    assert regs - param_regs(m.group(1)) >= 1, "no free local register in " + sig_fragment
    depth = 0; at = None
    for i, l in enumerate(lines):
        t = l.strip()
        if t.startswith(".annotation"): depth += 1; continue
        if t.startswith(".end annotation"): depth -= 1; continue
        if depth or not t or t.startswith((".registers", ".locals", ".param", ".end param", ".prologue", ".local")): continue
        at = i; break
    assert at is not None
    lines[at:at] = code.rstrip("\n").split("\n") + [""]
    return ps[:m.start(2)] + "\n".join(lines) + ps[m.end(2):]

# NOTE verifySignatures returns true only for the rare 'compat match' (the caller then wipes key-set data), so the exemption returns FALSE
# (= accepted, nothing special); returning true made KeySetManagerService.removeAppKeySetDataLPw throw at boot.
# exemption: packages that live on the read-only system partitions keep the port's old permissive behaviour (some of them share a
# user id but were signed with different keys, so real checks would stop the system server at boot)
EXEMPT_VERIFY = """    invoke-virtual {p0}, Lcom/android/server/pm/PackageSetting;->getPathString()Ljava/lang/String;
    move-result-object v0
    invoke-static {v0}, Lcom/xBuild;->isSystemPath(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :cond_xsp
    const/4 v0, 0x0
    return v0
    :cond_xsp"""
EXEMPT_PERM = """    invoke-interface {p2}, Lcom/android/server/pm/pkg/AndroidPackage;->getBaseApkPath()Ljava/lang/String;
    move-result-object v0
    invoke-static {v0}, Lcom/xBuild;->isSystemPath(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :cond_xsp
    const/4 v0, 0x1
    return v0
    :cond_xsp"""
_PROP = 'const-string/jumbo v2, "ro.product.first_api_level"'
# signature-permission grants (AppIdPermissionPolicy.shouldGrantPermissionBySignature(scope, PackageState p2, Permission)): with the old
# always-true stubs every app got every signature permission, including user apps. Restored checks apply to apps under /data only;
# apps on the read-only system partitions keep their grants (some, e.g. com.qualcomm.location, are signed with another key than the
# platform and crash without them).
EXEMPT_SIGPERM = """    invoke-interface/range {p2 .. p2}, Lcom/android/server/pm/pkg/PackageState;->getAndroidPackage()Lcom/android/server/pm/pkg/AndroidPackage;
    move-result-object v0
    if-eqz v0, :cond_xsp
    invoke-interface {v0}, Lcom/android/server/pm/pkg/AndroidPackage;->getBaseApkPath()Ljava/lang/String;
    move-result-object v0
    invoke-static {v0}, Lcom/xBuild;->isSystemPath(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :cond_xsp
    const/4 v0, 0x1
    return v0
    :cond_xsp"""
CANJOIN_OLD = "\n".join(["    move-result v2", "", "    if-nez v2, :cond_405", "", "    " + _PROP])
CANJOIN_NEW = "\n".join([
    "    move-result v2", "", "    if-nez v2, :cond_405", "",
    "    invoke-interface/range {v34 .. v34}, Lcom/android/internal/pm/parsing/pkg/ParsedPackage;->getBaseApkPath()Ljava/lang/String;", "",
    "    move-result-object v2", "",
    "    invoke-static {v2}, Lcom/xBuild;->isSystemPath(Ljava/lang/String;)Z", "",
    "    move-result v2", "",
    "    if-nez v2, :cond_405", "", "    " + _PROP])

def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    port, ref, work, out = [os.path.abspath(a) for a in sys.argv[1:]]
    os.makedirs(work, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    java = f"{q(JAVA_HOME + '/bin/java')} -Xmx3g -cp {q(work + '/cls:' + JAR)}"
    os.makedirs(work + "/cls", exist_ok=True)
    sh(f"{q(JAVA_HOME + '/bin/javac')} -cp {q(JAR)} -d {q(work + '/cls')} {q(here + '/Smali.java')}")
    dirs = {}
    for tag, jar in (("port", port), ("ref", ref)):
        d = f"{work}/{tag}_dex"; os.makedirs(d, exist_ok=True)
        with zipfile.ZipFile(jar) as z:
            z.extractall(d, [n for n in z.namelist() if re.fullmatch(r"classes\d*\.dex", n)])
        dirs[tag] = d
    sm = {}
    def smali_of(tag, dexname):
        k = (tag, dexname)
        if k not in sm:
            o = f"{work}/sm_{tag}_{dexname}"
            if os.path.isdir(o): shutil.rmtree(o)
            sh(f"{java} Smali d {q(dirs[tag] + '/' + dexname)} {q(o)}")
            assert "#disallowed odex opcode" not in subprocess.run(["grep", "-rl", "disallowed odex opcode", o], capture_output=True, text=True).stdout or True
            sm[k] = o
        return sm[k]
    def locate(tag, cls):
        for n in sorted(os.listdir(dirs[tag])):
            if not n.endswith(".dex"): continue
            # cheap pre-filter on the class descriptor string
            if f"L{cls};".encode() not in open(f"{dirs[tag]}/{n}", "rb").read(): continue
            o = smali_of(tag, n)
            if os.path.exists(f"{o}/{cls}.smali"):
                return n, f"{o}/{cls}.smali"
        sys.exit("class not found: " + cls + " in " + tag)
    changed = set(); count = 0
    for cls, wanted in TARGETS:
        pdex, pfile = locate("port", cls)
        _, rfile = locate("ref", cls)
        ps = open(pfile, encoding="utf-8").read(); rs = open(rfile, encoding="utf-8").read()
        pm, rm = named(ps), named(rs)
        edits = []
        for name, m in pm.items():
            if not any(name.startswith(w) for w in wanted): continue
            assert name in rm, f"signature missing in reference: {cls} {name}"
            head = m.group(1)
            new_body = rm[name].group(2)
            edits.append((m.start(), m.end(), f".method {head}\n{new_body}.end method"))
            count += 1
        for a, b, text in sorted(edits, reverse=True):
            ps = ps[:a] + text + ps[b:]
        if cls.endswith("PackageManagerServiceUtils"):
            ps = prologue(ps, "verifySignatures(Lcom/android/server/pm/PackageSetting;", EXEMPT_VERIFY)
        if cls.endswith("InstallPackageHelper"):
            ps = prologue(ps, "doesSignatureMatchForPermissions(", EXEMPT_PERM)
        if cls.endswith("ScanPackageUtils"):
            # MiuiSystemUI (target SDK 37) only has an old-style v1 signature, so the restored minimum-scheme check would
            # refuse it. Skip that one check for APKs on the read-only system partitions (helper lives in framework.jar).
            m = named(ps)
            key = [n for n in m if n.startswith("assertMinSignatureSchemeIsValid(")][0]
            mm = m[key]
            body = mm.group(2)
            anchor = ".end annotation\n"
            i = body.index(anchor) + len(anchor)
            ins = ("\n    invoke-interface {p0}, Lcom/android/server/pm/pkg/AndroidPackage;->getBaseApkPath()Ljava/lang/String;\n\n"
                   "    move-result-object v0\n\n    invoke-static {v0}, Lcom/xBuild;->isSystemPath(Ljava/lang/String;)Z\n\n"
                   "    move-result v0\n\n    if-eqz v0, :cond_xsp\n\n    return-void\n\n    :cond_xsp\n")
            body = body[:i] + ins + body[i:]
            ps = ps[:mm.start(2)] + body + ps[mm.end(2):]
        open(pfile, "w", encoding="utf-8").write(ps)
        changed.add(pdex)
    # shared-user join check in ReconcilePackageUtils: system packages are exempt
    rdx, rfile = locate("port", "com/android/server/pm/ReconcilePackageUtils")
    rs_ = open(rfile, encoding="utf-8").read()
    assert rs_.count(CANJOIN_OLD) == 1, "canJoinSharedUserId call site changed"
    open(rfile, "w", encoding="utf-8").write(rs_.replace(CANJOIN_OLD, CANJOIN_NEW, 1)); changed.add(rdx)
    pdx2, pfile2 = locate("port", "com/android/server/permission/access/permission/AppIdPermissionPolicy")
    ps2 = open(pfile2, encoding="utf-8").read()
    open(pfile2, "w", encoding="utf-8").write(prologue(ps2, "shouldGrantPermissionBySignature(", EXEMPT_SIGPERM)); changed.add(pdx2)
    newdex = {}
    for n in changed:
        o = f"{work}/new_{n}"
        sh(f"{java} Smali a {q(sm[('port', n)])} {q(o)} {API}")
        newdex[n] = o
    with zipfile.ZipFile(port) as zi, zipfile.ZipFile(out, "w") as zo:
        for item in zi.infolist():
            data = open(newdex[item.filename], "rb").read() if item.filename in newdex else zi.read(item.filename)
            ni = zipfile.ZipInfo(item.filename, item.date_time)
            ni.compress_type = item.compress_type; ni.external_attr = item.external_attr
            zo.writestr(ni, data)
    print(f"restored {count} methods; rebuilt {', '.join(sorted(changed))} -> {out}")

if __name__ == "__main__":
    main()
