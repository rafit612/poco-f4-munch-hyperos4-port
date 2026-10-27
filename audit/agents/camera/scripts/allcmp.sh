#!/bin/bash
SP=/tmp/claude-1000/-home-odoo-dbsl-poco-f4-5g-8gb-256gb-munch/155acf9c-1946-41a4-8e72-96ea9676041c/scratchpad
cd $SP/x
for s in munch_sunny_ov64b40_wide munch_aac_ov8856_ultra munch_sunny_ov8856_ultra munch_sunny_gc02m1_macro munch_ofilm_gc02m1_macro munch_sunny_imx596_front munch_ofilm_imx596_front munch_ofilm_imx582_wide default; do
  echo "######## $s"
  for i in m14 h1 pt; do python3 -I ../scripts/fsx.py cat $i /lib64/camera/com.qti.tuned.$s.bin > t_$i.bin; done
  ls -l t_*.bin | awk '{print $5, $9}'
  for i in m14 h1 pt; do echo "$i header: $(strings -n 6 t_$i.bin | head -2 | tr '\n' '|')  strings-sha1: $(strings -n 6 t_$i.bin | sort | sha1sum | cut -c1-12)"; done
  for p in m14:h1 h1:pt m14:pt; do a=${p%:*}; b=${p#*:}; n=$(cmp -l t_$a.bin t_$b.bin 2>/dev/null | wc -l); sz=$(stat -c%s t_$a.bin); echo "rawdiff $a-$b $n bytes = $(echo "scale=2;100*$n/$sz"|bc)%"; done
  python3 -I ../scripts/valdiff.py ../scripts t_m14.bin t_h1.bin t_pt.bin | cut -c1-600
  python3 -I ../scripts/smallint.py ../scripts t_m14.bin t_h1.bin t_pt.bin
  rm -f t_*.bin
done
