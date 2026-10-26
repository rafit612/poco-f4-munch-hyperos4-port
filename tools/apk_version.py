#!/usr/bin/env python3
"""apk_version.py <apk>... : print package, versionCode, versionName, targetSdk from the binary AndroidManifest.xml."""
import struct
import sys
import zipfile


def strings(buf, off):
    _, hsz, _, count, _, flags, sstart, _ = struct.unpack_from('<HHIIIIII', buf, off)
    utf8 = flags & 0x100
    offs = struct.unpack_from('<%dI' % count, buf, off + hsz)
    out = []
    for o in offs:
        p = off + sstart + o
        if utf8:
            n = buf[p]; p += 2 if n & 0x80 else 1
            n = buf[p]
            if n & 0x80:
                n = ((n & 0x7f) << 8) | buf[p + 1]; p += 2
            else:
                p += 1
            out.append(buf[p:p + n].decode('utf-8', 'replace'))
        else:
            n = struct.unpack_from('<H', buf, p)[0]; p += 2
            if n & 0x8000:
                n = ((n & 0x7fff) << 16) | struct.unpack_from('<H', buf, p)[0]; p += 2
            out.append(buf[p:p + 2 * n].decode('utf-16le', 'replace'))
    return out


def manifest(apk):
    buf = zipfile.ZipFile(apk).read('AndroidManifest.xml')
    off, pool, info = 8, [], {}
    while off < len(buf):
        typ, hsz, size = struct.unpack_from('<HHI', buf, off)
        if typ == 0x0001:
            pool = strings(buf, off)
        elif typ == 0x0102:  # start element
            name = pool[struct.unpack_from('<I', buf, off + 20)[0]]
            acount = struct.unpack_from('<H', buf, off + 28)[0]
            for i in range(acount):
                a = off + 36 + i * 20
                an = pool[struct.unpack_from('<I', buf, a + 4)[0]]
                raw, _, _, dtype, data = struct.unpack_from('<IHBBI', buf, a + 8)
                val = pool[raw] if raw != 0xffffffff else (pool[data] if dtype == 3 else data)
                if name == 'manifest' and an in ('package', 'versionCode', 'versionName'):
                    info[an] = val
                if name == 'uses-sdk' and an in ('minSdkVersion', 'targetSdkVersion'):
                    info[an] = val
            if name not in ('manifest', 'uses-sdk', 'uses-permission', 'permission'):
                if 'targetSdkVersion' in info or name == 'application':
                    break
        off += size
    return info


for apk in sys.argv[1:]:
    i = manifest(apk)
    print('%s\t%s\t%s\ttarget %s\t%s' % (i.get('package'), i.get('versionCode'), i.get('versionName'),
                                        i.get('targetSdkVersion'), apk))
