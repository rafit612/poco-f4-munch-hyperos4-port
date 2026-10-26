#!/system/bin/sh
# POCO F4: put the bundled LMC 8.4 configs where LMC reads them (/sdcard/LMC8.4, user 0).
# Runs once per boot after user 0 is unlocked; never overwrites a file the user already has.
SRC=/product/etc/gcam
DST=/data/media/0/LMC8.4
[ -d /data/media/0 ] || exit 0
OWNER=$(stat -c %u:%g /data/media/0)
[ -d "$DST" ] || { mkdir "$DST" && chown "$OWNER" "$DST" && chmod 0771 "$DST"; }
for f in "$SRC"/*.xml; do
    t="$DST/${f##*/}"
    [ -e "$t" ] && continue
    cp "$f" "$t" && chown "$OWNER" "$t" && chmod 0664 "$t"
done
exit 0
