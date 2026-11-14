exec(open('/app/scripts/check.py').read().split("print('REST')")[0])
import math,time
D=math.pi/180
cw=j['mobiles']['winding_face_wheel']['point']; sc=j['mobiles']['setting_face_wheel']['point']; bc=[2.15,4.157,0]
def rot(n,a,axis='z',point=None):
 if point is None:point=j['mobiles'].get(n,{}).get('point',[0,0,0])
 angles=[a,0,0] if axis=='x' else [0,0,a]
 return s[n].translate(-np.array(point)).rotate(angles).translate(point)
def vol(a,b):return max(0,(a^b).volume())
def clickshift(bar):
 lo=0.;hi=.4
 if vol(s['barrel_click'],bar)<=.00018:return 0.
 for _ in range(16):
  mid=(lo+hi)/2
  if vol(s['barrel_click'].translate([mid,0,0]),bar)>.00018:lo=mid
  else:hi=mid
 return hi

def test_wind():
 mx={}; start=time.time()
 for a in np.arange(0,360.01,3):
  w=rot('winding_face_wheel',-a*8/42);b=rot('barrel',a/3.5,point=bc);p=rot('winding_pinion',-a,axis='x');stem=rot('stem',-a,axis='x');c=rot('sliding_clutch',-a,axis='x');click=s['barrel_click'].translate([clickshift(b),0,0])
  moved={'winding_face_wheel':w,'barrel':b,'winding_pinion':p,'stem':stem,'sliding_clutch':c,'barrel_click':click}
  fixed={k:s[k] for k in ['bearing_bridge','minute_wheel','setting_face_wheel','main_plate','dial_plate','minute_post']}
  names=list(moved)
  for i,n in enumerate(names):
   for k,other in list(moved.items())[i+1:]+list(fixed.items()):
    v=vol(moved[n],other);key=n+'/'+k
    if v>mx.get(key,(0,0))[0]:mx[key]=(v,float(a))
 print('WIND violations', {k:v for k,v in mx.items() if v[0]>.0002},'elapsed',time.time()-start,flush=True)
 json.dump(mx,open('/app/scripts/wind_motion.json','w'),indent=2)
def test_set():
 mx={};start=time.time()
 for a in np.arange(-90,90.001,3):
  stem=rot('stem',-a,axis='x').translate([.9,0,0]);c=rot('sliding_clutch',-a,axis='x').translate([.9,0,0]);g=rot('setting_face_wheel',-a*8/20);minute=rot('minute_wheel',a*2/9,point=[4.65,-4.157,0])
  moved={'stem':stem,'sliding_clutch':c,'setting_face_wheel':g,'minute_wheel':minute};fixed={k:s[k] for k in ['bearing_bridge','winding_pinion','winding_face_wheel','barrel','barrel_click','main_plate','dial_plate','minute_post']}
  names=list(moved)
  for i,n in enumerate(names):
   for k,other in list(moved.items())[i+1:]+list(fixed.items()):
    v=vol(moved[n],other);key=n+'/'+k
    if v>mx.get(key,(0,0))[0]:mx[key]=(v,float(a))
 print('SET violations', {k:v for k,v in mx.items() if v[0]>.0002},'elapsed',time.time()-start,flush=True)
 json.dump(mx,open('/app/scripts/set_motion.json','w'),indent=2)
if __name__=='__main__':
 test_wind();test_set()
