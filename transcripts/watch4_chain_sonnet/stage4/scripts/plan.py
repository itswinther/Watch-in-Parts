import sys,json,numpy as np
sys.path.insert(0,'tools')
import kernel, manifold3d as m3
mv=json.load(open('work/movement.json'))
mob={}
for k,m in mv['mobiles'].items():
    for p in m['parts']: mob[p]=k
for p in mv['fixed']: mob[p]='F_'+p
mob['barrel']='barrel'
S={}
for n in mob:
    if n=='barrel': S[n]=kernel.tris_to_manifold(kernel.read_stl('meshes/barrel.stl',200000,33554432))
    else: S[n]=kernel.load_step_part(f'work/parts/{n}.step',16777216,200000,0.001,0.1,500,120,4096,0.005)
BB={n:np.array(m.bounding_box()).reshape(2,3) for n,m in S.items()}
allmin=np.min([b[0] for b in BB.values()],0); allmax=np.max([b[1] for b in BB.values()],0)
ZTOP=allmax[2]+5.0+1.0
def tz(dz): return S_cache(dz)
def moved(n,dz):
    return S[n].translate([0,0,dz])
def inter(a,b):
    return (a^b).volume()
def collides(n,dz,placed):
    bb=BB[n].copy(); bb[:,2]+=dz
    m=None
    for q in placed:
        if mob[q]==mob[n]: continue
        qb=BB[q]
        if (bb[1]<qb[0]-1e-9).any() or (bb[0]>qb[1]+1e-9).any(): continue
        if m is None: m=moved(n,dz)
        if inter(m,S[q])>0.005: return True
    return False
def zpath(n,direction,placed):
    # start offset so bbox outside
    if direction>0: start=allmax[2]+5.01-BB[n][0][2]
    else: start=allmin[2]-5.01-BB[n][1][2]
    nst=int(np.ceil(abs(start)/0.19))
    dzs=[start*(1-i/nst) for i in range(nst+1)]
    for dz in dzs[1:]:   # first pose is outside by construction
        if collides(n,dz,placed): return None
    return dzs
ORDER="main_plate barrel p1 w1 g_in s0 s1p s1w s2p mw cw cp hw arb_train1 arb_minute arb_idler arb_seconds arb_motion hour_tube bridge hand_hour hand_minute gh wa pa wd arb_a arb_day hand_seconds hand_day day_cock".split()
placed=[];paths={}
for n in ORDER:
    for d in (1,-1):
        p=zpath(n,d,placed)
        if p: break
    print(n,'OK' if p else 'FAIL',flush=True)
    if not p:
        for d in (1,-1):
            bad=set()
            for dz in np.arange(-15,15,0.5):
                for q in placed:
                    if mob[q]!=mob[n] and inter(moved(n,dz),S[q])>0.005: bad.add((q,round(dz,1)))
            print(' ',d,sorted(bad)[:8]);break
    placed.append(n)
    if p: paths[n]=p
print([n for n in S if n not in ORDER])
out={'order':placed,'paths':{n:[[[1,0,0,0],[0,1,0,0],[0,0,1,dz],[0,0,0,1]] for dz in p[:-1]]+[np.eye(4).tolist()] for n,p in paths.items()}}
json.dump(out,open('work/assembly.json','w'))
print(len(placed),len(S))
