import json,numpy as np,trimesh,manifold3d as m3
def M(path):
    t=trimesh.load(path); return m3.Manifold(m3.Mesh(t.vertices.astype(np.float32),t.faces.astype(np.uint32)))
base=M('work/base.stl')
parts={n:M('meshes/%s.stl'%n) for n in ['pcb','J1','J2','C1','J4']}
A=json.load(open('work/assembly.json'))['board']
for i,p in enumerate(A):
    p=np.array(p)
    r=[]
    for n,m in parts.items():
        mm=m.transform(p[:3])
        v=(mm^base).volume()
        if v>0.2: r.append((n,round(v,1)))
    if r: print(i,r)
