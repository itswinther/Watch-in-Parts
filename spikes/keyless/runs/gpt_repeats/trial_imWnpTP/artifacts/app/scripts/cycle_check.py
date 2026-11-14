from travel_check import *

def set_cycle():
 g=m=0.; bad={};seq=[]
 for sign,aa in [(1,np.arange(3,90.001,3)),(-1,np.arange(87,-.001,-3))]:
  start=m
  for a in aa:
   stem=rot('stem',-a,axis='x').translate([.9,0,0]);old=g
   dg=first_clear(lambda x:rot('setting_face_wheel',-(old+sign*x)),stem,0,1.2)
   g=old+sign*dg;wheel=rot('setting_face_wheel',-g);old=m
   dm=first_clear(lambda x:rot('minute_wheel',old+sign*x,point=[4.65,-4.157,0]),wheel,0,2/3)
   m=old+sign*dm;seq.append([float(a),g,m])
  print('Sequential setting leg',sign,'minute travel',m-start,flush=True)
 # Push out of the actual ending gear phase.
 for p in np.linspace(.9,0,31):
  st=rot('stem',0,axis='x').translate([p,0,0]);v=vol(st,rot('setting_face_wheel',-g))
  if v>TH:bad[str(p)]=v
 print('Push after setting-cycle intersections',bad,flush=True)
 return {'sequence':seq,'push_bad':bad}

def friction():
 mu=.51;ri=.54;ro=.94;h=.15
 lift_min=ri*(11.7*D)/h;lock_max=ro*(3.3*D)/h
 pa_max=math.degrees(math.acos((.48*math.cos(25*D))/.6));phi=math.degrees(math.atan(mu))
 result={'static_mu':mu,'sliding_mu':.44,'clutch_ramp_min_axial_to_tangential_normal':lift_min,'clutch_lock_max_axial_to_tangential_normal':lock_max,'pinion_max_pressure_angle_deg':pa_max,'friction_angle_deg':phi,'click_ramp_min_radial_to_tangential_normal':1.55/(.35/(15*D))}
 assert lift_min>mu and lock_max<.44 and pa_max+phi<90
 print('Friction checks',result,flush=True)
 return result
if __name__=='__main__':
 r={'cycle':set_cycle(),'friction':friction()};json.dump(r,open('/app/scripts/cycle_results.json','w'),indent=2)
