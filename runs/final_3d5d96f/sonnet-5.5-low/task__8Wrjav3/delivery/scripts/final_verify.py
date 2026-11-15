import sys,json,math,random,itertools,numpy as np
sys.path.insert(0,'/app/tools')
import kernel, manifold3d as m3
D='/app/delivery'
def load(n): return kernel.load_step_part(f'{D}/parts/{n}.step',16777216,200000,0.001,0.1,500,120,4096,0.005)
barrel=kernel.tris_to_manifold(kernel.read_stl('/app/supplied/BR-096-30.stl',10**7,10**9))
def rot(m,ax,ay,th):
    c,s=math.cos(th),math.sin(th)
    return m.transform([[c,-s,0,ax-c*ax+s*ay],[s,c,0,ay-s*ax-c*ay],[0,0,1,0]])
def speeds(doc,rate):
    sp={'barrel':rate}
    ms=list(doc['meshes'])
    changed=True
    while changed:
        changed=False
        for e in ms:
            if e['driver'] in sp and e['driven'] not in sp:
                sp[e['driven']]=-sp[e['driver']]*e['driver_teeth']/e['driven_teeth']; changed=True
    return sp
cache={}
def part(n):
    if n not in cache: cache[n]=load(n)
    return cache[n]
for fn,rate in (('movement.json',1/8),('variant_6h.json',1/6)):
    doc=json.load(open(f'{D}/{fn}'))
    sp=speeds(doc,rate)
    print(fn,'hands (rev/h, +cw):',{h:round(sp[v['mobile']],5) for h,v in doc['hands'].items()})
    C=doc['case_centre']
    for h,v in doc['hands'].items():
        ax=doc['mobiles'][v['mobile']]['axis']
        d=math.hypot(ax[0]-C[0],ax[1]-C[1])
        vp=part(v['part']).to_mesh().vert_properties[:,:3]
        L=np.hypot(vp[:,0]-ax[0],vp[:,1]-ax[1]).max()
        print('  ',h,'axis dist from centre',round(d,3),'length',round(L,3))
    items=[('barrel','barrel',barrel)]
    for n in doc['fixed']: items.append(('fixed',n,part(n)))
    for mn,m in doc['mobiles'].items():
        for pn in m['parts']: items.append((mn,pn,part(pn)))
    rng=random.Random(5); worst={}
    for it in range(120):
        t=rng.uniform(0,48) if it else 0
        cur=[]
        for mn,pn,p in items:
            if mn=='fixed': cur.append((mn,pn,p))
            elif mn=='barrel': cur.append((mn,pn,rot(p,0,0,-2*math.pi*sp['barrel']*t)))
            else:
                ax=doc['mobiles'][mn]['axis']; cur.append((mn,pn,rot(p,ax[0],ax[1],-2*math.pi*sp[mn]*t)))
        for (m1,n1,a),(m2,n2,b) in itertools.combinations(cur,2):
            if m1==m2: continue
            v=kernel.ivol(a,b)
            if v>0: worst[(n1,n2)]=max(worst.get((n1,n2),0),v)
    print('  max overlaps (mm3):',{k:round(x,5) for k,x in worst.items()} or 'none')
# assembly
asm=json.load(open(f'{D}/assembly.json'))
mv=json.load(open(f'{D}/movement.json'))
names=list(mv['fixed'])+[p for m in mv['mobiles'].values() for p in m['parts']]
allp={n:part(n) for n in names}; allp['barrel']=barrel
bbs=[p.bounding_box() for p in allp.values()]
lo=[min(b[i] for b in bbs)-5 for i in range(3)]; hi=[max(b[i+3] for b in bbs)+5 for i in range(3)]
print('order',asm['order'],len(asm['order']),'parts',len(allp))
assert set(asm['order'])==set(allp)
placed={}
ok=True
for n in asm['order']:
    poses=np.array(asm['paths'][n]); assert 2<=len(poses)<=1500
    for T in poses:
        R=T[:3,:3]
        assert np.allclose(R.T@R,np.eye(3),atol=1e-6) and abs(np.linalg.det(R)-1)<1e-6 and np.allclose(T[3],[0,0,0,1],atol=1e-6)
    assert np.allclose(poses[-1],np.eye(4),atol=1e-6)
    p=allp[n]; bb=p.bounding_box()
    T=poses[0]; b0=[bb[0]+T[0,3],bb[1]+T[1,3],bb[2]+T[2,3],bb[3]+T[0,3],bb[4]+T[1,3],bb[5]+T[2,3]]
    outside=any(b0[i+3]<lo[i] or b0[i]>hi[i] for i in range(3))
    v=kernel.verts(p)
    for a,b in zip(poses[:-1],poses[1:]):
        d=np.abs((v@(b[:3,:3]-a[:3,:3]).T)+(b[:3,3]-a[:3,3])).max()
        pass
    mv_=max(np.linalg.norm(((v@b[:3,:3].T)+b[:3,3])-((v@a[:3,:3].T)+a[:3,3]),axis=1).max() for a,b in zip(poses[:-1],poses[1:]))
    bad=0
    for T in poses:
        pm=kernel.apply(p,T)
        for q,qm in placed.items():
            if kernel.ivol(pm,qm)>0.01: bad+=1
    print(f'{n:14s} poses {len(poses):3d} first-outside {outside} maxstep {mv_:.3f} collisions {bad}')
    ok&=outside and mv_<=0.2 and bad==0
    placed[n]=p
print('ASSEMBLY OK' if ok else 'ASSEMBLY FAIL')
zs=[b[2] for b in bbs]+[b[5] for b in bbs]
print('height',max(b[5] for b in bbs)-min(b[2] for b in bbs))
