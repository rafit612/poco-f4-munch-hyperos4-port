Sunday release candidate for POCO F4 5G (munch), HyperOS 4 / Android 17 Full Global. **Pre-release: the vendor image (schedtune boost) is not yet tested on the phone.**

Contents: vendor (official HyperOS 1 camera/audio/fingerprint stack, OV64B40 tuning, quick-shot mask, schedtune boost, thermal profiles), system, system_ext, product (HyperOS 4 camera 6.7, Global apps, tuning), mi_ext, odm.

`product.img` is split: `cat product.img.part-* > product.img`, then `sha256sum -c SHA256SUMS`. Flash in fastbootd — see INSTALL.md. Only for munch with this port's boot/vendor_boot/dtbo.
