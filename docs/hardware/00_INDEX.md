# POCO F4 5G (munch) — hardware / firmware / drivers / architecture documentation

Start with `AUDIT_STATUS.md` (what is still true) and `subsystems/`: `POWER_THERMAL_PERF.md`, `MEMORY_SCHEDULING.md`, `DISPLAY_TOUCH.md`, `WIFI_MODEM_AUDIO.md`, `GNSS_SENSORS_POWER_STORAGE_SECURITY.md`, `KERNEL_BASE_COMPARISON.md`, `HYPEROS4_KERNEL_TARGET.md`. The driver sources, datasheets, device tree and raw dumps named below are on the pendrive `hardware_docs/`, not in this repo.

Built 2026-10-27 from the user's own phone (custom ROM T20261026, HyperOS 4 / Android 17, port kernel 4.19.325) and the matching kernel sources.
[Observed] = read from the phone; [Known] = general platform knowledge.

| Read this | What it answers |
|---|---|
| `SOC_ARCHITECTURE.md` | SoC and chip-by-chip architecture: CPU clusters, GPU, DSPs, ISP, modem, Wi-Fi/BT, PMICs, charging path, buses |
| `OS_ARCHITECTURE.md` | OS layers, boot chain, 123 partitions, SELinux/AVB, the VINTF HAL list (vendor/system/product/odm) |
| `hardware_inventory.md` (+ `.tsv`) | **Every device (1152)** on the phone -> bound kernel driver -> kernel source file -> Kconfig symbol -> device-tree node, grouped in 22 hardware categories |
| `hardware_nodes/` | Decoded live device-tree nodes of each category (the real properties: registers, GPIOs, rails, interrupts) |
| `live_devicetree.dts.zst` | The complete live merged device tree (4606 nodes) as text |
| `sensors/SENSORS_ARCHITECTURE.md` | All 57 sensors, the 6 chips (LSM6DSO, AK0991x, TCS3701, BU27030, SX932x/SX933x, Elliptic), the SLPI/SEE architecture, verbatim SEE chip configs (`sensors/config/*.json`) |
| `driver_sources/` | Kernel driver source code per category (25 archives, `README.md` lists directories), device-tree sources, kernel 4.19 `Documentation/`, defconfigs |
| `datasheets/` | Public datasheets that could be downloaded (+ `SOURCES.md` with links for the rest) |
| `upstream_reference/` | Upstream Linux 4.19 drivers/bindings of the same chip families (LSM6DSx, AK8975, SX9500, TCS3472, bq27xxx, NXP NCI, FT5x06) |
| `../this_phone_hardware_snapshot_2026-10-27/` | Raw dumps: kernel config, /proc, drivers by bus, firmware listing, thermal zones, dmesg (identifiers removed) |
| `../firmware_and_kernels/<version>/` | Kernel + firmware images of official MIUI 13 / MIUI 14 / HyperOS releases |

## Notes on accuracy
* Kernel config states in the inventory come from `/proc/config.gz`; on this port kernel some entries show "not set" for drivers that are clearly bound — treat the *driver binding* as truth.
* Sensors are handled by the SLPI DSP firmware (closed source); the repo holds the kernel glue, SEE JSON configs and public chip documentation, not the SEE chip drivers.
* Camera sensor/ISP/CAM-SS code is in `driver_sources/Camera_*`; the userspace camera stack (CamX/CHI) is binary (see the camera project notes in `project_docs`).
* Qualcomm kona hardware reference manuals and PMIC/camera-sensor datasheets are NDA-only and are not available publicly.
* `build_scripts/` regenerates the inventory from a connected phone and the kernel source tree.
