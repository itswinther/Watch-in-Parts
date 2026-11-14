from check import *
import sys
T=time.time()
movable=['crown_stem','winding_pinion','sliding_clutch','winding_transfer','setting_transfer','barrel_winding_wheel','retaining_click','minute_wheel','barrel_arbor']
fixed=[n for n in S if n not in movable]

def config(stem=0,pull=0,rotor=0,wind=0,barrel=0,setting=0,minute=0,clutch=None,click=None):
 d=dict(S)
 d['crown_stem']=rotate(S['crown_stem'],0,stem).translate([pull,0,0])
 if clutch is None:clutch=pull
 d['sliding_clutch']=rotate(S['sliding_clutch'],0,stem).translate([clutch,0,0])
 d['winding_pinion']=rotate(S['winding_pinion'],0,rotor)
 d['winding_transfer']=rotate(S['winding_transfer'],2,wind,[2.75,0,0])
 d['setting_transfer']=rotate(S['setting_transfer'],2,setting,[5.25,0,0])
 d['minute_wheel']=rotate(S['minute_wheel'],2,minute,[4.65,-4.157,0])
 d['barrel_winding_wheel']=rotate(S['barrel_winding_wheel'],2,barrel,[2.15,4.157,0])
 d['barrel_arbor']=rotate(S['barrel_arbor'],2,barrel,[2.15,4.157,0])
 if click is None:
  # Find the innermost unoccupied radial position, ignoring directionality.
  lo,hi=-.04,.25
  for _ in range(15):
   mid=(lo+hi)/2
   if vol(S['retaining_click'].translate([mid,0,0]),d['barrel_winding_wheel'])>.00002:lo=mid
   else:hi=mid
  click=hi
 d['retaining_click']=S['retaining_click'].translate([click,0,0])
 return d

def overlaps(d):
 hits=[];names=list(d)
 for i,a in enumerate(names):
  for b in names[i+1:]:
   if a in fixed and b in fixed:continue
   if {a,b}=={'barrel_arbor','barrel_winding_wheel'}:continue
   v=vol(d[a],d[b])
   if v>.0002:hits.append((a,b,v))
 return hits

def sweep(name,configs):
 maxes={};bad=[]
 for k,args in enumerate(configs):
  for a,b,v in overlaps(config(**args)):
   maxes[a,b]=max(v,maxes.get((a,b),0));bad.append((k,a,b,v))
 print(name,'bad_samples',len(set(x[0] for x in bad)),'maxes',maxes,flush=True)
 if bad:print('first',bad[:8],flush=True)
 return {'maxima':{str(k):v for k,v in maxes.items()},'first_failures':bad[:8],'samples_failed':len(set(x[0] for x in bad))}

if __name__=='__main__':
 results={}
 results['wind']=sweep('WIND',[dict(stem=t,rotor=t,wind=t,barrel=-t/6) for t in np.arange(0,-360.01,-3)])
 results['set']=sweep('SET',[dict(stem=t,pull=.9,setting=t,minute=-t/6) for t in np.r_[np.arange(0,-90.01,-3),np.arange(-90,0.01,3)]])
 results['position1_no_setting']=sweep('POSITION1_CLEAR',[dict(stem=t,rotor=t,wind=t,barrel=-t/6) for t in np.arange(0,360.01,3)])
 # Backward slips by cam height; the exact spring coordinate comes from contact.
 cc=[]
 for t in np.arange(0,360.01,3):
  lo,hi=-.005,.065
  r=rotate(S['sliding_clutch'],0,t)
  for _ in range(15):
   mid=(lo+hi)/2
   if vol(r.translate([mid,0,0]),S['winding_pinion'])>.00002:lo=mid
   else:hi=mid
  cc.append(dict(stem=t,clutch=hi))
 results['backward']=sweep('BACKWARD',cc)
 (P/'scripts/motion_check.json').write_text(json.dumps(results,indent=2))
 print('seconds',time.time()-T,flush=True)
