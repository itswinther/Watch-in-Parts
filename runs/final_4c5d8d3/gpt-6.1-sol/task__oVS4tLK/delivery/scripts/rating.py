# Conservative Lewis tooth ratings at the full 70.1 N mm bridle maximum.
# Torque branching is not credited: every branch is rated as if it took the full torque.
import json,math
Y={12:.2546,24:.3634,30:.3902,36:.4093,40:.4193,48:.4349,60:.4516,96:.4794}
results={}
for tag,n,mod in [('8h',40,.2),('6h',30,8/35)]:
 torque={'barrel':70.1};rows=[]
 edges=[('barrel',96,'input',12,.2,.4545),('input',n,'minute',40,mod,.4),('minute',36,'third',12,.2,.4),('third',48,'fourth',12,.175,.4),('fourth',60,'fifth',12,.15,.4),('fifth',12,'seconds',12,.4,.4),('minute',12,'reduction',36,.23125,.4),('reduction',12,'hour',48,.185,.5),('hour',12,'idler',12,.34,.6),('idler',12,'day',24,.34,.6)]
 for a,na,b,nb,m,width in edges:
  force=torque[a]/(na*m/2);torque[b]=torque[a]*nb/na
  sigma=max(force/(width*m*Y[na]),force/(width*m*Y[nb]))
  rows.append(dict(driver=a,driven=b,tangential_force_N=force,Lewis_max_MPa=sigma,conservative_steel_proof_MPa=1450,below_conservative_proof=sigma<1450))
 results[tag]=dict(teeth=rows,nominal_mobile_torques_Nmm=torque)
print(json.dumps(results,indent=2))
