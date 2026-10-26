#!/bin/bash
# Build the 64-bit audio and codec2 launchers with the Android NDK.
# Links against the phone's own 64-bit libraries (copied to $LIBS) so DT_NEEDED names and
# symbol versions match the device. Output: out/android.hardware.audio.service,
#                                           out/vendor.qti.media.c2@1.0-service
set -e
cd "$(dirname "$0")"
NDK=${NDK:-$HOME/Android/Sdk/ndk/28.2.13676358}
LIBS=${LIBS:-$HOME/kernel_build/hal64/libs}
CXX="$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin/clang++ --target=aarch64-linux-android30"
CFLAGS="-O2 -fPIE -pie -Wall -Werror -static-libstdc++ -Wl,--allow-shlib-undefined -Wl,-z,max-page-size=4096"
mkdir -p out

$CXX $CFLAGS audio_service.cpp -o out/android.hardware.audio.service \
    -llog "$LIBS/libhidlbase.so" "$LIBS/libbinder.so" "$LIBS/libutils.so" "$LIBS/libcutils.so" \
    "$LIBS/com.qualcomm.qti.bluetooth_audio@1.0.so"

$CXX $CFLAGS c2_service.cpp -o out/vendor.qti.media.c2@1.0-service \
    -llog "$LIBS/libhidlbase.so" "$LIBS/libbinder.so" "$LIBS/libutils.so" \
    "$LIBS/libavservices_minijail.so" "$LIBS/libqcodec2_core.so" "$LIBS/libcodec2_hidl@1.0.so" \
    "$LIBS/android.hardware.media.c2@1.0.so"

for f in out/*; do echo "$f: $(file -b "$f" | cut -d, -f1-2)"; done
