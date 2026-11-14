from phase import rot
from check import *
def run(a,b,pa,da,pb,db,ratio,span=360,step=3):
 vals=[]
 for deg in np.arange(0,span+step/2,step):
  v=vol(rot(mans[a],deg,pa,da),rot(mans[b],deg*ratio,pb,db));vals.append((round(v,8),deg))
 print(a,b,'max',sorted(vals,reverse=True)[:8],'nonzero',sum(v>.0002 for v,a in vals),flush=True)
run('winding_pinion','barrel_gear',[0,0,0],[1,0,0],[2.15,4.157,0],[0,0,1],-.2)
ys=math.sqrt(5.7**2-2.35**2)-4.157
run('setting_intermediate','minute_wheel',[7,ys,0],[0,0,1],[4.65,-4.157,0],[0,0,1],-21/36,span=120,step=2)
mans['crown_stem']=mans['crown_stem'].translate([.9,0,0])
run('crown_stem','setting_intermediate',[0,0,0],[1,0,0],[7,ys,0],[0,0,1],-12/18,span=180)
