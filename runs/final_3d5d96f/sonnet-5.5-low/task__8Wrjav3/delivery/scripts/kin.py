import sys,time,pickle,math,numpy as np,itertools,random
sys.path.insert(0,'/app/tools')
import kernel, manifold3d as m3
_argv=sys.argv; sys.argv=["x","1"]
import layout as LO; sys.argv=_argv
v,L,pil=pickle.load(open('/app/work/gen_meta.pkl','rb'))
P=LO.positions(v)
raw=pickle.load(open('/app/work/meshes.pkl','rb'))
def mk(name):
    vp,tv=raw[name]
    return m3.Manifold(m3.Mesh(vp.astype(np.float32),tv.astype(np.uint32)))
MESHES=None
def definition(variant):
    mob={'m1':(['m1_6h' if variant else 'm1'],'M1'),'x':(['x_6h' if variant else 'x'],'X'),'y':(['y'],'Y'),
         'minute':(['minute_tube','minute_hand'],'C'),'hour':(['hour_tube','hour_hand'],'H'),
         'a':(['a'],'A'),'b':(['b'],'B'),'j':(['j'],'J'),'i':(['i'],'I'),
         'd':(['d_wheel','d_hand'],'D'),'s1':(['s1'],'S1'),'s2':(['s2'],'S2'),'s3':(['s3'],'S3'),'sec':(['s_wheel','s_hand'],'S')}
    fixed=['plate_lower','plate_mid','plate_top']
    teeth={(m,g):z for m,gs in LO.G.items() for g,z in gs.items()}
    if variant: teeth[('M1','w')]=18; teeth[('X','a')]=24
    else: teeth[('M1','w')]=21; teeth[('X','a')]=21
    key2mob={'M1':'m1','X':'x','Y':'y','C':'minute','H':'hour','A':'a','B':'b','J':'j','I':'i','D':'d','S1':'s1','S2':'s2','S3':'s3','S':'sec'}
    meshes=[('barrel',96,'m1',12)]
    for a,b in LO.MESH:
        meshes.append((key2mob[a[0]],teeth[a],key2mob[b[0]],teeth[b]))
    return mob,fixed,meshes,key2mob
def speeds(meshes,barrel_rev_per_h):
    sp={'barrel':barrel_rev_per_h}
    for d,zd,n,zn in meshes:
        sp[n]=-sp[d]*zd/zn
    return sp
if __name__=='__main__':
    for variant,rate in ((False,1/8),(True,1/6)):
        mob,fixed,meshes,k2m=definition(variant)
        sp=speeds(meshes,rate)
        print('variant',variant,{k:round(x,4) for k,x in sp.items()})
