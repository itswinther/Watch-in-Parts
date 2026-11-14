from functional_check import one_follow,sleeve_pos,checkconfig
from check import *
# Search the allowed rocking phases only if the axial step cannot be made at the current phase.
q=0.;minute=0.;theta=0.;log=[]
for direction,positions in [('pull',np.arange(0,.90001,.03)),('push',np.arange(.87,-.00001,-.03))]:
 for p in positions:
  p=float(max(0,p));attempts=[];found=False
  rocks=[0]+[s*v for v in np.arange(1.5,15.001,1.5) for s in [-1,1]]
  for rock in rocks:
   t=theta+rock
   d=rotate(S['crown_stem'],0,t).translate([p,0,0])
   # Nearest rotational clearance of the setting wheel, allowing both directions.
   candidates=[(0,q)]
   for dist in np.arange(.25,18.001,.25):candidates.extend([(dist,q-dist),(dist,q+dist)])
   for distance,qq in candidates:
    if vol(d,rotate(S['setting_transfer'],2,qq,[5.25,0,0]))<=.00019:
     args=dict(stem=t,pull=p,setting=qq,minute=-qq/6,clutch=max(p-.004,0))
     try:checkconfig(args)
     except RuntimeError:continue
     q=qq;theta=t;minute=-qq/6
     log.append({'operation':direction,'pull':p,'stem_deg':t,'setting_deg':q,'rock':rock,'wheel_adjustment':distance});found=True;break
   if found:break
  if not found:raise RuntimeError(('NO SELECTOR PATH',direction,p,theta,q))
print('PULL_PUSH',len(log),'poses','largest rock',max(abs(x['rock']) for x in log),'largest wheel move',max(x['wheel_adjustment'] for x in log),flush=True)
(P/'scripts/pull_check.json').write_text(json.dumps(log,indent=2))
