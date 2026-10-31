# POCO F4 5G (munch) — sensors: list, chips, architecture

Generated 2026-10-27 from the live phone (`dumpsys sensorservice`, `/vendor/etc/sensors/config`, DT, kernel config). Tags: [Observed] = read from the phone, [Known] = general platform knowledge.

## 1. Architecture (how a sensor reading reaches an app)
```
 physical chip (LSM6DSO, AK0991x, TCS3701, BU27030, SX932x/SX933x)
      |  I2C / SPI + interrupt GPIO + power rails                 (wired to the SLPI, not to the Linux kernel)
      v
 SLPI  = Qualcomm "Sensor Low Power Island" Hexagon DSP, firmware slpi.mdt (loaded by the kernel with PIL)
      |  SEE = Sensors Execution Environment: one driver library per chip (sns_*), plus algorithms
      |  (step detector, pedometer, tilt, significant motion, rotation vector, gravity, SAR, pickup, pocket mode, AOD, HAR …)
      |  settings of every physical sensor: /vendor/etc/sensors/config/sm8250_<chip>_0.json  (see section 4)
      v
 glink / QRTR transport  --(kernel: drivers/rpmsg, drivers/soc/qcom/glink, subsys PIL)-->  vendor sensors HAL process
      v
 Android sensors HAL (multi-HAL, libssc / sensors.ssc, Xiaomi additions)  -->  SensorService (system_server)  -->  apps
```
* [Observed] 65 logical sensors are published (many are wake-up / non-wake-up pairs of the same sensor, and software "virtual" sensors).
* [Observed] The Linux kernel has **no driver bound to these chips**: its only sensor-related platform device is `soc:qcom,msm-ssc-sensors`
  (driver `sensors-ssc`, source `drivers/sensors/sensors_ssc.c`), which powers/boots the SLPI and handles its restarts. The IIO devices
  that exist (`iio:device0..2`) are the PMIC ADCs (`qcom-spmi-adc5`), i.e. battery/skin temperature, not motion sensors.
* [Known] The SEE chip drivers are closed-source binaries inside the SLPI firmware image (`slpi.mdt`/`slpi.bNN`). What is open is: the kernel glue
  (included in this archive), the JSON register/bus configuration (below), and the HAL interface headers of the Qualcomm sensors HAL.
* [Observed] Touch, fingerprint, haptics, NFC and the charger are different: they ARE Linux drivers (see `hardware_inventory.md`).

## 2. Physical sensor chips
| Chip | Role | SEE config file(s) |
|---|---|---|
| STMicroelectronics LSM6DSO | accelerometer + gyroscope (6-axis IMU) | sm8250_lsm6dso_0.json, lsm6dso_0.json |
| AKM AK0991x (AK09918-class) | magnetometer | sm8250_ak991x_0.json, ak991x_dri_0.json |
| ams TCS3701 | ambient light, front colour temperature (CCT), optical proximity | sm8250_tcs3701.json |
| ROHM BU27030 | rear ambient light / lux (colour + flicker for the camera) | sm8250_bu27030_0_back.json, bu27030_0_back.json |
| Semtech SX932x / SX933x | SAR (capacitive body-proximity for antenna power) — two chips | sm8250_sx932x_0.json, sm8250_sx933x_0.json |
| Elliptic Labs | ultrasonic virtual proximity sensor (software, uses the speaker/mic) | — |

