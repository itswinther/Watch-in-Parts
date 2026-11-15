import sys, json, itertools; sys.path.insert(0,'.'); sys.path.insert(0,'/app/tools')
from verify import *
mv=json.load(open(f'{D}/movement.json'))
owner={'barrel':('barrel',(0,0))}
for p in mv['fixed']: owner[p]=('fixed',None)
for mn,mo in mv['mobiles'].items():
    for p in mo['parts']: owner[p]=(mn,mo['axis'])
# 1 hands sweep
for hn,h in mv['hands'].items():
    ax=mv['mobiles'][h['mobile']]['axis']; mg=9
    for d in range(0,360,4):
        X=rot(get(h['part']),ax,d)
        for n in owner:
            if owner[n][0]==h['mobile']: continue
            Y=get(n)
            if not kernel.bbox_overlap(X,Y,0.05): continue
            iv=kernel.ivol(X,Y); g=0 if iv>1e-9 else X.min_gap(Y,0.1); 
            if g<mg: mg=g; who=n
    print('hand',hn,'min gap',round(mg,4),who if mg<9 else '')
# 2 joints: parts within a mobile touching; fixed parts touching
for mn,mo in mv['mobiles'].items():
    ps=mo['parts']
    for a,b in itertools.combinations(ps,2):
        iv=kernel.ivol(get(a),get(b)); g=get(a).min_gap(get(b),0.05) if iv<1e-9 else 0
        print('joint',mn,a,b,'ivol %.5f gap %.5f'%(iv,g))
fx=mv['fixed']
for a,b in itertools.combinations(fx,2):
    iv=kernel.ivol(get(a),get(b)); g=get(a).min_gap(get(b),0.05) if iv<1e-9 else 0
    if g<0.02: print('frame joint',a,b,'ivol %.5f gap %.5f'%(iv,g))
# 3 height & case
allb=[get(n).bounding_box() for n in owner]
zmin=min(b[2] for b in allb); zmax=max(b[5] for b in allb); print('height',zmax-zmin, zmin, zmax)
c=np.array(mv['case_centre'])
for n in owner:
    v=kernel.verts(get(n)); r=np.hypot(v[:,0]-c[0],v[:,1]-c[1]).max()
    if r>12.5: print('radius',n,round(r,4))
