import sys,json,time
from asm import *
D='/app/delivery'
def load_parts(folder,names):
    sys.path.insert(0,'/app/tools')
    out={}
    for n in names:
        out[n]=kernel.load_step_part(f'{folder}/parts/{n}.step',16777216,200000,0.001,0.1,500,120,4096,0.005)
    return out
def main():
    mv=json.load(open(D+'/movement.json'))
    names=list(mv['fixed'])
    for m in mv['mobiles'].values(): names+=m['parts']
    parts=load_parts(D,names)
    parts['barrel']=barrel()
    allb=[p.bounding_box() for p in parts.values()]
    lo=[min(b[i] for b in allb) for i in range(3)]; hi=[max(b[i+3] for b in allb) for i in range(3)]
    print('movement bbox',lo,hi)
    top=hi[2]
    first=['plate_lower','barrel','plate_mid']
    hands=['s_hand','minute_hand','hour_hand','d_hand']
    last=['plate_top']+hands
    mid=[n for n in names if n not in first+last]
    # exact sweeps among mid parts only vs each other
    edges={}
    for n in mid:
        others={k:parts[k] for k in mid if k!=n}
        h,T,k=sweep_hits(parts[n],others,top)
        edges[n]=h
    order_mid,rem=toposort(edges)
    print('mid order',order_mid,rem)
    if order_mid is None: sys.exit(1)
    order=first+order_mid+last
    # build paths & verify
    paths={}; placed={}
    ok=True
    for n in order:
        p=parts[n]; bb=p.bounding_box()
        # first pose: bbox must lie outside movement bbox grown by 5
        dz=(hi[2]+5.0+0.3)-bb[2]
        k=int(math.ceil(dz/0.15)); 
        poses=[]
        for i in range(k+1):
            t=dz*(1-i/k)
            M=[[1,0,0,0],[0,1,0,0],[0,0,1,round(t,9) if i<k else 0.0],[0,0,0,1]]
            poses.append(M)
        paths[n]=poses
        # collision check along the path vs placed
        bad=[]
        for i,M in enumerate(poses[:-1]):
            pm=p.translate([0,0,M[2][3]])
            for q,qm in placed.items():
                if kernel.ivol(pm,qm)>0.005: bad.append((i,q))
        # final pose
        for q,qm in placed.items():
            v=kernel.ivol(p,qm)
            if v>0.005: bad.append(('final',q,v))
        if bad:
            ok=False; print('COLLISION',n,bad[:5])
        placed[n]=p
    print('ok' if ok else 'FAIL', len(order))
    if ok:
        json.dump({'order':order,'paths':paths},open(D+'/assembly.json','w'))
main()
