"""Local contact-driven kinematic checks; not a replacement for the acceptance rig.
Uses the specified overlap tolerance and minimal feasible follower displacement.
The one-way direction choices are justified separately by flank/friction angles.
"""
from check import *
TOL=.0002
res={}
def follow(driver, follower, state, point, axis, sign, maximum, step=.25):
 def at(q):return overlap(driver,rot(follower,q,point,axis))
 if at(state)<=TOL:return state
 last=0
 for delta in np.arange(step,maximum+step,step):
  if at(state+sign*delta)<=TOL:
   lo=last;hi=delta
   for _ in range(13):
    mid=(lo+hi)/2
    if at(state+sign*mid)>TOL:lo=mid
    else:hi=mid
   return state+sign*hi
  last=delta
 raise RuntimeError(('blocked follower',state,sign,maximum,at(state)))

def wind(start=(0,0,0,0),degrees=360):
 crown,pin,inter,bar=start
 rows=[]
 for i in range(int(degrees/3)):
  crown-=3
  sleeve=rot(shapes['sliding_clutch'],crown,axis='x')
  pin=follow(sleeve,shapes['winding_pinion'],pin,(0,0,0),'x',-1,5)
  driver=rot(shapes['winding_pinion'],pin,axis='x')
  inter=follow(driver,shapes['winding_transfer'],inter,(2.15,0,0),'z',-1,5)
  driver=rot(shapes['winding_transfer'],inter,(2.15,0,0))
  bar=follow(driver,shapes['barrel_ratchet'],bar,(2.15,4.157,0),'z',1,2,.1)
  rows.append([crown,pin,inter,bar])
 return rows

def click_rest(barangle):
 wheel=rot(shapes['barrel_ratchet'],barangle,(2.15,4.157,0))
 lo=-.32;hi=.02
 for _ in range(24):
  mid=(lo+hi)/2
  if overlap(wheel,shapes['click'].translate((mid,0,0)))>TOL:lo=mid
  else:hi=mid
 return hi

def gradient(barangle,shift):
 b=rot(shapes['barrel_ratchet'],barangle,(2.15,4.157,0));c=shapes['click'].translate((shift,0,0))
 dx=.0001;da=.003
 gx=(overlap(b,c.translate((dx,0,0)))-overlap(b,c.translate((-dx,0,0))))/(2*dx)
 gt=(overlap(rot(b,da,(2.15,4.157,0)),c)-overlap(rot(b,-da,(2.15,4.157,0)),c))/(2*da*pi/180*3.54)
 return gx,gt,abs(gx/gt) if gt else float('inf')

if __name__=='__main__':
 rows=wind();w=rows[-1];print('WIND crown,pinion,transfer,barrel',w,'ratio',360/w[3],flush=True)
 res['wind']={'final_angles':w,'ratio':360/w[3],'steps':len(rows)}
 # Hold starting from the prescribed externally wound 45 degrees.
 b=45;shift=click_rest(b);held=False
 for i in range(80):
  trial=b-.25
  v=overlap(rot(shapes['barrel_ratchet'],trial,(2.15,4.157,0)),shapes['click'].translate((shift,0,0)))
  if v>TOL:
   gx,gt,ratio=gradient(trial,shift)
   if ratio<.51:
    held=True;break
  b=trial;shift=click_rest(b)
 print('HOLD stopped',held,'arbor',b,'rollback',45-b,'gradient',gradient(trial,shift),flush=True)
 res['hold']={'held':held,'arbor_angle':b,'rollback':45-b,'click_shift':shift,'gradient_at_block':gradient(trial,shift),'reserve_hours':(6-(45-b)/360)*8}
 # Positive barrel rotation: click returns/slides without reaching a hard stop.
 shifts=[];ratios=[]
 for t in np.arange(b,b+20.001,.5):
  s=click_rest(t);shifts.append(s)
  ratios.append(gradient(t+.05,s)[2])
 print('RUN click travel',min(shifts),max(shifts),flush=True)
 res['run_click']={'shift_range':[min(shifts),max(shifts)],'steps':len(shifts),'friction_ratios':ratios}
 # Backward: least axial clutch displacement with winding pinion held fixed.
 backward=[]
 for a in np.arange(0,360.001,3):
  driver=rot(shapes['sliding_clutch'],a,axis='x');lo=0.;hi=.12
  for _ in range(20):
   mid=(lo+hi)/2
   if overlap(driver.translate((mid,0,0)),shapes['winding_pinion'])>TOL:lo=mid
   else:hi=mid
  backward.append(hi)
 print('BACKWARD clutch travel',min(backward),max(backward),flush=True)
 res['backward']={'steps':len(backward),'clutch_shift_range':[min(backward),max(backward)],'barrel_held_fixed':True}
 # Setting contact propagation in both directions, fresh from the same state.
 cx=k['mobiles']['setting_transfer']['point'][0]
 for sign in [-1,1]:
  sf=0;mn=0;data=[]
  for a in np.arange(3,90.001,3):
   driver=rot(shapes['stem'].translate((.9,0,0)),sign*a,axis='x')
   sf=follow(driver,shapes['setting_transfer'],sf,(cx,0,0),'z',-sign,5)
   mn=follow(rot(shapes['setting_transfer'],sf,(cx,0,0)),shapes['minute_wheel'],mn,(4.65,-4.157,0),'z',sign,2,.1)
   data.append([sign*a,sf,mn])
  print('SET',sign,'final',data[-1],flush=True)
  res['setting_'+str(sign)]={'steps':len(data),'final_angles':data[-1]}
 json.dump(res,open('/app/scripts/contact_checks.json','w'),indent=2)
