import json,sys,math,numpy as np
sys.path.insert(0,'tools')
import kernel
mv=json.load(open('work/movement.json'))
def load(n):
    return kernel.load_step_part('work/parts/%s.step'%n,16777216,200000,0.001,0.1,500,120,4096,0.005)
cache={}
def mob(name):
    if name=='barrel': return kernel.tris_to_manifold(kernel.read_stl('meshes/barrel.stl',200000,33554432)),(0,0)
    d=mv['mobiles'][name]
    if name not in cache: cache[name]=(kernel.union([load(p) for p in d['parts']]),tuple(d['axis']))
    return cache[name]
def rot(man,ax,deg):
    a=math.radians(deg); c,s=math.cos(a),math.sin(a); x,y=ax
    T=np.array([[c,-s,0,x-c*x+s*y],[s,c,0,y-s*x-c*y],[0,0,1,0],[0,0,0,1]])
    return kernel.apply(man,T)
bad=0
for me in mv['meshes']:
    if len(sys.argv)>1 and me['driven'] not in sys.argv[1:]: continue
    A,ax=mob(me['driver']);B,bx=mob(me['driven'])
    nd,nn=me['driver_teeth'],me['driven_teeth']
    worst=0;dmax=0;drive=1e9
    for i in range(8*max(nd,nn)):
        ang=i*360/(8*nd)
        a=rot(A,ax,ang); b=rot(B,bx,-ang*nd/nn)
        worst=max(worst,kernel.ivol(a,b))
        if i%4==0: dmax=max(dmax,kernel.min_distance(a,b,1.0))
        if i%8==0: drive=min(drive,kernel.ivol(rot(A,ax,ang+90/nd),b))
    ok=worst<=0.01 and dmax<=0.1 and drive>0.01
    print(me['driver'],me['driven'],'jam',round(worst,4),'dist',round(dmax,3),'drive',round(drive,3),'OK' if ok else 'FAIL',flush=True)
