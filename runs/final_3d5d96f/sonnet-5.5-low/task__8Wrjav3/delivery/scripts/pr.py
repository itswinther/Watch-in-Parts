import sys,time,pickle,math,numpy as np
sys.path.insert(0,'/app/tools')
import kernel, manifold3d as m3
raw=pickle.load(open('/app/work/meshes.pkl','rb'))
def mk(name):
    vp,tv=raw[name]
    return m3.Manifold(m3.Mesh(vp.astype(np.float32),tv.astype(np.uint32)))
h=0.05
def test(name):
    m=mk(name); bb=np.array(m.bounding_box())
    lo=bb[:3]-0.2; hi=bb[3:]+0.2
    org=np.floor((lo+0.0137)/h)*h-0.0137
    shape=tuple(int(x) for x in np.ceil((hi-org)/h)+1)
    n,dev=kernel.opening_test_slabs(m,org,shape,h,1.5,1.0,4.0)
    return n,dev
if __name__=='__main__':
    names=sys.argv[1:] or list(raw)
    for n in names:
        t=time.time(); r=test(n); print(n,r,round(time.time()-t,1),flush=True)
