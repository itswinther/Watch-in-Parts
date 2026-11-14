"""Independent quasistatic mesh check.
Gear movement is found by first-clear intersection searches along each DOF.
Ratchet direction is selected using its manufactured ramps and Coulomb locking
criterion. This is a specialized model, not the undisclosed official verifier.
"""
from check import *
from phase import rot
import copy,time
TH=.00019
YS=math.sqrt(5.7**2-2.35**2)-4.157
BP=[2.15,4.157,0];SP=[7,YS,0];MP=[4.65,-4.157,0]
X=[1,0,0];Z=[0,0,1]

def first_clear(fn,start,direction,hi):
 if fn(start)<=TH:return start
 lo=0.
 found=False
 for trial in np.linspace(0,hi,25)[1:]:
  if fn(start+direction*trial)<=TH:
   hi=trial;found=True;break
  lo=trial
 if not found:raise RuntimeError(('no clearing movement',start,direction,hi))
 for _ in range(12):
  mid=(lo+hi)/2
  if fn(start+direction*mid)>TH:lo=mid
  else:hi=mid
 return start+direction*hi

def spring_clear(fn,lo,hi):
 if fn(lo)<=TH:return lo
 if fn(hi)>TH:raise RuntimeError(('spring stroke exhausted',lo,hi,fn(hi)))
 for _ in range(12):
  mid=(lo+hi)/2
  if fn(mid)>TH:lo=mid
  else:hi=mid
 return hi

class Model:
 def __init__(self):
  self.a=self.x=self.w=self.b=self.h=self.m=self.q=self.p=0.
  self.max_bad=0.;self.bad=[];self.history=[]
  self.springs()
 def clone(self):return copy.deepcopy(self)
 def wm(self):return rot(mans['winding_pinion'],self.w,[0,0,0],X)
 def bm(self):return rot(mans['barrel_gear'],self.b,BP,Z)
 def hm(self):return rot(mans['setting_intermediate'],self.h,SP,Z)
 def mm(self):return rot(mans['minute_wheel'],self.m,MP,Z)
 def sm(self):return rot(mans['crown_stem'],self.a,[0,0,0],X).translate([self.x,0,0])
 def springs(self):
  bm=self.bm();wm=self.wm();cl=rot(mans['sliding_clutch'],self.a,[0,0,0],X)
  low=self.x-.009
  self.q=spring_clear(lambda q:vol(cl.translate([q,0,0]),wm),low,low+.080)
  self.p=spring_clear(lambda p:vol(mans['barrel_click'].translate([p,0,0]),bm),-.10,.27)
 def drive_winding(self,wnew):
  # Forward rotor displacement, arbor gives way by the least positive rotation.
  self.w=wnew;wm=self.wm()
  self.b=first_clear(lambda b:vol(wm,rot(mans['barrel_gear'],b,BP,Z)),self.b,1,2.)
 def drive_setting(self,sgn):
  sm=self.sm()
  self.h=first_clear(lambda h:vol(sm,rot(mans['setting_intermediate'],h,SP,Z)),self.h,-sgn,5.)
  hm=self.hm()
  self.m=first_clear(lambda m:vol(hm,rot(mans['minute_wheel'],m,MP,Z)),self.m,sgn,3.)
 def turn(self,da,check=True):
  old=self.a;delta=old-self.w;self.a+=da
  # 36-tooth face ratchet: drive flank is self-locking; coast ramp lifts.
  if da<0 and self.x<.025:
   boundary=math.floor((delta+1e-6)/10)*10
   neww=min(self.w,self.a-boundary)
   if neww<self.w:self.drive_winding(neww)
  # At neutral positions this is simply a no-contact test.
  self.drive_setting(1 if da>0 else -1)
  self.springs()
  if check:self.check()
 def arbor_positive(self,db,check=True):
  self.b+=db;bm=self.bm()
  self.w=first_clear(lambda w:vol(bm,rot(mans['winding_pinion'],w,[0,0,0],X)),self.w,-1,4.)
  self.springs()
  if check:self.check()
 def settle_hold(self):
  # Reverse until the locking flank first touches the rested click.
  # Its steep flank has radial/tangential force ratio below mu_static.
  initial=self.b
  for _ in range(120):
   oldb=self.b;oldp=self.p;trial=oldb-.1
   bm=rot(mans['barrel_gear'],trial,BP,Z)
   ptry=spring_clear(lambda p:vol(mans['barrel_click'].translate([p,0,0]),bm),-.10,.27)
   if ptry>oldp+.001:
    lo=trial;hi=oldb
    for _ in range(16):
     mid=(lo+hi)/2
     if vol(rot(mans['barrel_gear'],mid,BP,Z),mans['barrel_click'].translate([oldp,0,0]))>TH:lo=mid
     else:hi=mid
    self.b=hi
    break
   self.b=trial;self.p=ptry
  else:raise RuntimeError('click did not lock')
  bm=self.bm();oldw=self.w
  self.w=first_clear(lambda w:vol(bm,rot(mans['winding_pinion'],w,[0,0,0],X)),self.w,1,40.)
  # Crown is free; it can follow the drive flank during run-back.
  self.a+=self.w-oldw
  self.springs();self.check()
  return initial-self.b
 def pull(self,x):
  # Try rock angles permitted by the brief when axial insertion is obstructed.
  oldx=self.x;olda=self.a;self.x=x
  for rock in [0]+[s*k*1.5 for k in range(1,11) for s in [1,-1]]:
   self.a=olda+rock
   try:
    self.drive_setting(1);self.springs();self.check()
    if not self.bad:return
   except RuntimeError:pass
   self.bad=[]
  raise RuntimeError(('pull blocked',oldx,x))
 def check(self):
  posed=dict(mans)
  posed.update({'crown_stem':self.sm(),'sliding_clutch':rot(mans['sliding_clutch'],self.a,[0,0,0],X).translate([self.q,0,0]),'winding_pinion':self.wm(),'barrel_gear':self.bm(),'barrel_click':mans['barrel_click'].translate([self.p,0,0]),'setting_intermediate':self.hm(),'minute_wheel':self.mm()})
  for a,b in itertools.combinations(posed,2):
   if group[a]==group[b]:continue
   vv=vol(posed[a],posed[b])
   if vv>.000205:
    self.max_bad=max(self.max_bad,vv);self.bad.append((a,b,vv,self.a,self.x))
  if self.bad:raise RuntimeError(('collision',self.bad[-3:]))
  self.history.append([self.a,self.x,self.w,self.b,self.q,self.p,self.h,self.m])
 def turns(self,degrees):
  for _ in range(round(abs(degrees)/3)):self.turn(math.copysign(3,degrees))

