# usage: symbol_coverage.py <lineage> <liyafe> <rohman>; reads ~/kernel_build/phone_snapshot/kallsyms.txt
import os,re,sys
L,M,R=sys.argv[1:4]
idp=re.compile(rb'[A-Za-z_][A-Za-z0-9_]{3,}')
def ids(paths):
    s=set()
    for r in paths:
        for d,ds,fs in os.walk(r):
            ds[:]=[x for x in ds if x not in('.git','Documentation','tools','samples','out')]
            for f in fs:
                if f.endswith(('.c','.h','.S')):
                    try:s|={m.decode() for m in idp.findall(open(os.path.join(d,f),'rb').read())}
                    except:pass
    return s
syms=set()
for l in open(os.path.expanduser('~/kernel_build/phone_snapshot/kallsyms.txt')):
    p=l.split()
    if len(p)>=3 and p[1] in'tT':
        syms.add(re.sub(r'(\.cfi(_jt)?|\.llvm\.\d+|\.\d+)$','',p[2]))
groups={
'camera(cam_)':(r'^cam_',('techpack/camera-xiaomi','techpack/camera-xiaomi','techpack/camera')),
'display(dsi_,sde_,mi_dsi)':(r'^(dsi_|sde_|mi_dsi|mi_disp|dp_)',None),
'audio(afe,adm,asm,wcd,wsa,msm_pcm,q6)':(r'^(afe_|adm_|asm_|wcd|wsa|msm_pcm|msm_dai|q6|audio_|apr_)',('techpack/audio','techpack/audio','techpack/audio')),
'bpf':(r'^(bpf_|btf_|sock_map|tcp_bpf|ringbuf|sk_msg)',None),
'gpu(kgsl,adreno)':(r'^(kgsl_|adreno_|a6xx_|gen7_)',None),
'scheduler(walt,sched_,cpufreq_gov)':(r'^(walt_|sched_|sugov_|cpufreq_gov|core_ctl)',None),
'memory(mi_reclaim,rtmm,zram,zsmalloc)':(r'^(mi_reclaim|rtmm|zram|zs_|process_reclaim|memcg_)',None),
'binder':(r'^(binder_|mi_binder)',None),
'wifi(hdd,wlan,sme,csr,wma)':(r'^(hdd_|wlan_|sme_|csr_|wma_|cds_)',None),
'charging(smblib,bq,ln8000,pd_)':(r'^(smblib_|smb5_|bq2|ln8000|pd_|usbpd_|qg_)',None),
'touch/haptic(fts,xiaomi_touch,aw8)':(r'^(fts_|xiaomi_touch|aw86|haptic)',None),
'thermal(thermal_,board_sensor)':(r'^(thermal_|board_sensor|cooling_)',None),
}
full={n:ids([p]) for n,p in (('L',L),('M',M),('R',R))}
print(f'{"group":44}{"porter":>7}{"Lin":>7}{"liyafe":>7}{"rohman":>7}  (porter functions MISSING in each tree)')
ex={}
for g,(rx,dirs) in groups.items():
    ss={s for s in syms if re.search(rx,s)}
    if dirs:
        tset=[ids([os.path.join(t,d)]) for t,d in zip((L,M,R),dirs)]
    else: tset=[full['L'],full['M'],full['R']]
    miss=[ss-t for t in tset]
    ex[g]=miss
    print(f'{g:44}{len(ss):7}{len(miss[0]):7}{len(miss[1]):7}{len(miss[2]):7}')
for g in ('camera(cam_)','scheduler(walt,sched_,cpufreq_gov)','audio(afe,adm,asm,wcd,wsa,msm_pcm,q6)','display(dsi_,sde_,mi_dsi)'):
    for n,m in zip('LMR',ex[g]):
        print(g[:8],n,' '.join(sorted(m)[:28]))
