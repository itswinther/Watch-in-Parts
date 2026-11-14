from check import *
from phase import rot

def limit(a,b,da,db,pb,axisb,maxdist=5):
 # a and b already posed. angular movement b until interpenetration threshold
 out=[]
 for sign in [-1,1]:
  lo=0.;hi=maxdist
  if vol(a,rot(b,sign*hi,pb,axisb))<=.0002:out.append(sign*hi);continue
  for _ in range(12):
   mid=(lo+hi)/2
   if vol(a,rot(b,sign*mid,pb,axisb))>.0002:hi=mid
   else:lo=mid
  out.append(sign*lo)
 return out
print('Winding backlash envelope, degrees of arbor')
for stem in np.arange(0,46,3):
 a=rot(mans['winding_pinion'],stem,[0,0,0],[1,0,0]);b=rot(mans['barrel_gear'],-stem/5,[2.15,4.157,0],[0,0,1]);print(stem,limit(a,b,None,None,[2.15,4.157,0],[0,0,1]),flush=True)
ys=math.sqrt(5.7**2-2.35**2)-4.157
print('Setting backlash envelope, degrees of rotor')
for stem in np.arange(0,31,3):
 a=rot(mans['crown_stem'].translate([.9,0,0]),stem,[0,0,0],[1,0,0]);b=rot(mans['setting_intermediate'],-stem*2/3,[7,ys,0],[0,0,1]);print(stem,limit(a,b,None,None,[7,ys,0],[0,0,1]),flush=True)
