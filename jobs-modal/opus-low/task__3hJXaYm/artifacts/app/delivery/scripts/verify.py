import sys, json, math, itertools, pickle, os
sys.path.insert(0,'/app/tools'); import kernel, numpy as np, manifold3d as m3, trimesh
from fractions import Fraction as F
D='/app/delivery'
def load(n):
    return kernel.load_step_part(f'{D}/parts/{n}.step',16777216,200000,0.001,0.1,500,120,4096,0.005)
bm=trimesh.load('/app/supplied/BR-096-30.stl')
BAR=m3.Manifold(m3.Mesh(vert_properties=np.asarray(bm.vertices,np.float32),tri_verts=np.asarray(bm.faces,np.uint32)))
cache={}
def get(n):
    if n=='barrel': return BAR
    if n not in cache: cache[n]=load(n)
    return cache[n]
def rot(man,axis,deg):
    return man.translate([-axis[0],-axis[1],0]).rotate([0,0,deg]).translate([axis[0],axis[1],0])
def speeds(mv,barrel_h):
    w={'barrel':F(-1,barrel_h)}  # rev/h, + = CCW
    todo=list(mv['meshes'])
    while todo:
        for e in list(todo):
            if e['driver'] in w:
                w[e['driven']]=-w[e['driver']]*F(e['driver_teeth'],e['driven_teeth']); todo.remove(e)
    return w
def check(fn,barrel_h,tsamples=12):
    mv=json.load(open(f'{D}/{fn}'))
    w=speeds(mv,barrel_h); print(fn,{k:str(v) for k,v in w.items()})
    owner={'barrel':('barrel',(0,0))}
    for p in mv['fixed']: owner[p]=('fixed',None)
    for mn,mo in mv['mobiles'].items():
        for p in mo['parts']: owner[p]=(mn,mo['axis'])
    names=list(owner)
    meshpairs={frozenset((e['driver'],e['driven'])) for e in mv['meshes']}
    # static + moving: at random times
    rng=np.random.default_rng(0)
    worst={}
    ts=[0.0]+list(rng.uniform(0,24,tsamples))
    for t in ts:
        pose={}
        for n in names:
            mob,ax=owner[n]
            if mob=='fixed': pose[n]=get(n)
            else: pose[n]=rot(get(n),ax,float(w[mob])*360*t)
        for a,b in itertools.combinations(names,2):
            ma,mb=owner[a][0],owner[b][0]
            if ma==mb and ma!='fixed': continue
            if ma=='fixed' and mb=='fixed': continue
            if not kernel.bbox_overlap(pose[a],pose[b],0.05): continue
            iv=kernel.ivol(pose[a],pose[b])
            g=0 if iv>1e-9 else pose[a].min_gap(pose[b],0.1)
            k=(a,b); worst[k]=min(worst.get(k,9),g)
            if iv>1e-6: print('  OVERLAP t=%.3f'%t,a,b,iv)
    for k,v in sorted(worst.items(),key=lambda x:x[1])[:15]: print('  gap',k,round(v,4))
    return mv,w,owner
def mesh_sweep(mv,w,owner,steps=30):
    # for each mesh, rotate over 1.2 tooth pitch of driver
    byname={}
    for n,(mob,ax) in owner.items(): byname.setdefault(mob,[]).append(n)
    for e in mv['meshes']:
        A,B=e['driver'],e['driven']
        axA=(0,0) if A=='barrel' else mv['mobiles'][A]['axis']; axB=mv['mobiles'][B]['axis']
        pa=byname[A]; pb=byname[B]
        tmax=1.2/e['driver_teeth']/abs(float(w[A]))
        mg=9
        for t in np.linspace(0,tmax,steps):
            for x in pa:
                X=rot(get(x),axA,float(w[A])*360*t)
                for y in pb:
                    Y=rot(get(y),axB,float(w[B])*360*t)
                    if not kernel.bbox_overlap(X,Y,0.05): continue
                    iv=kernel.ivol(X,Y)
                    g=0 if iv>1e-9 else X.min_gap(Y,0.1)
                    mg=min(mg,g)
                    if iv>1e-7: print('  MESH OVERLAP',A,B,x,y,t,iv)
        print('  mesh',A,B,'min gap',round(mg,4))
if __name__=='__main__':
    for fn,bh in (('movement.json',8),('variant_6h.json',6)):
        mv,w,owner=check(fn,bh)
        mesh_sweep(mv,w,owner)