if __name__=='__main__':
 results={};start=time.time()
 def log(name,data):results[name]=data;print(name,json.dumps(data),flush=True);(ROOT/'scripts/model_results.json').write_text(json.dumps(results,indent=2))
 def slide_to(model,target):
  while abs(target-model.x)>1e-10:
   model.pull(model.x+math.copysign(min(.03,abs(target-model.x)),target-model.x))
 s=Model();s.check();s.turns(-360)
 log('wind',{'arbor_degrees':s.b,'ratio':360/s.b,'minute':s.m,'collisions':len(s.bad)})
 s=Model()
 for _ in range(90):s.arbor_positive(.5)
 loss=s.settle_hold();hold=s.clone()
 # The click stays on its locking flank; free gears can be tapped through
 # their backlash without opening the radial engagement.
 log('hold',{'runback_degrees':loss,'arbor_end':s.b,'click_stroke':s.p,'reserve_hours':(6-loss/360)*8})
 for _ in range(40):s.arbor_positive(.5)
 initial=s.b;s.turns(-30)
 log('run',{'free_arbor_degrees':20,'coupled_wind_degrees':s.b-initial})
 s=hold.clone();ib=s.b;im=s.m;s.turns(360);bw=s.b-ib;mm=s.m-im;ib=s.b;s.turns(-30)
 log('backward',{'arbor_change':bw,'minute_change':mm,'coupled_wind_degrees':s.b-ib})
 s=hold.clone();stops=[]
 for target in np.linspace(0,.9,5):
  slide_to(s,target)
  tests=[]
  for deg in [-24,24]:
   t=s.clone();ib=t.b;im=t.m;t.turns(deg);tests.append({'crown':deg,'wind':t.b-ib,'set':t.m-im})
  stops.append({'x':target,'tests':tests})
 initial=s.m;s.turns(-90);forward=s.m-initial;initial=s.m;s.turns(90);back=s.m-initial
 log('set',{'stops':stops,'forward_minute':forward,'backward_minute':back,'arbor_end':s.b})
 stops=[]
 for target in np.linspace(.9,0,5):
  slide_to(s,target)
  tests=[]
  for deg in [-24,24]:
   t=s.clone();ib=t.b;im=t.m;t.turns(deg);tests.append({'crown':deg,'wind':t.b-ib,'set':t.m-im})
  stops.append({'x':target,'tests':tests})
 initial=s.b;s.turns(-90)
 log('return',{'stops':stops,'final_winding_degrees':s.b-initial})
 results['elapsed_seconds']=time.time()-start
 (ROOT/'scripts/model_results.json').write_text(json.dumps(results,indent=2))
