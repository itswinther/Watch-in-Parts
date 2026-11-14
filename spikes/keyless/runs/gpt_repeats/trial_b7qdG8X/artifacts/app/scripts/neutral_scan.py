from check import *
a=S['crown_stem'].translate([.675,0,0]);b=S['setting_transfer'];mx=(0,0,0)
for t in np.arange(0,18,.75):
 aa=rotate(a,0,t)
 for q in np.arange(0,18,.75):
  v=vol(aa,rotate(b,2,q,[5.25,0,0]))
  if v>mx[0]:mx=(v,float(t),float(q))
print(mx,flush=True)
