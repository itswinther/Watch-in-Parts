from common import *
import trimesh
tp=load('top_plate'); bp=load('bottom_plate')
def zcol(man,x,y):
    zs=np.arange(-2,12,0.05); 
    inside=[]
    for z in zs:
        p=kernel.box((x-0.01,y-0.01,z),(x+0.01,y+0.01,z+0.05))
        inside.append(kernel.ivol(man,p)>0)
    return [round(z,2) for z,i in zip(zs,inside) if i]
for (x,y) in [(10.5,12.6),(10.5,10),(10.5,15)]:
    r=zcol(tp,x,y); print('top',x,y,r[0] if r else None, r[-1] if r else None, len(r))
for (x,y) in [(10.5,12.6),(10.5,4.5),(10.5,18)]:
    r=zcol(bp,x,y); print('bot',x,y,r[0] if r else None, r[-1] if r else None, len(r))
