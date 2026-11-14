from check import *
pin=shapes['winding_pinion'];inter=shapes['winding_transfer'];bar=shapes['barrel_ratchet'];setter=shapes['setting_transfer'];minute=shapes['minute_wheel'];cx=k['mobiles']['setting_transfer']['point'][0]
res={}
for mode in ['face','spur','setting_face','setting_spur']:
 values=[]
 for angle in np.arange(0,360.01,3):
  if mode=='face':a=rot(pin,-angle,axis='x');b=rot(inter,-angle/1.2,(2.15,0,0))
  if mode=='spur':a=rot(inter,-angle/1.2,(2.15,0,0));b=rot(bar,angle/4.95,(2.15,4.157,0))
  if mode=='setting_face':
   a=rot(shapes['stem'].translate((.9,0,0)),-angle,axis='x');b=rot(setter,angle/1.2,(cx,0,0))
  if mode=='setting_spur':a=rot(setter,angle/1.2,(cx,0,0));b=rot(minute,-angle/1.2*8/36,(4.65,-4.157,0))
  v=overlap(a,b);values.append(v)
 print(mode,'max',max(values),'bad',sum(v>.0002 for v in values),flush=True)
 res[mode]={'max_overlap':max(values),'bad':sum(v>.0002 for v in values),'volumes':values}
json.dump(res,open('/app/scripts/mesh_checks.json','w'),indent=2)