## 3. All 65 sensors reported by SensorService
| Handle | Name | Vendor | Android type | |
|---|---|---|---|---|
| 0x00000001 | Elliptic Proximity | Elliptic Labs | `android.sensor.proximity` |  |
| 0x00000002 | step_detector  Wakeup | XiaoMi(V2.14) | `android.sensor.step_detector` | wakeup |
| 0x00000003 | step_detector  Non-wakeup | XiaoMi(V2.14) | `android.sensor.step_detector` | wakeup |
| 0x00000004 | pedometer  Wakeup | qualcomm | `android.sensor.step_counter` | wakeup |
| 0x00000005 | pedometer  Non-wakeup | qualcomm | `android.sensor.step_counter` | wakeup |
| 0x00000006 | stationary_detect_wakeup | qualcomm | `android.sensor.stationary_detect` | wakeup |
| 0x00000007 | stationary_detect | qualcomm | `android.sensor.stationary_detect` |  |
| 0x00000008 | sns_smd  Wakeup | qualcomm | `android.sensor.significant_motion` | wakeup |
| 0x00000009 | screen_down  Wakeup | XiaoMi(V3.6.2) | `xiaomi.sensor.screen_down` | wakeup |
| 0x0000000a | screen_down  Non-wakeup | XiaoMi(V3.6.2) | `xiaomi.sensor.screen_down` | wakeup |
| 0x0000000b | semtech_sx933x_0  Non-wakeup | Semtech | `xiaomi.sensor.sar_secondary` | wakeup |
| 0x0000000c | sar_detector_1  Wakeup | xiaomi | `xiaomi.sensor.sar_algo_1` | wakeup |
| 0x0000000d | sar_detector_1  Non-wakeup | xiaomi | `xiaomi.sensor.sar_algo_1` | wakeup |
| 0x0000000e | ccd_tilt  Wakeup | qualcomm | `android.sensor.tilt_detector` | wakeup |
| 0x0000000f | semtech_sx932x_0  Non-wakeup | Semtech | `xiaomi.sensor.sar` | wakeup |
| 0x00000010 | Rotation Vector  Non-wakeup | qualcomm | `android.sensor.rotation_vector` | wakeup |
| 0x00000011 | orientation  Non-wakeup | xiaomi | `android.sensor.orientation` | wakeup |
| 0x00000012 | tcs3701 Ambient Light Sensor Wakeup | ams AG | `android.sensor.light` | wakeup |
| 0x00000013 | tcs3701 Ambient Light Sensor Non-wakeup | ams AG | `android.sensor.light` | wakeup |
| 0x00000014 | pocket_mode  Wakeup | XiaoMi(V2.7) | `xiaomi.sensor.oem_pocket` | wakeup |
| 0x00000015 | pocket_mode  Non-wakeup | XiaoMi(V2.7) | `xiaomi.sensor.oem_pocket` | wakeup |
| 0x00000016 | NonUi  Wakeup | XiaoMi(V2.7) | `xiaomi.sensor.nonui` | wakeup |
| 0x00000017 | NonUi  Non-wakeup | XiaoMi(V2.7) | `xiaomi.sensor.nonui` | wakeup |
| 0x00000018 | pickup  Wakeup | XiaoMi | `xiaomi.sensor.pickup` | wakeup |
| 0x00000019 | pickup  Non-wakeup | XiaoMi | `xiaomi.sensor.pickup` | wakeup |
| 0x0000001a | oem13_light_smd  Wakeup | XiaoMi(V3.34) | `xiaomi.sensor.oem13` | wakeup |
| 0x0000001b | oem13_light_smd  Non-wakeup | XiaoMi(V3.34) | `xiaomi.sensor.oem13` | wakeup |
| 0x0000001c | motion_detect_wakeup | qualcomm | `android.sensor.motion_detect` | wakeup |
| 0x0000001d | motion_detect | qualcomm | `android.sensor.motion_detect` |  |
| 0x0000001e | tcs3701  Non-wakeup | ams AG | `xiaomi.sensor.ambientlight.factory` | wakeup |
| 0x0000001f | ak0991x Magnetometer-Uncalibrated Non-wakeup | akm | `android.sensor.magnetic_field_uncalibrated` | wakeup |
| 0x00000020 | ois_manager  Wakeup | Xiaomi | `xiaomi.sensor.ois_sensor` | wakeup |
| 0x00000021 | ois_manager  Non-wakeup | Xiaomi | `xiaomi.sensor.ois_sensor` | wakeup |
| 0x00000022 | ak0991x Magnetometer Non-wakeup | akm | `android.sensor.magnetic_field` | wakeup |
| 0x00000023 | linear_acceleration | qualcomm | `android.sensor.linear_acceleration` |  |
| 0x00000024 | har_wakeup | xiaomi | `xiaomi.sensor.har` | wakeup |
| 0x00000025 | har | xiaomi | `xiaomi.sensor.har` |  |
| 0x00000026 | gravity  Non-wakeup | qualcomm | `android.sensor.gravity` | wakeup |
| 0x00000027 | sns_geomag_rv  Non-wakeup | qualcomm | `android.sensor.geomagnetic_rotation_vector` | wakeup |
| 0x00000028 | Game Rotation Vector  Non-wakeup | qualcomm | `android.sensor.game_rotation_vector` | wakeup |
| 0x00000029 | lsm6dso Gyroscope Non-wakeup | STMicro | `android.sensor.gyroscope` | wakeup |
| 0x0000002a | Aod  Wakeup | XiaoMi | `xiaomi.sensor.aod` | wakeup |
| 0x0000002b | Aod  Non-wakeup | XiaoMi | `xiaomi.sensor.aod` | wakeup |
| 0x0000002c | device_orient  Wakeup | xiaomi | `android.sensor.device_orientation` | wakeup |
| 0x0000002d | device_orient  Non-wakeup | xiaomi | `android.sensor.device_orientation` | wakeup |
| 0x0000002e | tcs3701 front CCT stream  Non-wakeup | ams AG | `xiaomi.sensor.front_cct_strm` | wakeup |
| 0x0000002f | tcs3701 front CCT  Wakeup | ams AG | `xiaomi.sensor.front_cct` | wakeup |
| 0x00000030 | tcs3701 front CCT  Non-wakeup | ams AG | `xiaomi.sensor.front_cct` | wakeup |
| 0x00000031 | rohm_bu27030_back  Wakeup | Rohm | `xiaomi.sensor.back_lux` | wakeup |
| 0x00000032 | rohm_bu27030_back  Non-wakeup | Rohm | `xiaomi.sensor.back_lux` | wakeup |
| 0x00000033 | rohm_bu27030_back  Non-wakeup | Rohm | `xiaomi.sensor.back_lux_strm` | wakeup |
| 0x00000034 | sar_detector  Wakeup | xiaomi | `xiaomi.sensor.sar_algo` | wakeup |
| 0x00000035 | sar_detector  Non-wakeup | xiaomi | `xiaomi.sensor.sar_algo` | wakeup |
| 0x00000036 | lsm6dso Accelerometer-Uncalibrated Non-wakeup | STMicro | `android.sensor.accelerometer_uncalibrated` | wakeup |
| 0x00000037 | lsm6dso Gyroscope-Uncalibrated Non-wakeup | STMicro | `android.sensor.gyroscope_uncalibrated` | wakeup |
| 0x00000038 | lsm6dso Accelerometer Non-wakeup | STMicro | `android.sensor.accelerometer` | wakeup |
| 0x00000039 | Touch Sensor | xiaomi | `qti.sensor.touch` |  |
| 0x5f636779 | Corrected Gyroscope Sensor | AOSP | `android.sensor.gyroscope` |  |
| 0x5f676172 | Game Rotation Vector Sensor | AOSP | `android.sensor.game_rotation_vector` |  |
| 0x5f676273 | Gyroscope Bias (debug) | AOSP | `android.sensor.accelerometer` |  |
| 0x5f67656f | GeoMag Rotation Vector Sensor | AOSP | `android.sensor.geomagnetic_rotation_vector` |  |
| 0x5f677276 | Gravity Sensor | AOSP | `android.sensor.gravity` |  |
| 0x5f6c696e | Linear Acceleration Sensor | AOSP | `android.sensor.linear_acceleration` |  |
| 0x5f726f76 | Rotation Vector Sensor | AOSP | `android.sensor.rotation_vector` |  |
| 0x5f797072 | Orientation Sensor | AOSP | `android.sensor.orientation` |  |

