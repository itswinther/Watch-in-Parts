import numpy as np, json, trimesh, manifold3d as m3, sys
TH=np.radians(float(sys.argv[1]) if len(sys.argv)>1 else 22)
P=np.array([72,0,-2.5])
def mat(th,t):
    c,s=np.cos(th),np.sin(th)
    R=np.array([[c,0,s],[0,1,0],[-s,0,c]])
    M=np.eye(4); M[:3,:3]=R; M[:3,3]=P-R@P+np.array(t); return M
def interp(keys,maxstep,verts):
    # keys: list of (th,t). linear interp, subdivide to bound vertex motion
    poses=[mat(*keys[0])]
    for a,b in zip(keys[:-1],keys[1:]):
        ma,mb=mat(*a),mat(*b)
        d=np.abs((verts@ (mb[:3,:3]-ma[:3,:3]).T+(mb[:3,3]-ma[:3,3]))).max()
        d=max(d,1e-9)
        # rough upper bound; do adaptive check
        n=int(np.ceil(d/maxstep))
        while True:
            seq=[mat(a[0]+(b[0]-a[0])*i/n,np.array(a[1])+(np.array(b[1])-np.array(a[1]))*i/n) for i in range(n+1)]
            mx=max(np.linalg.norm(verts@(q[:3,:3]-p[:3,:3]).T+(q[:3,3]-p[:3,3]),axis=1).max() for p,q in zip(seq[:-1],seq[1:]))
            if mx<=maxstep: break
            n+=1
        poses+=seq[1:]
    return poses
board=trimesh.load('meshes/board.stl')
V=board.vertices
th=TH
H=40
t3=(0.8,0,1.2)
t4=(1.3,0,1.2)
s=2.0
t2=(t3[0]-s*np.cos(th),0,t3[2]+s*np.sin(th))
keys=[(th,(t2[0],0,t2[2]+H)),(th,t2),(th,t3),(0,t4),(0,(0,0,1.2)),(0,(0,0,0))]
bp=interp(keys,0.45,V)
def trans(dx,dy,dz,n_total,verts):
    return None
def lin(start,end,maxstep=0.45):
    start=np.array(start,float);end=np.array(end,float)
    n=int(np.ceil(np.linalg.norm(end-start)/maxstep))
    out=[]
    for i in range(n+1):
        M=np.eye(4);M[:3,3]=start+(end-start)*i/n;out.append(M)
    return out
lid=lin((0,0,40),(0,0,0))
bat=lin((9.1,-35,-8.5),(9.1,0.05,-8.5))
door=lin((0,-35,0),(0,0,0))
out={k:[p.tolist() for p in v] for k,v in dict(board=bp,lid=lid,battery=bat,door=door).items()}
json.dump(out,open('work/assembly.json','w'))
print({k:len(v) for k,v in out.items()})
