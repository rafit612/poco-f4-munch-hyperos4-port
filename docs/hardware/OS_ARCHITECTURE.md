# POCO F4 5G (munch) — operating-system architecture

Generated 2026-10-27 from the live phone running the custom ROM T20261026 (HyperOS 4.0.0.24 / Android 17, build CP2A.260605.016).

## Layers
```
Apps / HyperOS framework (system, system_ext, product, mi_ext)            Android 17 + HyperOS 4 + Xiaomi 17 Global layer
  |  Binder / AIDL / HIDL  (VINTF: system manifest <-> vendor manifest, 77 HAL entries below)
Vendor layer (vendor, odm)  — official POCO F4 HyperOS 1.0.9 hardware layer: HALs, CamX/CHI camera, audio, sensors, modem, GPU blobs
  |  device nodes, sysfs, netlink, ioctl
Linux kernel 4.19 (port kernel 4.19.325-zyndong-perf; stock HyperOS 1.0.9 kernel = 4.19.157)   drivers: see hardware_inventory.md
  |  DT (vendor_boot dtb + dtbo overlay), PIL / remoteproc / glink / QMI / IPC router
Firmware blobs on the SoC: modem (X55 DSP + ARM), aDSP, cDSP (HVX/NPU), SLPI (sensors), venus (video), IPA, GPU ZAP, TrustZone, hypervisor
  |
Boot chain: PBL (ROM) -> XBL (xbl.img, xbl_config) -> ABL (UEFI, abl.img) -> boot.img + vendor_boot.img + dtbo.img (header v3) -> kernel -> init
```
* Boot images [Observed]: `boot.img` = kernel + generic ramdisk; `vendor_boot.img` = vendor ramdisk (tiny, no modules) + dtb of the 3 Kona SoC revisions; `dtbo.img` = board overlays (munch).
  The live device tree is base DT + munch overlay (`live_devicetree.dts`).
* Partitions: UFS 3.1, 6 LUNs, A/B slots; logical (dynamic) partitions system, system_ext, product, vendor, odm, mi_ext live inside `super`; userdata is file-based encrypted.
* Security [Observed]: SELinux enforcing; policy compiled on the device at every boot (product CIL + mapping); AVB/vbmeta; privapp permission allowlist enforced.
* Kernel command line (identifiers removed): `cgroup_disable=pressure ramoops_memreserve=4M rcupdate.rcu_expedited=1 rcu_nocbs=0-7 kpti=off console=ttyMSM0,115200n8 androidboot.hardware=qcom androidboot.console=ttyMSM0 androidboot.memcg=1 lpm_levels.sleep_disabled=1 video=vfb:640x400,bpp=32,memsize=3072000 msm_rtb.filter=0x237 service_locator.enable=1 androidboot.usbcontroller=a600000.dwc3 swiotlb=2048 loop.max_part=7 cgroup.memory=nokmem,nosocket reboot=panic_warm buildvariant=user  androidboot.verifiedbootstate=orange androidboot.keymaster=1  androidboot.bootdevice=1d84000.ufshc androidboot.fstab_suffix=default androidboot.boot_devices=soc/1d84000.ufshc androidboot.serialno=<REDACTED> androidboot.secureboot=1 androidboot.hwversion=F.1`
* `/proc/version`: `Linux version 4.19.325-zyndong-perf-g7e817c4ca270 (runner@runnervmlun5p) (ZyC clang version 16.0.6 (https://github.com/llvm/llvm-project 7cbf1a2591520c2491aa35339f227775f4d3adf6), LLD 16.0.6) #1 SMP PREEMPT Thu Sep 10 15:16:03 UTC 2026`

