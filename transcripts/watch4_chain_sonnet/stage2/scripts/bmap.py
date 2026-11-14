import sys
sys.path.insert(0,'tools')
import cadquery as cq, numpy as np
s=cq.importers.importStep('work/parts/bridge.step').val()
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
xs=np.arange(-3,20.5,0.5); ys=np.arange(-3,20,0.5)
H=np.full((len(ys),len(xs)),np.nan)
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN
for i,y in enumerate(ys):
  for j,x in enumerate(xs):
    for z in (7.25,7.05):
        c=BRepClass3d_SolidClassifier(s.wrapped,gp_Pnt(x,y,z),1e-6)
        if c.State()==TopAbs_IN: H[i,j]=z;break
np.save('scripts/bmap.npy',H)
fig,ax=plt.subplots(figsize=(9,9)); ax.imshow(~np.isnan(H),origin='lower',extent=(-3.25,20.25,-3.25,19.75)); ax.grid(True)
plt.savefig('scripts/bmap.png',dpi=60)
print(np.nanmax(H),np.nanmin(H))
