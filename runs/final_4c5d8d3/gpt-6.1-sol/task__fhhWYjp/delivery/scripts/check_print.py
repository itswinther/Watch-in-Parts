import sys,os,math,json
import numpy as np
sys.path.insert(0,'/app/tools');import kernel as K
from pathlib import Path
results={}
for file in sorted(Path('/app/cache').glob('*.stl')):
 if file.stem=='barrel':continue
 m=K.load_part(str(file),200000,16777216,.005);bb=m.bounding_box();h=.05
 # voxel centres exactly 0.05*k + 0.0113
 first=np.floor((np.array(bb[:3])-.0113)/h).astype(int)-2
 origin=first*h+.0113-h/2
 shape=tuple((np.ceil((np.array(bb[3:])-(origin+h/2))/h).astype(int)+3).tolist())
 pieces,dev=K.opening_test_slabs(m,origin,shape,h,1.5,1.,5.,slab=32)
 results[file.stem]={'survives':pieces>0,'deviation_mm':dev*h,'pass':pieces>0 and dev*h<=.200001}
 print(file.stem,results[file.stem],flush=True)
Path('/app/print_check.json').write_text(json.dumps(results,indent=2))
