# Run on the phone as root. Lists /sys /proc /dev paths named by the HyperOS layer and whether they exist.
# Output: /data/local/tmp/hp2.txt, lines "E|N|T path file" (T = template with {} or %).
O=/data/local/tmp/hp.txt; : > $O
P='/(sys|proc|dev)/[A-Za-z0-9_.,:/{}%-]{3,}'
for f in /system/framework/*.jar /system_ext/framework/*.jar /product/framework/*.jar; do [ -f "$f" ] && { unzip -p "$f" 'classes*.dex' 2>/dev/null | grep -aoE "$P" | sed "s|\$| ${f##*/}|" >> $O; }; done
for f in /system/lib64/*.so /system_ext/lib64/*.so /product/lib64/*.so /system/bin/* /system_ext/bin/*; do [ -f "$f" ] && grep -aoE "$P" "$f" 2>/dev/null | sed "s|\$| ${f##*/}|" >> $O; done
for f in /product/app/*/*.apk /product/priv-app/*/*.apk /system_ext/priv-app/*/*.apk /system_ext/app/*/*.apk /system/priv-app/*/*.apk; do unzip -p "$f" 'classes*.dex' 2>/dev/null | grep -aoE "$P" | sed "s|\$| ${f##*/}|" >> $O; done
for f in /system/etc/init/*.rc /system_ext/etc/init/*.rc /product/etc/init/*.rc /system/etc/init/hw/*.rc; do [ -f "$f" ] && grep -oE "$P" "$f" | sed "s|\$| ${f##*/}|" >> $O; done
sort -u $O > $O.u
while read p f; do case "$p" in *{*|*%*) echo "T $p $f";; *) [ -e "$p" ] && echo "E $p $f" || echo "N $p $f";; esac; done < $O.u > /data/local/tmp/hp2.txt
rm -f $O $O.u
