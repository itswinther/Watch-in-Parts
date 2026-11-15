import sys, json, math; sys.path.insert(0,'.'); sys.path.insert(0,'/app/tools')
from verify import *
h=0.05; off=0.0113
names=sorted({p.replace('.step','') for p in os.listdir(D+'/parts')})
if len(sys.argv)>1: names=sys.argv[1:]
for n in names:
    man=get(n); bb=np.array(man.bounding_box())
    k0=np.floor((bb[:3]-off)/h)-2; origin=k0*h+off-h/2
    shape=tuple(int(x) for x in np.ceil((bb[3:]-origin)/h)+3)
    vox=kernel.voxelize(man,origin,shape,h)
    pcs,dev=kernel.opening_test(vox,1.5,1.0)
    print(n,shape,'pieces',pcs,'dev(vox)',round(dev,3),'OK' if pcs>=1 and dev*h<=0.2+1e-9 else 'FAIL',flush=True)
