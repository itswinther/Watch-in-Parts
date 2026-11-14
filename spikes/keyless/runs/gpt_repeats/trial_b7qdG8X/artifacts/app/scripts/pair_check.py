from check import *

def follow(driver,output,driver_axis,output_axis,driver_point,output_point,angles,sign,threshold=.0002):
 q=0.;hist=[];maxlag=0
 for angle in angles:
  a=rotate(driver,driver_axis,angle,driver_point)
  def overlap(t):return vol(a,rotate(output,output_axis,t,output_point))
  v=overlap(q)
  if v>threshold:
   found=False
   for delta in np.arange(.1,15.0001,.1):
    new=q+sign*delta
    if overlap(new)<=threshold:
     lo=delta-.1;hi=delta
     for _ in range(12):
      mid=(lo+hi)/2
      if overlap(q+sign*mid)>threshold:lo=mid
      else:hi=mid
     q+=sign*hi;found=True;break
   if not found:return {'blocked':float(angle),'last_q':q,'vol':v}
  hist.append([float(angle),q,v])
 return hist

if __name__=='__main__':
 for label,di,out,da,oa,dp,op,sign,angles in [
 ('wind_bevel',S['winding_pinion'],S['winding_transfer'],0,2,[0,0,0],[2.75,0,0],-1,np.arange(0,-360.01,-3)),
 ('set_bevel',S['crown_stem'].translate([.9,0,0]),S['setting_transfer'],0,2,[0,0,0],[5.25,0,0],-1,np.arange(0,-90.01,-3)),
 ('wind_spur',S['winding_transfer'],S['barrel_winding_wheel'],2,2,[2.75,0,0],[2.15,4.157,0],1,np.arange(0,-360.01,-3)),
 ('set_spur',S['setting_transfer'],S['minute_wheel'],2,2,[5.25,0,0],[4.65,-4.157,0],1,np.arange(0,-90.01,-3))]:
  result=follow(di,out,da,oa,dp,op,angles,sign)
  print(label, result if isinstance(result,dict) else {'end':result[-1],'first':result[:11]},flush=True)
  (P/'scripts'/f'{label}_follow.json').write_text(json.dumps(result,indent=2))