SEE algorithm/registry configs present: sns_amd, sns_amd_sw_disabled, sns_amd_sw_enabled, sns_aod, sns_ccd, sns_ccd_v2_walk, sns_ccd_v3_walk, sns_cm, sns_dae, sns_dbtap, sns_device_orient, sns_diag_filter, sns_dpc, sns_fmv, sns_geomag_rv, sns_gyro_cal, sns_mag_cal, sns_nonui, sns_oem13, sns_rmd, sns_rotv, sns_sar_algo, sns_sar_algo_1, sns_screen_down, sns_smd, sns_tilt, sns_tilt_sw_disabled, sns_tilt_sw_enabled, sns_tilt_to_wake.

Firmware/driver files seen on the phone for the sensor subsystem:
```
-r--r----- 1 system system      756 2025-03-24 13:50 slpi.b00
-r--r----- 1 system system     7624 2025-03-24 13:50 slpi.b01
-r--r----- 1 system system    82680 2025-03-24 13:50 slpi.b02
-r--r----- 1 system system   247232 2025-03-24 13:50 slpi.b03
-r--r----- 1 system system  2071564 2025-03-24 13:50 slpi.b04
-r--r----- 1 system system  1732972 2025-03-24 13:50 slpi.b05
-r--r----- 1 system system    63642 2025-03-24 13:50 slpi.b06
-r--r----- 1 system system    28972 2025-03-24 13:50 slpi.b07
-r--r----- 1 system system   167668 2025-03-24 13:50 slpi.b08
-r--r----- 1 system system   111388 2025-03-24 13:50 slpi.b09
-r--r----- 1 system system    59320 2025-03-24 13:50 slpi.b10
-r--r----- 1 system system    27572 2025-03-24 13:50 slpi.b11
```

