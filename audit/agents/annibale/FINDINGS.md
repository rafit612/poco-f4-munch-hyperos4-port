# Port (OS4.0.0.24) vs official annibale HyperOS 4 (OS4.0.0.34, MD5 verified)

Base: port is built on .24 (Aug 2026); official annibale is now .34 (Sep 2026), so many
file differences are just version drift. Full lists: changed_*.txt, portonly_*.txt, annonly_*.txt;
prop diffs: props/diff_*.txt.

| Partition  | identical | changed | port-only | official-only |
|------------|-----------|---------|-----------|---------------|
| system     | 2959 | 967  | 232 | 168  |
| system_ext | 2132 | 1087 | 53  | 178  |
| product    | 1136 | 141  | 72  | 365  |
| mi_ext     | 39   | 4    | 0   | 38   |
| odm        | 4    | 11   | 7   | 2952 (annibale hardware, irrelevant) |

## Porter-added props (not in official HyperOS 4 nor official munch 1.0.9)
- persist.sys.deviceidle.disable=true          -> Doze off (battery)
- ro.surface_flinger.set_{idle,touch,display_power}_timer_ms=2147483647 -> refresh-rate idle never drops
- persist.sys.enable_templimit=false           (official munch: true)
- persist.sys.mi.prerender / prestart.proc / PrereadEnable / PtePrereadEnable = false (official HyperOS 4: true)
- missing persist.sys.enhance_vkpipelinecache.enable=true and computilityV2.* (HyperOS 4 device-tier props)
- sys.keep_app_1..12 keep-alive list (porter's own apps: MT Manager, Via, Kuaishou, Mobile Legends, Termux, ...)
- persist.sys.shutdown.mode=hibernate, ro.config.hw_quickpoweron=true ("fast reboot")
- fake lock state: ro.boot.flash.locked=1, verifiedbootstate=green, warranty_bit=0, ro.crypto.state=encrypted
- persist.sys.kaorios=kousei, ro.mi.os.version.beta=true
- privapp permissions: official enforce -> port log (system_ext) / disable (product)
- media.stagefright.thumbnail.prefer_hw_codecs: official true -> port false

## Props that ARE official munch values (keep)
lcd_density 440, minfree_* tables, debug.sf.latch_unsignaled=1.

## Camera
- Port: com.android.camera 6.7.000070.0, signed "Android Debug" (modified build)
- Official HyperOS 4 annibale: 6.6.000570.5, Xiaomi-signed (built for annibale)
- Official munch HyperOS 1: 5.1.001140.0
Port system_ext also adds CameraMind 1.0.0.

## Other
- system/bin/hwservicemanager added (HIDL, needed by the old munch vendor).
- system_ext adds com.android.hardware.biometrics.fingerprint.virtual.apex (virtual fingerprint HAL) - check against the fingerprint retry loop.
