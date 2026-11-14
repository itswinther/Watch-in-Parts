from check_movement import *
from fractions import Fraction
speeds={'barrel':Fraction(1,8)}
while True:
 changed=False
 for e in D['meshes']:
  a,b=e['driver'],e['driven'];r=Fraction(-e['driver_teeth'],e['driven_teeth'])
  if a in speeds:
   v=speeds[a]*r
   if b in speeds:assert speeds[b]==v
   else:speeds[b]=v;changed=True
  elif b in speeds:speeds[a]=speeds[b]/r;changed=True
 if not changed:break
print('SPEEDS clockwise revolutions/hour',speeds,flush=True)
assert speeds[D['hands']['day']['mobile']]==Fraction(1,24)
for name,period in [('hour',12),('minute',1),('seconds',Fraction(1,60))]:assert speeds[D['hands'][name]['mobile']]==Fraction(1)/period
print('DAY placement',np.linalg.norm(np.array(A['day'])-A[D['hands']['hour']['mobile']]),'reach',np.linalg.norm(k.verts(P['day_hand'])[:,:2]-A['day'],axis=1).max(),flush=True)
if sys.argv[1]=='pairs':
 edges={frozenset([e['driver'],e['driven']]) for e in D['meshes']}
 for a,b in itertools.combinations(M,2):
  if frozenset([a,b]) in edges:continue
  worst=(0,None)
  for phase,period in enumerate([1/max(abs(speeds[a]),abs(speeds[b])),1/abs(speeds[a]-speeds[b]) if speeds[a]!=speeds[b] else 0]):
   for i in range(144):
    time=period*Fraction(i,144)
    v=k.ivol(rotate(M[a],A[a],float(360*speeds[a]*time)),rotate(M[b],A[b],float(360*speeds[b]*time)))
    if v>worst[0]:worst=(v,(phase,i))
  print('PAIR',a,b,worst,flush=True)
 print('FIXED size',max(np.linalg.norm(k.verts(P[n])[:,:2]-D['case_centre'],axis=1).max() for n in D['fixed']),flush=True)
elif sys.argv[1]=='print':
 for name in ['day_pinion','day_wheel','day_hand','day_cock','upper_bridge']:
  m=P[name]; bb=np.array(m.bounding_box());
  for jit in [0,.023]:
   origin,shape=k.grid_for(bb[:3]-.1,bb[3:]+.1,.05,jit)
   vox=k.voxelize(m,origin,shape,.05)
   pieces,dev=k.opening_test(vox,1.5,1)
   print('PRINT',name,'jitter',jit,'core_components',pieces,'maximum defect mm',dev*.05,flush=True)