## 4. SEE configuration of each chip (verbatim, first 3000 characters)
### sm8250_ak991x_0.json
```json
{
  "config":
  {
    "hw_platform": ["MTP", "Surf", "MUNCH"],
    "soc_id": ["321", "339", "356"]
  },
  "ak0991x_0_platform":{
    "owner": "sns_ak0991x",
    ".config":{
      "owner": "sns_ak0991x",
      "bus_type":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "bus_instance":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "slave_config":{ "type": "int", "ver": "0",
        "data": "14"
      },
      "min_bus_speed_khz":{ "type": "int", "ver": "0",
        "data": "400"
      },
      "max_bus_speed_khz":{ "type": "int", "ver": "0",
        "data": "400"
      },
      "reg_addr_type":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "dri_irq_num":{ "type": "int", "ver": "0",
        "data": "119"
      },
      "irq_pull_type":{ "type": "int", "ver": "0",
        "data": "3"
      },
      "irq_is_chip_pin":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "irq_drive_strength":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "irq_trigger_type":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "num_rail":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "rail_on_state":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "vddio_rail":{ "type": "str", "ver": "0",
        "data": "/pmic/client/sensor_vddio"
      },
      "rigid_body_type":{ "type": "int", "ver": "0",
      "data": "0"
      }
    },
    ".orient":{
      "owner": "sns_ak0991x",
      "x":{ "type": "str", "ver": "1",
        "data": "-y"
      },
      "y":{ "type": "str", "ver": "1",
        "data": "-x"
      },
      "z":{ "type": "str", "ver": "1",
        "data": "-z"
      }
    },
    ".mag":{
      "owner": "sns_ak0991x",
      ".fac_cal":{
        "owner": "sns_ak0991x",
        ".corr_mat":{
          "owner": "sns_ak0991x",
          "0_0":{ "type": "flt", "ver": "0",
            "data": "1.0"
          },
          "0_1":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "0_2":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "1_0":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "1_1":{ "type": "flt", "ver": "0",
            "data": "1.0"
          },
          "1_2":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "2_0":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "2_1":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "2_2":{ "type": "flt", "ver": "0",
            "data": "1.0"
          }
        },
        ".bias":{
          "owner": "sns_ak0991x",
          "x":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "y":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "z":{ "type": "flt", "ver": "0",
            "data": "0.0"
          }
        }
      }
    },
    ".placement":{
      "owner": "sns_ak0991x",
      "0":{ "
```

