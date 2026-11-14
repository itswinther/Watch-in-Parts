from contact_checks import *
result=[]
cx=k['mobiles']['setting_transfer']['point'][0]
for pull in [0,.225,.45,.675,.9]:
 for sign in [-1,1]:
  sf=0;mn=0;maxwind=0
  for ang in np.arange(3,24.001,3):
   stem=rot(shapes['stem'].translate((pull,0,0)),sign*ang,axis='x')
   sf=follow(stem,shapes['setting_transfer'],sf,(cx,0,0),'z',-sign,6)
   mn=follow(rot(shapes['setting_transfer'],sf,(cx,0,0)),shapes['minute_wheel'],mn,(4.65,-4.157,0),'z',sign,2,.1)
   if pull>=.225:
    sleeve=rot(shapes['sliding_clutch'],sign*ang,axis='x').translate((pull-.03,0,0))
    maxwind=max(maxwind,overlap(sleeve,shapes['winding_pinion']))
  row={'pull':pull,'crown':sign*24,'setting_transfer':sf,'minute':mn,'wind_clutch_overlap_when_disengaged':maxwind}
  print(row,flush=True);result.append(row)
# Pure axial insertion of the initially aligned setting pinion, all 0.03 mm steps.
vs=[]
for pull in np.arange(0,.90001,.03):
 vs.append(overlap(shapes['stem'].translate((pull,0,0)),shapes['setting_transfer']))
print('AXIAL aligned max overlap',max(vs),flush=True)
json.dump({'stops':result,'aligned_pull_max_overlap':max(vs),'winding_clutch_release_pull_bound':.056,'setting_contact_pull_lower_bound':.62},open('/app/scripts/stop_checks.json','w'),indent=2)
