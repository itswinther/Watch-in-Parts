import sys
sys.path.insert(0,'tools')
import cadquery as cq, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
names=sys.argv[2:]
z=float(sys.argv[1])
fig,ax=plt.subplots(figsize=(9,9))
import random
for n in names:
    s=cq.importers.importStep(f'work/parts/{n}.step').val()
    sec=cq.Workplane('XY').add(s).section(z) if False else None
    sl=s.intersect(cq.Solid.makeBox(100,100,0.01,cq.Vector(-30,-30,z)))
    for f in sl.Faces():
        if abs(f.normalAt().z)>0.9 and f.Center().z<z+0.005 and f.Center().z>z-0.005 or True:
            pass
    # use tessellation of top faces
    if sl.Volume()<1e-6: continue
    v,t=sl.tessellate(0.02)
    pts=np.array([[p.x,p.y,p.z] for p in v]);tr=np.array(t)
    m=pts[:,2]>z+0.005
    keep=[tt for tt in tr if m[tt].all()]
    if keep: ax.triplot(pts[:,0],pts[:,1],keep,lw=0.2,label=n)
ax.set_aspect('equal');ax.grid(True);ax.legend()
plt.savefig('<host>/sec.png',dpi=70) if False else plt.savefig(sys.argv[0].replace('sec.py','sec.png'),dpi=70)
