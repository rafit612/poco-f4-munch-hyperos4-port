import sys,json
sys.path.insert(0,sys.argv[1])
import fsx
from concurrent.futures import ThreadPoolExecutor
CAMRE=r'(?i)(cam|chi|mialgo|anc_|libwa_|arcsoft|mibokeh|mpbase|qti\.stats|qtistatic|stats|eis|sns|mivi|hdr|dualcam|depth|bokeh|portrait|aiscene|morpho|clearsight|ipebps|chromatix|tuned|sensor|qcom\.so$|vidhance|xmi|ofilm|sunny|beauty|facedetect|fd|snpe|hta|vndk_cam|aide|night|super|mfnr|swmf|lsc|pdaf|ae|af|awb|isp)'
out={}
for img in ["m14","h1","pt"]:
    files=fsx.walk(img,"/lib64/camera")+fsx.walk(img,"/etc/camera")+fsx.walk(img,"/lib64/hw",False,r'(?i)cam')+fsx.walk(img,"/lib64",False,CAMRE)+fsx.walk(img,"/lib/camera")+fsx.walk(img,"/lib/hw",False,r'(?i)cam')+fsx.walk(img,"/etc",False,r'(?i)cam')
    files=[f for f in files if not f.endswith("->link")]
    def h(f): return f,fsx.hashf(img,f)
    with ThreadPoolExecutor(8) as ex:
        out[img]={f:v for f,v in ex.map(h,files)}
    print(img,len(out[img]),file=sys.stderr)
json.dump(out,open(sys.argv[2],"w"),indent=0)