## Partitions by name (123)
| Name | Block device |
|---|---|
| ALIGN_TO_128K_1 | /dev/block/sdd1 |
| ALIGN_TO_128K_2 | /dev/block/sdf1 |
| abl_a | /dev/block/sde9 |
| abl_b | /dev/block/sde34 |
| aop_a | /dev/block/sde1 |
| aop_b | /dev/block/sde26 |
| apdp | /dev/block/sde55 |
| bk01 | /dev/block/sda4 |
| bk010 | /dev/block/sda32 |
| bk02 | /dev/block/sda5 |
| bk03 | /dev/block/sda6 |
| bk04 | /dev/block/sda7 |
| bk06 | /dev/block/sda12 |
| bk08 | /dev/block/sda19 |
| bk09 | /dev/block/sda21 |
| bk41_a | /dev/block/sde2 |
| bk41_b | /dev/block/sde27 |
| bk42 | /dev/block/sde51 |
| bk43 | /dev/block/sde52 |
| bk44 | /dev/block/sde53 |
| bk51 | /dev/block/sdf6 |
| bluetooth_a | /dev/block/sde6 |
| bluetooth_b | /dev/block/sde31 |
| boot_a | /dev/block/sde12 |
| boot_b | /dev/block/sde37 |
| cdt | /dev/block/sdd2 |
| cmnlib64_a | /dev/block/sde14 |
| cmnlib64_b | /dev/block/sde39 |
| cmnlib_a | /dev/block/sde13 |
| cmnlib_b | /dev/block/sde38 |
| countrycode | /dev/block/sda10 |
| cust | /dev/block/sda28 |
| dbg | /dev/block/sda3 |
| ddr | /dev/block/sdd3 |
| devcfg_a | /dev/block/sde15 |
| devcfg_b | /dev/block/sde40 |
| devinfo | /dev/block/sda16 |
| dip | /dev/block/sde54 |
| dsp_a | /dev/block/sde10 |
| dsp_b | /dev/block/sde35 |
| dtbo_a | /dev/block/sde18 |
| dtbo_b | /dev/block/sde43 |
| featenabler_a | /dev/block/sde23 |
| featenabler_b | /dev/block/sde48 |
| ffu | /dev/block/sda14 |
| frp | /dev/block/sda9 |
| fsc | /dev/block/sdf5 |
| fsg | /dev/block/sdf4 |
| gsort | /dev/block/sde56 |
| hyp_a | /dev/block/sde4 |
| hyp_b | /dev/block/sde29 |
| imagefv_a | /dev/block/sde24 |
| imagefv_b | /dev/block/sde50 |
| keymaster_a | /dev/block/sde11 |
| keymaster_b | /dev/block/sde36 |
| keystore | /dev/block/sda8 |
| limits | /dev/block/sde59 |
| limits-cdsp | /dev/block/sde60 |
| logdump | /dev/block/sda25 |
| logfs | /dev/block/sda13 |
| mdm1m9kefs1 | /dev/block/sdf8 |
| mdm1m9kefs2 | /dev/block/sdf9 |
| mdm1m9kefs3 | /dev/block/sdf7 |
| mdm1m9kefsc | /dev/block/sdf10 |
| mdmddr | /dev/block/sdd4 |
| mdtp_a | /dev/block/sde8 |
| mdtp_b | /dev/block/sde33 |
| mdtpsecapp_a | /dev/block/sde7 |
| mdtpsecapp_b | /dev/block/sde32 |
| metadata | /dev/block/sda18 |
| minidump | /dev/block/sda26 |
| misc | /dev/block/sda11 |
| modem_a | /dev/block/sde5 |
| modem_b | /dev/block/sde30 |
| modemst1 | /dev/block/sdf2 |
| modemst2 | /dev/block/sdf3 |
| msadp | /dev/block/sde57 |
| mtdblk | /dev/block/sda24 |
| multiimgoem_a | /dev/block/sde20 |
| multiimgoem_b | /dev/block/sde45 |
| multiimgqti_a | /dev/block/sde21 |
| multiimgqti_b | /dev/block/sde46 |
| oem_misc1 | /dev/block/sda17 |
| oops | /dev/block/sda15 |
| persist | /dev/block/sda22 |
| persistbak | /dev/block/sda23 |
| qupfw_a | /dev/block/sde16 |
| qupfw_b | /dev/block/sde41 |
| rawdump | /dev/block/sda27 |
| rescue | /dev/block/sda33 |
| sda | /dev/block/sda |
| sdb | /dev/block/sdb |
| sdc | /dev/block/sdc |
| sdd | /dev/block/sdd |
| sde | /dev/block/sde |
| sdf | /dev/block/sdf |
| secdata | /dev/block/sde63 |
| splash | /dev/block/sda20 |
| spunvm | /dev/block/sde58 |
| ssd | /dev/block/sda2 |
| storsec | /dev/block/sde61 |
| super | /dev/block/sda29 |
| switch | /dev/block/sda1 |
| tz_a | /dev/block/sde3 |
| tz_b | /dev/block/sde28 |
| uefisecapp_a | /dev/block/sde19 |
| uefisecapp_b | /dev/block/sde44 |
| uefivarstore | /dev/block/sde62 |
| userdata | /dev/block/sda34 |
| vbmeta_a | /dev/block/sde17 |
| vbmeta_b | /dev/block/sde42 |
| vbmeta_system_a | /dev/block/sda30 |
| vbmeta_system_b | /dev/block/sda31 |
| vendor_boot_a | /dev/block/sde25 |
| vendor_boot_b | /dev/block/sde49 |
| vm-data | /dev/block/sde65 |
| vm-keystore | /dev/block/sde64 |
| vm-linux_a | /dev/block/sde22 |
| vm-linux_b | /dev/block/sde47 |
| xbl_a | /dev/block/sdb1 |
| xbl_b | /dev/block/sdc1 |
| xbl_config_a | /dev/block/sdb2 |
| xbl_config_b | /dev/block/sdc2 |