### sm8250_bu27030_0_back.json
```json
{
  "config":{
    "hw_platform": ["MTP", "Dragon", "Surf","MUNCH"],
    "soc_id": ["291", "246", "305", "341", "356", "400"]
  },
  "bu27030_back_0_platform":{
    "owner": "sns_bu27030_back",
    ".config":{
      "owner": "sns_bu27030_back",
      "bus_type":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "bus_instance":{ "type": "int", "ver": "0",
        "data": "4"
      },
      "slave_config":{ "type": "int", "ver": "0",
        "data": "56"
      },
      "min_bus_speed_khz":{ "type": "int", "ver": "0",
        "data": "400"
      },
      "max_bus_speed_khz":{ "type": "int", "ver": "0",
        "data": "400"
      },
      "reg_addr_type":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "dri_irq_num":{ "type": "int", "ver": "0",
        "data": "162"
      },
      "irq_pull_type":{ "type": "int", "ver": "0",
        "data": "2"
      },
      "irq_is_chip_pin":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "irq_drive_strength":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "irq_trigger_type":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "num_rail":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "rail_on_state":{ "type": "int", "ver": "0",
        "data": "2"
      },
      "vddio_rail":{ "type": "str", "ver": "0",
        "data": "/pmic/client/sensor_vddio"
      },
      "rigid_body_type":{ "type": "int", "ver": "0",
      "data": "0"
      }
    },
    ".ambient_light":{
      "owner": "sns_bu27030_back",
      ".fac_cal":{
        "owner": "sns_bu27030_back",
        "scale":{ "type": "flt", "ver": "0",
          "data": "1.0"
        },
        "bias":{ "type": "flt", "ver": "0",
          "data": "0.0"
        }
      }
    },
    ".lcd_lux":{
      "owner": "sns_bu27030_back",
      ".diff_adc":{
        "owner": "sns_bu27030_back",
        "data0":{ "type": "flt", "ver": "0",
          "data": "0.0"
        },
        "data1":{ "type": "flt", "ver": "0",
          "data": "0.0"
        }
      }
    },
    ".highlcd":{
      "owner": "sns_tsl2560",
      ".fac_cal":{
        "owner": "sns_tsl2560",
      "dbv":{ "type": "flt", "ver": "0",
          "data": "4095.0"
        },
        "lux":{ "type": "flt", "ver": "0",
          "data": "0.0"
        }
      }
    },
    ".lowlcd":{
      "owner": "sns_tsl2560",
      ".fac_cal":{
        "owner": "sns_tsl2560",
      "dbv":{ "type": "flt", "ver": "0",
          "data": "200.0"
        },
        "lux":{ "type": "flt", "ver": "0",
          "data": "0.0"
        }
      }
    },
    ".prx2lux":{
      "owner": "sns_tsl2560",
      ".fac_cal":{
        "owner": "sns_tsl2560",
      "ch0_diff":{ "type": "flt", "ver": "0",
          "data": "0.0"
        },
        "ch1_diff":{ "type": "flt", "ver": "0",
          "data": "0.0"
        }
      }
    },
    ".coefficient":{
      "owner": "sns_bu27030_back",
      "0":{ "type": "flt", "ver": "0",
        "data": "200.0"
      },
      "
```

