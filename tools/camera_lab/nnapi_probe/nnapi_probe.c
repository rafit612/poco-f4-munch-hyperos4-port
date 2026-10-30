// List the NNAPI devices an ordinary app sees (U7 in 06b_UNUSED_CAPABILITY.md). Run as adb shell, no root.
// build: aarch64-linux-android34-clang nnapi_probe.c -lneuralnetworks -o nnapi_probe
#include <android/NeuralNetworks.h>
#include <stdio.h>

static const char *type_name(int32_t t) {
    switch (t) {
        case ANEURALNETWORKS_DEVICE_CPU: return "CPU";
        case ANEURALNETWORKS_DEVICE_GPU: return "GPU";
        case ANEURALNETWORKS_DEVICE_ACCELERATOR: return "ACCELERATOR";
        case ANEURALNETWORKS_DEVICE_OTHER: return "OTHER";
        default: return "UNKNOWN";
    }
}

int main(void) {
    uint32_t n = 0;
    if (ANeuralNetworks_getDeviceCount(&n) != ANEURALNETWORKS_NO_ERROR) { puts("getDeviceCount failed"); return 1; }
    printf("runtime feature level %lld, %u devices\n", (long long)ANeuralNetworks_getRuntimeFeatureLevel(), n);
    for (uint32_t i = 0; i < n; i++) {
        ANeuralNetworksDevice *d; const char *name = "?", *ver = "?"; int32_t type = 0; int64_t level = 0;
        ANeuralNetworks_getDevice(i, &d);
        ANeuralNetworksDevice_getName(d, &name);
        ANeuralNetworksDevice_getVersion(d, &ver);
        ANeuralNetworksDevice_getType(d, &type);
        ANeuralNetworksDevice_getFeatureLevel(d, &level);
        printf("%u  %-24s %-12s feature level %lld  version %s\n", i, name, type_name(type), (long long)level, ver);
    }
    return 0;
}
