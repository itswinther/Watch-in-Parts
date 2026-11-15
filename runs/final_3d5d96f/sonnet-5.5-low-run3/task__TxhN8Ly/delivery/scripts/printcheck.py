import sys, glob, os, math, numpy as np
sys.path.insert(0,'/app/tools'); sys.path.insert(0,'/app/work')
import kernel
from check import part
h=0.05
for f in sorted(glob.glob('/app/delivery/parts/*.step')):
    n=os.path.basename(f)[:-5]
    m=part(n); b=m.bounding_box()
    lo=np.array(b[:3]); hi=np.array(b[3:])
    k=np.floor((lo-0.0113)/h)-2
    origin=(k*h+0.0113-0.5*h)
    shape=tuple(int(math.ceil((hi[i]-origin[i])/h))+3 for i in range(3))
    pieces,dev=kernel.opening_test_slabs(m,origin,shape,h,1.5,1.0,6.0)
    print(n,shape,'pieces',pieces,'dev vox',round(dev,2),'->',round(dev*h,3),'mm', 'OK' if dev*h<=0.2 and pieces==1 else 'FAIL',flush=True)
