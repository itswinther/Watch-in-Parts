from check import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,axs=plt.subplots(1,2,figsize=(12,5))
for ax,z in zip(axs,[-.7,1.3]):
 for name,m in S.items():
  if name in ['main_plate','dial_plate']:continue
  c=m.slice(z)
  for poly in c.to_polygons():
   p=np.vstack([poly,poly[0]])
   ax.plot(p[:,0],p[:,1],label=name)
 ax.set_aspect('equal');ax.set_title(f'z={z} mm');ax.set_xlim(1,7);ax.set_ylim(-1.5,5.5);ax.grid()
fig.savefig('/app/scripts/sections.png',dpi=180)
# bevel section near one tooth for examination
m=S['setting_transfer'].translate([-5.25,0,0]);cs=m.slice(-.7)
fig,ax=plt.subplots(figsize=(6,6))
for p in cs.to_polygons():
 p=np.vstack([p,p[0]]);ax.plot(p[:,0],p[:,1])
ax.set_aspect('equal');ax.grid();fig.savefig('/app/scripts/bevel_section.png',dpi=160)