### sm8250_lsm6dso_0.json
```json
{
  "config":{
    "hw_platform": ["MTP", "Dragon", "Surf", "HDK", "MUNCH"],
    "soc_id": ["321", "339", "356"]
  },
  "lsm6dso_0_platform":{
    "owner": "lsm6dso",
    ".config":{
      "owner": "lsm6dso",
      "bus_type":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "bus_instance":{ "type": "int", "ver": "0",
        "data": "3"
      },
      "slave_config":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "i3c_address":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "min_bus_speed_khz":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "max_bus_speed_khz":{ "type": "int", "ver": "0",
        "data": "9600"
      },
      "reg_addr_type":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "dri_irq_num":{ "type": "int", "ver": "0",
        "data": "122"
      },
      "irq_pull_type":{ "type": "int", "ver": "0",
        "data": "2"
      },
      "irq_is_chip_pin":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "irq_drive_strength":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "irq_trigger_type":{ "type": "int", "ver": "0",
        "data": "3"
      },
      "num_rail":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "rail_on_state":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "vddio_rail":{ "type": "str", "ver": "0",
        "data": "/pmic/client/sensor_vddio"
      },
      "rigid_body_type":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "min_odr":{ "type": "int", "ver": "0",
        "data": "20"
      },
      "max_odr":{ "type": "int", "ver": "0",
        "data": "500"
      }
    },
    ".orient":{
      "owner": "lsm6dso",
      "x":{ "type": "str", "ver": "1",
        "data": "-x"
      },
      "y":{ "type": "str", "ver": "1",
        "data": "-y"
      },
      "z":{ "type": "str", "ver": "2",
        "data": "+z"
      }
    },
    ".gyro":{
      "owner": "lsm6dso",
      ".fac_cal":{
        "owner": "lsm6dso",
        ".corr_mat":{
          "owner": "lsm6dso",
          "0_0":{ "type": "flt", "ver": "1",
            "data": "1.017"
          },
          "0_1":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "0_2":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "1_0":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "1_1":{ "type": "flt", "ver": "0",
            "data": "1.0"
          },
          "1_2":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "2_0":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "2_1":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "2_2":{ "type": "flt", "ver": "0",
            "data": "1.0"
          }
        },
        ".bias":{
          "owner": "lsm6dso",
          "x":{ "type": "flt", "ver": "0",
            "data": "0.0"
          },
          "y":{ "type": "flt", "
```

### sm8250_sx932x_0.json
```json
{
  "config":{
    "hw_platform": ["MTP", "Surf", "HAYDN", "MUNCH"],
    "soc_id": ["321", "339", "356", "415", "356"]
  },
    "sx932x_0":{
    "owner": "sns_sx932x",
    ".sar":{
      "owner": "sns_sx932x",
      ".config":{
        "owner": "sns_sx932x",
        "is_dri":{ "type": "int", "ver": "0",
          "data": "0"
        },
        "hw_id":{ "type": "int", "ver": "0",
          "data": "0"
        },
        "res_idx":{ "type": "int", "ver": "0",
          "data": "2"
        },
        "sync_stream":{ "type": "int", "ver": "0",
          "data": "0"
        }
      }
    }
  },
  "sx932x_0_platform":{
    "owner": "sns_sx932x",
    ".config":{
      "owner": "sns_sx932x",
      "bus_type":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "bus_instance":{ "type": "int", "ver": "0",
        "data": "5"
      },
      "slave_config":{ "type": "int", "ver": "0",
        "data": "44"
      },
      "min_bus_speed_khz":{ "type": "int", "ver": "0",
        "data": "400"
      },
      "max_bus_speed_khz":{ "type": "int", "ver": "0",
        "data": "400"
      },
      "reg_addr_type":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "dri_irq_num":{ "type": "int", "ver": "0",
        "data": "91"
      },
      "irq_pull_type":{ "type": "int", "ver": "0",
        "data": "3"
      },
      "irq_is_chip_pin":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "irq_drive_strength":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "irq_trigger_type":{ "type": "int", "ver": "0",
        "data": "4"
      },
      "num_rail":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "rail_on_state":{ "type": "int", "ver": "0",
        "data": "2"
      },
      "vddio_rail":{ "type": "str", "ver": "1",
        "data": "/pmic/client/sensor_vddio"
      },
      "rigid_body_type":{ "type": "int", "ver": "0",
      "data": "0"
      }
    },
    ".temp":{
      "owner": "sns_sx932x",
      ".fac_cal":
      {
        "owner": "sns_sx932x",
        ".scale":{
          "owner": "sns_sx932x",
          "x":{ "type": "flt", "ver": "0",
            "data": "1.0"
          }
        },
        ".bias":{
          "owner": "sns_sx932x",
          "x":{ "type": "flt", "ver": "0",
            "data": "0.0"
          }
        }
      }
    },
    ".sar":{
      "owner": "sns_sx932x",
      ".fac_cal":
      {
        "owner": "sns_sx932x",
        ".scale":{
          "owner": "sns_sx932x",
          "x":{ "type": "flt", "ver": "0",
            "data": "1.0"
          }
        },
        ".bias":{
          "owner": "sns_sx932x",
          "x":{ "type": "flt", "ver": "0",
            "data": "0.0"
          }
        }
      }
    },
    ".placement":{
      "owner": "sns_sx932x",
      "0":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "1":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "2":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "3":
```

