from contact_check import *

def sleeve_q(stemangle,pinionangle):
 rotor=rot('winding_pinion',pinionangle,axis='x');clutch=rot('sliding_clutch',stemangle,axis='x')
 if vol(clutch,rotor)<=TH:return 0
 lo=0;hi=.17
 for _ in range(17):
  mid=(lo+hi)/2
  if vol(clutch.translate([mid,0,0]),rotor)>TH:lo=mid
  else:hi=mid
 return hi

def hold():
 lo=0;hi=None
 for rb in np.arange(0,30,.05):
  if vol(rot('barrel',45-rb,point=bc),s['barrel_click'])>TH:hi=rb;break
  lo=rb
 if hi is None:raise RuntimeError('click did not hold')
 for _ in range(17):
  mid=(lo+hi)/2
  if vol(rot('barrel',45-mid,point=bc),s['barrel_click'])>TH:hi=mid
  else:lo=mid
 b=45-lo
 print('Hold click boundary: runback',lo,'reserve hours',(6-lo/360)*8,flush=True)
 return b,lo

def backward(b):
 pa=-b*3.5;ca=-b*2/3;mx={};qs=[]
 for a in np.arange(0,360.001,3):
  q=sleeve_q(a,pa);qs.append(q)
  c=rot('sliding_clutch',a,axis='x').translate([q,0,0]);stem=rot('stem',a,axis='x')
  env={'stem':stem,'winding_pinion':rot('winding_pinion',pa,axis='x'),'winding_face_wheel':rot('winding_face_wheel',ca),'barrel':rot('barrel',b,point=bc),**{k:s[k] for k in ['bearing_bridge','main_plate','dial_plate','minute_post','minute_wheel','setting_face_wheel','barrel_click']}}
  for k,ob in env.items():mx['clutch/'+k]=max(mx.get('clutch/'+k,0),vol(c,ob))
  for k in ['bearing_bridge','winding_pinion','winding_face_wheel','setting_face_wheel']:
   mx['stem/'+k]=max(mx.get('stem/'+k,0),vol(stem,env[k]))
 print('Backward clutch q range',min(qs),max(qs),'violations',{k:v for k,v in mx.items() if v>TH+1e-7},flush=True)
 return {'q_range':[min(qs),max(qs)],'intersections':mx}

def restart(b,crown_turn=30):
 p0=b*3.5;c0=b*2/3;p=p0;c=c0;bar=b;q=sleeve_q(0,-p)
 for i in range(1,int(crown_turn/3)+1):
  a=i*3;clutch=rot('sliding_clutch',-a,axis='x').translate([q,0,0])
  # Choose a pinion orientation near its current turn count; min move along winding side.
  p=first_clear(lambda x:rot('winding_pinion',-x,axis='x'),clutch,p,3,span=4)
  q=sleeve_q(-a,-p)
  c=first_clear(lambda x:rot('winding_face_wheel',-x),rot('winding_pinion',-p,axis='x'),c,3*8/42)
  bar=first_clear(lambda x:rot('barrel',x,point=bc),rot('winding_face_wheel',-c),bar,3/3.5)
 print('Restart after hold:',crown_turn,'crown ->',bar-b,'barrel',flush=True)
 return bar-b
if __name__=='__main__':
 b,rb=hold();result={'hold_runback_deg':rb,'reserve_h':(6-rb/360)*8,'backward':backward(b),'restart_deg':restart(b),'restart_after_20_arbor_deg':restart(b+20),'position_1_test_24_deg':restart(b,24),'return_90_deg':restart(b,90)}
 json.dump(result,open('/app/scripts/ratchet_results.json','w'),indent=2)
