import sys,json,pickle,numpy as np
sys.path.insert(0,'tools')
import kernel
mv=json.load(open('work/movement.json'))
names=[p for m in mv['mobiles'].values() for p in m['parts']]+mv['fixed']
S={}
for n in names:
    m=kernel.load_step_part(f'work/parts/{n}.step',16777216,200000,0.001,0.1,500,120,4096,0.005)
    S[n]=m
S['barrel']=kernel.tris_to_manifold(kernel.read_stl('meshes/barrel.stl',200000,33554432))
for n,m in S.items():
    b=m.bounding_box(); print(n,np.round(b,2).tolist(),round(m.volume(),2))
