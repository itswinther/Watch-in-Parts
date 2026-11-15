import sys,math,numpy as np,glob,os
sys.path.insert(0,'/app/work')
from load import *
h=0.05
names=sys.argv[1:] or sorted(os.path.basename(p)[:-5] for p in glob.glob('/app/delivery/parts/*.step'))
for n in names:
    m=part(n); bb=m.bounding_box()
    lo=np.array(bb[:3]);hi=np.array(bb[3:])
    k0=np.floor((lo-0.0113)/h)-2
    origin=k0*h+0.0113-h/2
    shape=tuple(int(v) for v in np.ceil((hi-origin)/h)+3)
    pieces,dev=kernel.opening_test_slabs(m,origin,shape,h,1.5,1.0,6.0)
    print('%-16s pieces=%d dev=%.2f vox (%.3f mm) %s'%(n,pieces,dev,dev*h,'OK' if pieces>=1 and dev*h<=0.2+1e-9 else 'FAIL'),flush=True)