## Treble / VINTF HAL entries (77)
| Manifest | Format | HAL | Version/FQName | Interfaces |
|---|---|---|---|---|
| system | hidl | `android.hidl.manager` | @1.2::IServiceManager/default |  |
| system | hidl | `android.hidl.token` | @1.0::ITokenManager/default |  |
| system | aidl | `android.frameworks.sensorservice` | ISensorManager/default |  |
| system | hidl | `android.frameworks.sensorservice` | @1.0::ISensorManager/default |  |
| system | hidl | `android.hidl.memory` | @1.0::IMapper/ashmem |  |
| system | hidl | `android.system.net.netd` | @1.1::INetd/default |  |
| system | hidl | `android.system.wifi.keystore` | @1.0::IKeystore/default |  |
| system | native | `netutils-wrapper` | 1.0 |  |
| system | hidl | `vendor.qti.hardware.qccsyshal` | @1.2::IQccsyshal/qccsyshal |  |
| system | hidl | `vendor.qti.hardware.radio.atcmdfwd` | @1.0::IAtCmdFwd/AtCmdFwdService |  |
| system | hidl | `vendor.qti.hardware.systemhelper` | @1.0::ISystemEvent/default,@1.0::ISystemResource/default |  |
| vendor | hidl | `android.hardware.audio` | 6.0 | IDevicesFactory |
| vendor | hidl | `android.hardware.audio.effect` | 6.0 | IEffectsFactory |
| vendor | hidl | `android.hardware.bluetooth` | 1.0 | IBluetoothHci |
| vendor | hidl | `android.hardware.bluetooth.audio` | 2.0 | IBluetoothAudioProvidersFactory |
| vendor | hidl | `android.hardware.camera.provider` | 2.4 | ICameraProvider |
| vendor | hidl | `android.hardware.gatekeeper` | 1.0 | IGatekeeper |
| vendor | hidl | `android.hardware.ir` | 1.0 | IConsumerIr |
| vendor | hidl | `android.hardware.keymaster` | 4.0 | IKeymasterDevice |
| vendor | hidl | `android.hardware.media.omx` | 1.0 | IOmx,IOmxStore |
| vendor | hidl | `android.hardware.memtrack` | 1.0 | IMemtrack |
| vendor | hidl | `android.hardware.nfc` | 1.2 | INfc |
| vendor | hidl | `android.hardware.radio` | @1.2::ISap/slot1,@1.2::ISap/slot2,@1.5::IRadio/slot1,@1.5::IRadio/slot2 |  |
| vendor | hidl | `android.hardware.radio.config` | 1.1 | IRadioConfig |
| vendor | hidl | `android.hardware.secure_element` | 1.2 | ISecureElement |
| vendor | hidl | `android.hardware.sensors` | 1.0 | ISensors |
| vendor | hidl | `android.hardware.soundtrigger` | 2.3 | ISoundTriggerHw |
| vendor | hidl | `android.hardware.tetheroffload.config` | 1.0 | IOffloadConfig |
| vendor | hidl | `android.hardware.tetheroffload.control` | 1.0 | IOffloadControl |
| vendor | hidl | `com.qualcomm.qti.bluetooth_audio` | 1.0 | IBluetoothAudio |
| vendor | hidl | `com.qualcomm.qti.dpm.api` | 1.0 | IdpmQmi |
| vendor | hidl | `vendor.nxp.hardware.nfc` | 2.0 | INqNfc |
| vendor | hidl | `vendor.qti.data.factory` | 2.2 | IFactory |
| vendor | hidl | `vendor.qti.esepowermanager` | 1.1 | IEsePowerManager |
| vendor | hidl | `vendor.qti.hardware.alarm` | 1.0 | IAlarm |
| vendor | hidl | `vendor.qti.hardware.audiohalext` | 1.0 | IAudioHalExt |
| vendor | hidl | `vendor.qti.hardware.bluetooth_audio` | 2.0 | IBluetoothAudioProvidersFactory |
| vendor | hidl | `vendor.qti.hardware.bluetooth_sar` | 1.1 | IBluetoothSar |
| vendor | hidl | `vendor.qti.hardware.btconfigstore` | 1.0 | IBTConfigStore |
| vendor | hidl | `vendor.qti.hardware.cacert` | 1.0 | IService |
| vendor | hidl | `vendor.qti.hardware.camera.postproc` | 1.0 | IPostProcService |
| vendor | hidl | `vendor.qti.hardware.capabilityconfigstore` | 1.0 | ICapabilityConfigStore |
| vendor | hidl | `vendor.qti.hardware.data.connection` | 1.1 | IDataConnection |
| vendor | hidl | `vendor.qti.hardware.data.iwlan` | 1.0 | IIWlan |
| vendor | hidl | `vendor.qti.hardware.data.latency` | 1.0 | ILinkLatency |
| vendor | hidl | `vendor.qti.hardware.dsp` | 1.0 | IDspService |
| vendor | hidl | `vendor.qti.hardware.factory` | 1.1 | IFactory |
| vendor | hidl | `vendor.qti.hardware.iop` | 2.0 | IIop |
| vendor | hidl | `vendor.qti.hardware.perf` | 2.2 | IPerf |
| vendor | hidl | `vendor.qti.hardware.qccvndhal` | 1.0 | IQccvndhal |
| vendor | hidl | `vendor.qti.hardware.qseecom` | 1.0 | IQSEECom |
| vendor | hidl | `vendor.qti.hardware.qteeconnector` | 1.0 | IAppConnector,IGPAppConnector |
| vendor | hidl | `vendor.qti.hardware.radio.am` | 1.0 | IQcRilAudio |
| vendor | hidl | `vendor.qti.hardware.radio.ims` | 1.7 | IImsRadio |
| vendor | hidl | `vendor.qti.hardware.radio.internal.deviceinfo` | 1.0 | IDeviceInfo |
| vendor | hidl | `vendor.qti.hardware.radio.lpa` | 1.0 | IUimLpa |
| vendor | hidl | `vendor.qti.hardware.radio.qcrilhook` | 1.0 | IQtiOemHook |
| vendor | hidl | `vendor.qti.hardware.radio.qtiradio` | 1.0 | IQtiRadio |
| vendor | hidl | `vendor.qti.hardware.radio.qtiradio` | 2.4 | IQtiRadio |
| vendor | hidl | `vendor.qti.hardware.radio.uim` | 1.2 | IUim |
| vendor | hidl | `vendor.qti.hardware.radio.uim_remote_client` | 1.0 | IUimRemoteServiceClient |
| vendor | hidl | `vendor.qti.hardware.radio.uim_remote_server` | 1.0 | IUimRemoteServiceServer |
| vendor | hidl | `vendor.qti.hardware.sensorscalibrate` | 1.0 | ISensorsCalibrate |
| vendor | hidl | `vendor.qti.hardware.soter` | 1.0 | ISoter |
| vendor | hidl | `vendor.qti.hardware.tui_comm` | 1.0 | ITuiComm |
| vendor | hidl | `vendor.qti.hardware.vpp` | 1.3 | IHidlVppService |
| vendor | hidl | `vendor.qti.hardware.wifi.wifilearner` | 1.0 | IWifiStats |
| vendor | hidl | `vendor.qti.hardware.wifidisplaysession` | 1.0 | IWifiDisplaySession,IWifiDisplaySessionAudioTrack,IWifiDispl |
| vendor | hidl | `vendor.qti.imsrtpservice` | 3.0 | IRTPService |
| vendor | hidl | `vendor.qti.qspmhal` | 1.0 | IQspmhal |
| vendor | hidl | `vendor.qti.sla.service` | 1.0 | ISlaService |
| vendor | hidl | `vendor.xiaomi.hardware.citsensorservice` | 1.1 | ICitSensorService |
| vendor | hidl | `vendor.xiaomi.hardware.citvendorservice` | 1.0 | ICitVendorService |
| vendor | hidl | `vendor.xiaomi.hardware.displayfeature` | 1.0 | IDisplayFeature |
| vendor | hidl | `vendor.xiaomi.hardware.fingerprintextension` | 1.0 | IXiaomiFingerprint |
| vendor | hidl | `vendor.xiaomi.hardware.fx.tunnel` | 1.0 | IMiFxTunnel |
| vendor | hidl | `vendor.xiaomi.hardware.touchfeature` | 1.0 | ITouchFeature |
