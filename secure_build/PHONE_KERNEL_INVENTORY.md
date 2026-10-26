# Phone kernel inventory — porter kernel vs our kernel v4

Snapshot taken 2026-10-24 from the running phone (porter kernel `4.19.325-zyndong-perf`), read-only, stored in
`~/kernel_build/phone_snapshot/`. Compared with kernel v4 (`secure_build/kernel_v4/`, source `rohmanurip/kernel_munch`).
Method and tools: live `/proc/kallsyms`, live dtb (`/sys/firmware/fdt`), `/sys/bus/*/drivers`, the porter's saved boot log
(`/data/adb/ksu/log/dmesg.log`), `tools/kallsyms_dump.py`, `llvm-nm` on the vendor modules, strings of both kernel Images.

## Summary
| Check | Porter (boots) | v4 | Verdict |
|---|---|---|---|
| Drivers running on the phone | 252 | 248 present | 4 missing, none needed for boot (table below) |
| Enabled device-tree devices with a matching driver | 741 of 821 | 734 of 821 | 10 differences, 5 of them used (below) |
| Firmware images loaded at boot | 20 | all 20 names requested | no risk |
| Vendor modules (`/vendor/lib/modules`, 48, built for 4.19.157) | none loaded (`/proc/modules` empty) | none will load | same on both |
| Boot, vendor_boot, dtbo on slots A and B | byte-identical to the port's originals | — | nothing half-written left |
| Firmware partitions | slot A = slot B for all | — | XBL `BOOT.XF.3.2-00354`, TZ/HYP `TZ.XF.5.8-00274`, AOP `AOP.HO.2.0-00194`, ADSP/modem `ADSP.HT.5.3-00614`, BT `BTFM.HST.1.0.0-00218` |

Hardware coverage does not explain the v2/v3 boot hangs: every driver the phone needs to start is present in v4.

## Drivers running on the porter that v4 lacks
| Driver | Hardware | Effect with v4 | Fix |
|---|---|---|---|
| `ir-spi` | IR blaster (`/dev/ir_spi`) | IR remote does not work | our `drivers/media/rc/ir-spi.c` only matches `ir-spi-led`; add `ir-spi` to its match table |
| `qcom_ice` | inline crypto engine of the UFS **card** controller (`ufscardice@1db0000`) | none (no card slot); main storage encryption uses `QTI_CRYPTO` in the UFS driver, which v4 has | optional: `CONFIG_CRYPTO_DEV_QCOM_ICE=y` |
| `cpu_isolate` | WALT CPU isolation | none (v4 uses CASS) | — |
| `md-testing-mode` | Xiaomi modem factory test | none in normal use | not in our source |

Device-tree devices the porter supports but no driver uses on this phone: DCC and SPMI debug, DisplayPort PLL,
boot_stats, MPM sleep counter, Kryo cache error reporting (debug or unused hardware).

## Subsystems in the porter kernel that v4 does not have
| Family | What | Matters? |
|---|---|---|
| `millet` | Xiaomi app-freeze framework (binder/netlink hooks, `ro.millet.netlink=31`) | Not for boot. `persist.sys.powmillet.enable=false` on this ROM, but HyperOS power management may use it; check battery behaviour on v4 |
| `walt`, `schedtune` | porter's scheduler | Replaced by CASS + uclamp; vendor scripts writing WALT knobs will fail harmlessly |
| `bfq`, `kyber`, `deadline` | blk-mq I/O schedulers | v4 has noop and cfq; Android's scheduler writes fail harmlessly |
| `rtc6226` (FM), `ch101` (ultrasonic), `qbt` (ultrasonic fingerprint), `nanosic` (keyboard) | drivers present but **0 devices** bound on this phone | No |
| `mmc`, `sdhci`, `cqhci`, `dvb`, `tuner`, USB-Ethernet, `wacom`, `wiimote`, `l2tp`, `ppp`, `edac`, `kfence` | unused hardware or extras | No |

v4 has extra: KernelSU (rsuntk), BBR, CASS/uclamp, Synaptics touch, Wolfson and Cirrus CS35L41 codecs, AW22xxx LED.

## Vendor modules
All 48 modules are built for `4.19.157-perf-g045c5942d886`, so neither kernel loads them (version magic differs).
Audio (26 modules), Wi-Fi qca6390/qca6490, fingerprint `fpc1540`/`gf_spi` and exFAT are **built into both kernels**.
Missing in both: `rmnet_shs`/`rmnet_perf` (mobile-data packet steering: data works, slightly more CPU at high speed),
`llcc_perfmon`, `gspca_main`, `mpq-*` (TV tuner), `rdbg`, `fragmentize`.

## Firmware loaded at boot (porter boot log)
GPU `a650_sqe.fw`, `a650_gmu`, `a650_zap`; DSPs `adsp`, `cdsp`, `slpi`, `npu`, `cvpss`; video `venus`; camera `CAMERA_ICP`;
IPA `ipa_fws`, `ipa_uc`; Wi-Fi `qca6390/amss20`, `bd_l11rgl`, `m3`, `regdb`; 5G modem `sdx55m/sbl1`;
touch `focaltech_ts_fw` (replacement panel); haptics `aw8697_haptic`; amplifier `tfa98xx.cnt`. v4 requests every one by the same name.

## What this means for the next build
1. Hardware support is not the reason v2/v3 hung; the crash log from v4 (`PANIC_ON_OOPS` + ramoops records) is still
   needed to find the real cause.
2. Two small fixes to fold into the next build: the IR blaster match (`ir-spi`) and optionally the card ICE driver.
3. The porter's boot log (`phone_snapshot/boot_dmesg_porter.txt`, 5,202 lines) is the reference for a line-by-line
   comparison with v4's first boot.
