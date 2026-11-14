from contact_check import *

def partial(p,sign):
 g=m=0.;mx={};
 for i in range(0,9):
  a=sign*i*3;stem=rot('stem',-a,axis='x').translate([p,0,0])
  if i==0:
   v=vol(stem,s['setting_face_wheel'])
   if v>TH:print('START collision',p,v,flush=True)
  try:g=first_clear(lambda x:rot('setting_face_wheel',-sign*x),stem,g,3*8/20,span=5)
  except RuntimeError as e: print('BLOCKED',p,sign,i,str(e),flush=True);return
  wheel=rot('setting_face_wheel',-sign*g)
  m=first_clear(lambda x:rot('minute_wheel',sign*x,point=[4.65,-4.157,0]),wheel,m,3*2/9)
  poses={'stem':stem,'sliding_clutch':rot('sliding_clutch',-a,axis='x').translate([p,0,0]),'setting_face_wheel':wheel,'minute_wheel':rot('minute_wheel',sign*m,point=[4.65,-4.157,0])}
  for n,ob in poses.items():
   for k in ['bearing_bridge','winding_pinion','winding_face_wheel','barrel','barrel_click','main_plate','dial_plate','minute_post']:
    v=vol(ob,s[k]);key=n+'/'+k
    mx[key]=max(mx.get(key,0),v)
 print('Partial',p,sign,'set',sign*m,'bad',{k:round(v,7) for k,v in mx.items() if v>TH},flush=True)
 return g,m
if __name__=='__main__':
 for p in [.225,.45,.675,.9]:
  for sign in [1,-1]:partial(p,sign)
