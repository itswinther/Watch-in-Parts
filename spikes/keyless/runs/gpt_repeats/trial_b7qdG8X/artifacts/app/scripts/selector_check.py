from pair_check import *
for pull in [0,.225,.45,.675,.9]:
 for sign in [-1,1]:
  driver=S['crown_stem'].translate([pull,0,0]);out=S['setting_transfer']
  # Phase at the start may settle by up to one tooth interval.
  starts=[]
  for q in np.arange(-18,18.001,.5):
   v=vol(driver,rotate(out,2,q,[5.25,0,0]))
   if v<=.0002:starts.append(float(q))
  if not starts: print('PULL',pull,'SIGN',sign,'NO START PHASE',flush=True);continue
  # Choose phase closest to original.
  q0=min(starts,key=abs)
  out=rotate(out,2,q0,[5.25,0,0])
  r=follow(driver,out,0,2,[0,0,0],[5.25,0,0],np.arange(0,sign*24.01,sign*3),sign)
  print('PULL',pull,'SIGN',sign,'start',q0,'follow',r if isinstance(r,dict) else [r[-1][0],r[-1][1],max(x[2] for x in r)],flush=True)
