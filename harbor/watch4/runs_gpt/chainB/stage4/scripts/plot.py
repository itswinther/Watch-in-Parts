exec(open('/app/scripts/assemble.py').read().split('for n,s in solids.items():')[0])
import matplotlib.pyplot as plt
fig,axs=plt.subplots(2,2,figsize=(12,10))
for ax,z in zip(axs.flat,[-.65,-.45,2.85,3.15]):
 for n in ['lower_bridge','reduction_input']:
  for p in solids[n].slice(z).to_polygons():
   p=np.array(p);ax.plot(*np.vstack([p,p[0]]).T,label=n)
 ax.set_xlim(8.5,14.7);ax.set_ylim(-10,-6);ax.set_aspect('equal');ax.set_title(str(z))
plt.savefig('/app/sections.png')
