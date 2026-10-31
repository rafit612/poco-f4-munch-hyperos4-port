cd /
find /vendor/etc/init /vendor/bin /vendor/lib64/hw /vendor/lib/hw /odm/etc/init /system_ext/etc/init /vendor/etc/thermal* -maxdepth 2 -type f 2>/dev/null | while read f; do
 grep -aoE '/(sys|proc)/[A-Za-z0-9_.,:/-]{3,}' "$f" 2>/dev/null | sed "s|\$| ${f##*/}|"
done | sort -u > /data/local/tmp/paths.txt
while read p f; do [ -e "$p" ] && echo "E $p $f" || echo "N $p $f"; done < /data/local/tmp/paths.txt > /data/local/tmp/paths2.txt
wc -l /data/local/tmp/paths2.txt
