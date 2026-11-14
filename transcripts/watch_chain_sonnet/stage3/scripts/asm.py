import sys,json,numpy as np
sys.path.insert(0,'tools')
import kernel as K
mv=json.load(open('work/movement.json'))
P={}
mob={}
for n in mv['fixed']: P[n]=K.load_part('work/parts/%s.stl'%n,200000,2**25,1e-3); mob[n]=n
for m,d in mv['mobiles'].items():
    for n in d['parts']: P[n]=K.load_part('work/parts/%s.stl'%n,200000,2**25,1e-3); mob[n]=m
P['barrel']=K.load_part('meshes/barrel.stl',200000,2**25,1e-3); mob['barrel']='barrel'
allb=np.array([P[n].bounding_box() for n in P]); lo=allb[:,:3].min(0)-5; hi=allb[:,3:].max(0)+5
print(lo,hi)
order=sys.argv[1].split(',') if len(sys.argv)>1 else None
if not order:
    order=['main_plate','barrel','A_body','B_body','C_body','T_body','S_body','M_body','H_body','D_body','T_top','barrel_cock','hand_sec','hand_min','hand_hour','hand_day']
assert set(order)==set(P),set(P)^set(order)
dirs=[(0,0,1),(0,0,-1),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
def pose(d,s):
    T=np.eye(4);T[:3,3]=np.array(d)*s;return T
def tryd(n,placed,d):
    d=np.array(d,float);b=np.array(P[n].bounding_box())
    # distance s so bbox outside lo/hi
    ax=int(np.argmax(np.abs(d)))
    if d[ax]>0: s=hi[ax]-b[ax]+0.5
    else: s=b[3+ax]-lo[ax]+0.5
    s=abs(s)
    k=int(np.ceil(s/0.19))
    step=s/k
    others=[p for p in placed if mob[p]!=mob[n]]
    for i in range(k,-1,-1):
        T=pose(d,i*step)
        m=K.apply(P[n],T)
        for p in others:
            if K.ivol(m,P[p])>0.01: return None,(i,p)
    return [pose(d,i*step).tolist() for i in range(k,-1,-1)],None
placed=[];paths={};bad=[]
for n in order:
    ok=None
    for d in dirs:
        r,why=tryd(n,placed,d)
        if r: ok=r;break
        print(n,d,'blocked',why)
    if ok: paths[n]=ok;print(n,'OK',d,len(ok))
    else: bad.append(n);print(n,'FAIL')
    placed.append(n)
json.dump({'order':order,'paths':paths},open('work/assembly.json','w'))
print('bad',bad)