### sm8250_sx933x_0.json
```json
{
  "config":{
    "hw_platform": ["MTP", "Surf", "QRD", "HDK", "MUNCH"],
    "soc_id": ["321", "341", "356"]
  },
  "sx933x_0_platform":{
    "owner": "sns_sx933x",
    ".config":{
      "owner": "sns_sx933x",
      "bus_type":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "bus_instance":{ "type": "int", "ver": "0",
        "data": "5"
      },
      "slave_config":{ "type": "int", "ver": "0",
        "data": "40"
      },
      "min_bus_speed_khz":{ "type": "int", "ver": "0",
        "data": "400"
      },
      "max_bus_speed_khz":{ "type": "int", "ver": "0",
        "data": "400"
      },
      "reg_addr_type":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "dri_irq_num":{ "type": "int", "ver": "0",
        "data": "120"
      },
      "irq_pull_type":{ "type": "int", "ver": "0",
        "data": "3"
      },
      "irq_is_chip_pin":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "irq_drive_strength":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "irq_trigger_type":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "num_rail":{ "type": "int", "ver": "0",
        "data": "2"
      },
      "rail_on_state":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "vdd_rail":{ "type": "str", "ver": "0",
        "data": "/pmic/client/sensor_vdd_2"
      },
      "vddio_rail":{ "type": "str", "ver": "0",
        "data": "/pmic/client/sensor_vddio"
      },
      "rigid_body_type":{ "type": "int", "ver": "0",
      "data": "0"
      }
    },
    ".placement":{
      "owner": "sns_sx933x",
      "0":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "1":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "2":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "3":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "4":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "5":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "6":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "7":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "8":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "9":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "10":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "11":{ "type": "flt", "ver": "0",
        "data": "0.0"
      }
    },
    ".thresh":{
      "owner": "sns_sx933x",
      "threshold_0":{ "type": "flt", "ver": "0",
        "data": "25.0"
      },
      "threshold_1":{ "type": "flt", "ver": "0",
        "data": "25.0"
      },
      "threshold_2":{ "type": "flt", "ver": "0",
        "data": "25.0"
      },
      "threshold_3":{ "type": "flt", "ver": "0",
        "data": "25.0"
      }
    },
    ".offset":{
      "owner": "sns_sx933x",
      "0":{ "type": "flt", "ver": "0",
        "data": "0.0"
      },
      "1":{ "type": "flt", "ver": "0",
        "data": "0.0"
     
```

