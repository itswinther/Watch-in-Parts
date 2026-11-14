exec(open('/app/scripts/check.py').read().split("if '--mesh' not in sys.argv:")[0])
from fractions import Fraction
speeds={'barrel':Fraction(-1)}
while True:
 old=len(speeds)
 for e in D['meshes']:
  a,b=e['driver'],e['driven'];r=Fraction(-e['driver_teeth'],e['driven_teeth'])
  if a in speeds:
   s=speeds[a]*r
   if b in speeds:assert speeds[b]==s
   speeds[b]=s
  elif b in speeds:speeds[a]=speeds[b]/r
 if len(speeds)==old:break
print('SPEEDS',speeds,flush=True)
assert speeds['hour']==Fraction(-2,3) and speeds['minute']==-8 and speeds['seconds']==-480
hand_z=[]
for n,e in D['hands'].items():
 v=k.verts(P[e['part']]);ax=np.array(AX[e['mobile']]);reach=np.max(np.linalg.norm(v[:,:2]-ax,axis=1))
 assert reach>=5
 print('HAND',n,'reach',reach,'z',v[:,2].min(),v[:,2].max(),'period_hours',float(Fraction(8)/abs(speeds[e['mobile']])),flush=True)
 hand_z.append((v[:,2].min(),v[:,2].max()))
assert hand_z[0][1]<hand_z[1][0] and hand_z[1][1]<hand_z[2][0]
assert all(np.linalg.norm(np.array(AX[D['hands'][n]['mobile']])-AX['hour'])<.01 for n in D['hands'])
pairs={frozenset([e['driver'],e['driven']]) for e in D['meshes']}
names=list(M)
for i,a in enumerate(names):
 for b in names[i+1:]:
  if frozenset([a,b]) in pairs:continue
  sa,sb=float(speeds[a]),float(speeds[b]);worst=0
  for denominator in [max(abs(sa),abs(sb)),abs(sa-sb)]:
   if denominator==0:continue
   for j in range(144):
    t=j*360/144/denominator
    worst=max(worst,k.ivol(rot(a,t*sa),rot(b,t*sb)))
  print('NONMESH',a,b,worst,flush=True)
cc=np.array(D['case_centre']);rmax=0;zlo=100;zhi=-100
for n,man in M.items():
 v=k.verts(man);ax=np.array(AX[n]);r=np.max(np.linalg.norm(v[:,:2]-ax,axis=1))+np.linalg.norm(ax-cc)
 rmax=max(rmax,r);zlo=min(zlo,v[:,2].min());zhi=max(zhi,v[:,2].max())
 print('ROTATING_SIZE',n,r,flush=True)
v=k.verts(F);rmax=max(rmax,np.max(np.linalg.norm(v[:,:2]-cc,axis=1)));zlo=min(zlo,v[:,2].min());zhi=max(zhi,v[:,2].max());print('SIZE',rmax,zhi-zlo,zlo,zhi,flush=True)
# Printable voxels at three offsets; each part independently.
for n,man in P.items():
 if n=='barrel':continue
 bb=man.bounding_box();worst=0
 for jitter in [0,.017,.033]:
  origin,shape=k.grid_for(bb[:3],bb[3:],.05,jitter)
  for ix in range(0,shape[0],200):
   for iy in range(0,shape[1],200):
    x0=max(0,ix-7);x1=min(shape[0],ix+207);y0=max(0,iy-7);y1=min(shape[1],iy+207)
    tile_shape=(x1-x0,y1-y0,shape[2]);tile_origin=origin+np.array([x0,y0,0])*.05
    mask=k.voxelize(man,tile_origin,tile_shape,.05)
    pad=np.pad(mask,1);core=k.edt(pad)>=1.5
    if not core.any():
     if mask[ix-x0:min(ix+200,shape[0])-x0,iy-y0:min(iy+200,shape[1])-y0,:].any():worst=float('inf')
     continue
    opened=(k.edt(~core)<=1)&pad
    dist=k.edt(~opened)[1:-1,1:-1,1:-1]
    sub=mask[ix-x0:min(ix+200,shape[0])-x0,iy-y0:min(iy+200,shape[1])-y0,:]
    dd=dist[ix-x0:min(ix+200,shape[0])-x0,iy-y0:min(iy+200,shape[1])-y0,:]
    if sub.any():worst=max(worst,dd[sub].max()*.05)
 print('PRINTABLE',n,worst,'PASS' if worst<=.2 else 'FAIL',flush=True)
