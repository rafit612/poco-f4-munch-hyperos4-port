# POCO F4 5G (munch) — SoC and hardware architecture (Snapdragon 870 5G, SM8250-AC, codename "kona")

Generated 2026-10-27. [Observed] = read from the phone, [Known] = general platform knowledge (Qualcomm public spec), to be checked against datasheets.

| Block | Facts |
|---|---|
| SoC | `chip_name SM8250`, family Snapdragon, hw_platform MUNCH, DT compatible `qcom,kona-mtp / qcom,kona` (3 revisions in vendor_boot: v1, v2, v2.1) [Observed] |
| CPU | 8 cores, 3 clusters by maximum frequency [Observed]: 4× 1.80 GHz, 3× 2.42 GHz, 1× 3.19 GHz; implementer/part ids seen: 0x805, 0xd0d (0x805 = Qualcomm Kryo 4xx Silver, A55-based, the 4 little cores; 0xd0d = Arm Cortex-A77, the 3 gold + 1 prime cores) [Observed from /proc/cpuinfo]; marketed as Kryo 585 (1 prime A77 + 3 gold A77 + 4 silver A55) [Known]; governor schedutil |
| CPU features | fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics fphp asimdhp cpuid asimdrdm lrcpc dcpop asimddp |
| GPU | gpu_model: Adreno650v3; max clock 670 MHz, 7 power levels; devfreq governor msm-adreno-tz; driver `kgsl` (drivers/gpu/msm) [Observed] |
| Memory | MemTotal 7776688 kB (8 GB LPDDR5 [Known]); zram swap; LLCC cache controller; ARM SMMU (IOMMU) ×3 |
| Storage | UFS 3.1 host `ufshcd-qcom` (+ QMP v4 PHY + ICE inline encryption) [Observed] |
| DSPs | aDSP (audio), cDSP (compute / NPU path, HVX), SLPI (sensors), modem DSP [Observed: subsystem devices, see hardware_inventory "Remote processors"]; Hexagon 698 [Known] |
| ISP / camera | Spectra 480 (CAM-SS: cam-cpas, cam-icp/a5, cci, csiphy, ife, jpeg, lrme…) [Observed]; sensors OV64B40 (main), OV8856 (UW), GC02M1 (macro), IMX596 (front) |
| Display | MDSS/DPU (sde), 2 DSI controllers + PHY + PLL, SDE resource state coordinator; panel via `qcom,dsi-display-primary` [Observed] |
| Modem / connectivity | Snapdragon X55 5G modem (MHI ×34 devices, IPA) [Observed/Known]; Wi-Fi + Bluetooth: Qualcomm QCA6390 (cnss2 PCIe, bt_qca6390, btfmslim) [Observed]; NFC NXP-class `nq-nci` [Observed] |
| PMICs | pm8008, pm8009, pm8150, pm8150b, pm8150l, pmxprairie on SPMI (+ pm8008 camera PMICs on I2C) [Observed] |
| Power path | battery Li-poly design 4500 mAh [Observed]; fuel gauge `bq27z561`; charge pumps `ln8000` master/slave + `bq2597x` + SMB1390; wireless input `dc`; USB `pc_port`/`usb`; thermal: 93 thermal zones, tsens ×2, LMH limits DCVS |
| Haptics / input | AW8697 haptic driver (×2 buses), QTI haptics, FocalTech touch `fts_ts` (SPI), Xiaomi touch feature, fingerprint FPC/Goodix platform entries, gpio-keys, qpnp-power-on |
| Audio | WCD938x codec + TFA98xx smart amps (see inventory "Audio"), ADSP audio via q6 (techpack/audio) |
| Buses | SPMI, I2C ×19 devices, SPI, SLIMbus, PCIe (Wi-Fi), MHI (modem), USB3/DP, UFS |

## Where to look next
* `hardware_inventory.md` / `.tsv`: every device -> live driver -> kernel source file -> Kconfig -> DT node (1152 devices).
* `hardware_nodes/`: decoded device-tree nodes per hardware category.
* `live_devicetree.dts.zst`: the complete live device tree.
* `sensors/SENSORS_ARCHITECTURE.md`: the 57 sensors and the SLPI/SEE design.
* `driver_sources/`: kernel driver source trees per category (+ device-tree sources, + kernel `Documentation/`).
* `datasheets/`: public datasheets of the main chips (+ `SOURCES.md`).
* `../this_phone_hardware_snapshot_2026-10-27/`: raw kernel config, /proc dumps, firmware listing, thermal zones, sensors.
