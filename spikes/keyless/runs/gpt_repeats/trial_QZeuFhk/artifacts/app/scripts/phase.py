from check import *
def rot(m,deg,point,axis):
 a=np.deg2rad(deg);d=np.array(axis,float);d/=np.linalg.norm(d);K=np.array([[0,-d[2],d[1]],[d[2],0,-d[0]],[-d[1],d[0],0]]);R=np.eye(3)+np.sin(a)*K+(1-np.cos(a))*(K@K);p=np.array(point);T=np.column_stack((R,p-R@p));return m.transform(T)
if __name__=='__main__':
 for a,b,p,d,span in [('barrel_gear','winding_pinion',[2.15,4.157,0],[0,0,1],9),('setting_intermediate','minute_wheel',[7,math.sqrt(5.7**2-2.35**2)-4.157,0],[0,0,1],360/21)]:
  print(a)
  vals=[]
  for angle in np.linspace(0,span,37):
   v=vol(rot(mans[a],angle,p,d),mans[b]);vals.append((v,angle))
  print('best',sorted(vals)[:5],flush=True)
