from ratchet_check import *

def pairs(poses,skip=()):
 bad={};names=list(poses)
 for i,n in enumerate(names):
  for k in names[i+1:]:
   if {n,k}=={'barrel','barrel_arbor'}:continue
   if body.get(n)==body.get(k)=='fixed':continue
   v=vol(poses[n],poses[k])
   if v>TH+1e-7:bad[n+'/'+k]=v
 return bad

def travel(b):
 pa=-b*3.5;ca=-b*2/3;q0=sleeve_q(0,pa);bad={}
 for p in np.linspace(0,.9,31):
  poses=dict(s);poses.update(stem=s['stem'].translate([p,0,0]),sliding_clutch=s['sliding_clutch'].translate([max(p,q0),0,0]),barrel=rot('barrel',b,point=bc),barrel_arbor=rot('barrel_arbor',b,point=bc),winding_pinion=rot('winding_pinion',pa,axis='x'),winding_face_wheel=rot('winding_face_wheel',ca))
  v=pairs(poses)
  if v:bad[str(float(p))]=v
 print('Pull/push at 0.03 increments violations',bad,flush=True)
 return bad

def arbor_run(b):
 bad={};qs=[]
 for db in np.arange(0,20.001,.5):
  bb=b+db;pa=-bb*3.5;ca=-bb*2/3;q=sleeve_q(0,pa);qs.append(q)
  poses=dict(s);poses.update(sliding_clutch=s['sliding_clutch'].translate([q,0,0]),barrel=rot('barrel',bb,point=bc),barrel_arbor=rot('barrel_arbor',bb,point=bc),winding_pinion=rot('winding_pinion',pa,axis='x'),winding_face_wheel=rot('winding_face_wheel',ca));poses['barrel_click']=s['barrel_click'].translate([clickshift(poses['barrel']),0,0])
  v=pairs(poses)
  if v:bad[str(float(db))]=v
 print('Arbor-only 20 degree travel violations',bad,'clutch range',min(qs),max(qs),flush=True)
 return bad

def dense_gears():
 mx={};
 for a in np.arange(0,45.001,.25):
  p=rot('winding_pinion',-a,axis='x');c=rot('winding_face_wheel',-a*8/42);b=rot('barrel',a/3.5,point=bc)
  ps=rot('stem',-a,axis='x').translate([.9,0,0]);g=rot('setting_face_wheel',-a*.4);minute=rot('minute_wheel',a*2/9,point=[4.65,-4.157,0])
  for k,v in {'pinion/face':vol(p,c),'wind spur pair':vol(c,b),'setting face':vol(ps,g),'setting spur pair':vol(g,minute)}.items():mx[k]=max(mx.get(k,0),v)
 print('Dense gear sweeps max intersections',mx,flush=True)
 return mx
if __name__=='__main__':
 b,rb=hold();result={'translation':travel(b),'arbor_run':arbor_run(b),'dense_gears':dense_gears()};json.dump(result,open('/app/scripts/travel_results.json','w'),indent=2)
