from motion_check import *
TH=.000195

def one_follow(driver,out,axis,point,q,sign,cap=15):
 if vol(driver,rotate(out,axis,q,point))<=TH:return q
 last=0
 for delta in np.arange(.15,cap+.001,.15):
  if vol(driver,rotate(out,axis,q+sign*delta,point))<=TH:
   lo=last;hi=delta
   for _ in range(12):
    mid=(lo+hi)/2
    if vol(driver,rotate(out,axis,q+sign*mid,point))>TH:lo=mid
    else:hi=mid
   return q+sign*hi
  last=delta
 raise RuntimeError('Blocked follower')

def sleeve_pos(stem,rotor,pull=0):
 sleeve=rotate(S['sliding_clutch'],0,stem)
 r=rotate(S['winding_pinion'],0,rotor)
 lo=max(-.005,pull-.005);hi=pull+.1
 for _ in range(18):
  mid=(lo+hi)/2
  if vol(sleeve.translate([mid,0,0]),r)>.00002:lo=mid
  else:hi=mid
 return hi

def click_pos(a,threshold=.00002):
 rat=rotate(S['barrel_winding_wheel'],2,a,[2.15,4.157,0])
 lo=-.03;hi=.25
 for _ in range(18):
  mid=(lo+hi)/2
  if vol(S['retaining_click'].translate([mid,0,0]),rat)>threshold:lo=mid
  else:hi=mid
 return hi

def checkconfig(args):
 hits=overlaps(config(**args))
 if hits:raise RuntimeError(('interference',args,hits))

results={}
# Series contact following, not imposed ideal gear ratios.
w=0;b=0;hist=[]
for t in np.arange(0,-360.01,-3):
 rotor=rotate(S['winding_pinion'],0,t)
 w=one_follow(rotor,S['winding_transfer'],2,[2.75,0,0],w,-1)
 driven=rotate(S['winding_transfer'],2,w,[2.75,0,0])
 b=one_follow(driven,S['barrel_winding_wheel'],2,[2.15,4.157,0],b,1,cap=3)
 args=dict(stem=t,rotor=t,wind=w,barrel=b,clutch=sleeve_pos(t,t))
 checkconfig(args);hist.append([float(t),float(w),float(b)])
results['wind']={'series_contact_end_deg':hist[-1],'ratio':360/b,'samples':len(hist),'interferences':0}
print('WIND',results['wind'],flush=True)
# Setting and reversing the motion at position 2.
s=0;m=0;hist=[]
for i,t in enumerate(np.r_[np.arange(0,-90.01,-3),np.arange(-87,.01,3)]):
 sign=-1 if i<=30 else 1
 driver=rotate(S['crown_stem'],0,t).translate([.9,0,0])
 s=one_follow(driver,S['setting_transfer'],2,[5.25,0,0],s,sign)
 driven=rotate(S['setting_transfer'],2,s,[5.25,0,0])
 m=one_follow(driven,S['minute_wheel'],2,[4.65,-4.157,0],m,-sign,cap=3)
 args=dict(stem=t,pull=.9,setting=s,minute=m,clutch=.9)
 checkconfig(args);hist.append([float(t),float(s),float(m)])
results['set']={'forward_end_deg':hist[30],'reverse_end_deg':hist[-1],'minute_reverse_travel':hist[30][2]-hist[-1][2],'samples':len(hist),'interferences':0}
print('SET',results['set'],flush=True)
# Independent arbor advance: gearing back-drives, clutch lifts, click rides.
maxlift=0
for a in np.arange(42,62.00001,.5):
 q=-6*a;x=sleeve_pos(0,q);maxlift=max(maxlift,x)
 checkconfig(dict(rotor=q,wind=q,barrel=a,clutch=x))
results['run']={'independent_arbor_advance_deg':20,'step_deg':.5,'largest_clutch_shift':maxlift,'interferences':0}
print('RUN',results['run'],flush=True)
# Backward at a held, phased arbor. Phase deliberately differs from the submitted rest pose.
maxlift=0
for t in np.arange(0,360.0001,3):
 q=-252;x=sleeve_pos(t,q);maxlift=max(maxlift,x)
 checkconfig(dict(stem=t,rotor=q,wind=q,barrel=42,clutch=x))
results['backward']={'crown_travel_deg':360,'largest_clutch_shift':maxlift,'arbor_travel_deg':0,'minute_travel_deg':0,'interferences':0}
print('BACKWARD',results['backward'],flush=True)
# Click drop is an abrupt rise in required outward displacement while unwinding.
prev=click_pos(45);lock=None
for a in np.arange(44.98,35.999,-.02):
 x=click_pos(a)
 if x-prev>.015:
  lock={'arbor_angle':float(a),'run_back_before_lock_deg':float(45-a),'outward_jump':float(x-prev)};break
 prev=x
results['hold_click_geometry']=lock
print('CLICK',lock,flush=True)
# Friction cone checks for analytically defined ramps and locking planes.
mu=.51
clutch_slope=.060/(.4*2*math.pi/32)
ratchet_slope=.18/(3.02*2*math.pi/60)
results['friction']={'mu_static':mu,'mu_sliding':.44,'clutch_ramp_worst_axial_normal_cosine':1/math.sqrt(1+clutch_slope**2),'click_ramp_radial_normal_cosine':1/math.sqrt(1+ratchet_slope**2),'minimum_cosine_for_a_slide':mu/math.sqrt(1+mu**2),'locking_face_slide_normal_component':0,'note':'Analytical normal-cone checks for ideal ramp/locking faces, not a full multi-contact friction solver.'}
(P/'scripts/functional_check.json').write_text(json.dumps(results,indent=2))
print('DONE',flush=True)
