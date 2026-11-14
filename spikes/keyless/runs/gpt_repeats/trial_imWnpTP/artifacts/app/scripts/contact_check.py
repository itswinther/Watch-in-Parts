from motion import *
TH=.0002
# The rig's intersection allowance, used as the contact boundary.
def first_clear(make,obstacle,old,step,span=None):
 if vol(make(old),obstacle)<=TH:return old
 if span is None:span=step*2+.5
 grid=np.arange(old+step/16,old+span+step/32,step/16)
 lo=old
 for hi in grid:
  if vol(make(hi),obstacle)<=TH:
   for _ in range(11):
    mid=(lo+hi)/2
    if vol(make(mid),obstacle)>TH:lo=mid
    else:hi=mid
   return hi
  lo=hi
 raise RuntimeError('no clear state '+str((old,step,span)))

def winding(nsteps=120):
 p=c=b=0.;rows=[]
 for i in range(1,nsteps+1):
  a=i*3;clutch=rot('sliding_clutch',-a,axis='x')
  p=first_clear(lambda x:rot('winding_pinion',-x,axis='x'),clutch,p,3)
  pinion=rot('winding_pinion',-p,axis='x')
  c=first_clear(lambda x:rot('winding_face_wheel',-x),pinion,c,3*8/42)
  crown=rot('winding_face_wheel',-c)
  b=first_clear(lambda x:rot('barrel',x,point=bc),crown,b,3/3.5)
  bar=rot('barrel',b,point=bc);q=clickshift(bar)
  if vol(s['barrel_click'].translate([q,0,0]),s['bearing_bridge'])>TH:raise RuntimeError('click bracket collision')
  rows.append([a,p,c,b,q])
 print('Contact winding: crown, pinion, face, barrel, ratio:',a,p,c,b,a/b,flush=True)
 return rows

def setting(sign):
 g=m=0.;rows=[]
 for i in range(1,31):
  a=sign*i*3;stem=rot('stem',-a,axis='x').translate([.9,0,0])
  g=first_clear(lambda x:rot('setting_face_wheel',-sign*x),stem,g,3*8/20)
  wheel=rot('setting_face_wheel',-sign*g)
  m=first_clear(lambda x:rot('minute_wheel',sign*x,point=[4.65,-4.157,0]),wheel,m,3*2/9)
  rows.append([a,sign*g,sign*m])
 print('Contact setting',sign,'crown,face,minute:',a,sign*g,sign*m,flush=True)
 return rows
if __name__=='__main__':
 results={'wind':winding(),'set_forward':setting(1),'set_backward':setting(-1)}
 json.dump(results,open('/app/scripts/contact_results.json','w'),indent=2)