### sm8250_tcs3701.json
```json
{
  "config":{
    "hw_platform": ["QRD", "MTP", "Dragon", "Surf", "HDK", "MUNCH"],
    "soc_id": ["336", "339", "341", "321", "339", "356"]
  },
  "tcs3701_platform":{
    "owner": "sns_tcs3701",
    ".config":{
      "owner": "sns_tcs3701",
      "bus_type":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "bus_instance":{ "type": "int", "ver": "0",
        "data": "5"
      },
      "slave_config":{ "type": "int", "ver": "0",
        "data": "57"
      },
      "min_bus_speed_khz":{ "type": "int", "ver": "0",
        "data": "400"
      },
      "max_bus_speed_khz":{ "type": "int", "ver": "0",
        "data": "400"
      },
      "reg_addr_type":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "dri_irq_num":{ "type": "int", "ver": "0",
        "data": "126"
      },
      "irq_pull_type":{ "type": "int", "ver": "0",
        "data": "2"
      },
      "irq_is_chip_pin":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "irq_drive_strength":{ "type": "int", "ver": "0",
        "data": "0"
      },
      "irq_trigger_type":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "num_rail":{ "type": "int", "ver": "0",
        "data": "1"
      },
      "rail_on_state":{ "type": "int", "ver": "0",
        "data": "2"
      },
      "vddio_rail":{ "type": "str", "ver": "0",
        "data": "/pmic/client/sensor_vddio"
      },
      "rigid_body_type":{ "type": "int", "ver": "0",
      "data": "0"
      }
    },
    ".als":{
      "owner": "sns_tcs3701",
      ".fac_cal":{
        "owner": "sns_tcs3701",
        "scale":{ "type": "flt", "ver": "0",
          "data": "1.0"
        },
        "bias":{ "type": "flt", "ver": "0",
          "data": "0.0"
        }
      }
    },
    ".prox":{
      "owner": "sns_tcs3701",
      ".fac_cal":{
        "owner": "sns_tcs3701",
        "near_threshold":{ "type": "flt", "ver": "0",
          "data": "700.0"
        },
        "far_threshold":{ "type": "flt", "ver": "0",
          "data": "680.0"
        }
      }
    },
    ".channel":{
      "owner": "sns_tcs3701",
      ".fac_cal":{
        "owner": "sns_tcs3701",
        "data_cch":{ "type": "flt", "ver": "0",
          "data": "1.0"
        },
        "data_rch":{ "type": "flt", "ver": "0",
          "data": "1.0"
        },
        "data_gch":{ "type": "flt", "ver": "0",
          "data": "1.0"
        },
        "data_bch":{ "type": "flt", "ver": "0",
          "data": "1.0"
        },
        "data_wch":{ "type": "flt", "ver": "0",
          "data": "1.0"
        }
      }
    },
    ".coefficient":{
      "owner": "sns_tcs3701",
      "0":{ "type": "flt", "ver": "0",
        "data": "1.5698"
      },
      "1":{ "type": "flt", "ver": "0",
        "data": "3.8"
      },
      "2":{ "type": "flt", "ver": "0",
        "data": "-2.6"
      },
      "3":{ "type": "flt", "ver": "0",
        "data": "2.8"
      },
      "4":{ "type": "flt", "ver": "0",
        "data": "-5.2"
      },
      "5":{ "type": "flt", "v
```


## 5. Where the code is
* Kernel glue: `driver_sources/` archive -> `sensors_ssc.c` and the remoteproc/glink/PIL drivers (see `driver_sources/README.md`).
* Device-tree node: `hardware_nodes/*Sensors*` and `live_devicetree.dts` (`qcom,msm-ssc-sensors`, `slpi`, `qcom,glink-slpi`…).
* Chip datasheets (public, when available): `datasheets/` and `datasheets/SOURCES.md`.
* SEE chip drivers and the SLPI firmware: binary only — `firmware_and_kernels/<version>/dsp.img.zst` of each ROM contains the DSP images (aDSP/cDSP) and
  the SLPI blobs are in the vendor image `/vendor/firmware_mnt` / `/vendor/lib/rfsa`.
