from check import *
from phase import rot
pi=math.pi
R={};files=[]
for p in sorted((ROOT/'submission/parts').glob('*.stl')):
 m=meshes[p.stem];rr=np.linalg.norm(m.vertices[:,:2]-[3.5,0],axis=1)
 files.append({'name':p.stem,'triangles':len(m.faces),'binary_size_valid':p.stat().st_size==84+50*len(m.faces),'watertight':bool(m.is_watertight),'components':len(m.split()),'volume':m.volume,'max_case_radius':float(rr.max()),'z_min':float(m.bounds[0,2]),'z_max':float(m.bounds[1,2])})
R['files']=files;overlaps=[]
for a,b in itertools.combinations(meshes,2):
 if group[a]==group[b]:continue
 v=vol(mans[a],mans[b])
 if v>.0002:overlaps.append([a,b,v])
R['rest_overlap_failures']=overlaps
held=[]
for name,mob in C['mobiles'].items():
 if mob['kind'] not in ['free','spring']:continue
 d=np.array(mob['direction'],float);d/=np.linalg.norm(d);u=np.cross(d,[0,0,1] if abs(d[2])<.9 else [1,0,0]);u/=np.linalg.norm(u);v=np.cross(d,u)
 dirs=[u*np.cos(a)+v*np.sin(a) for a in np.linspace(0,2*pi,32,endpoint=False)]
 if mob['dof']=='rot':dirs.extend([d,-d])
 minmax=1e9
 for dd in dirs:
  maxv=0
  for p in mob['parts']:
   mm=mans[p].translate(.3*dd)
   for other in meshes:
    if group[other]!=name:maxv=max(maxv,vol(mm,mans[other]))
  minmax=min(minmax,maxv)
 held.append({'mobile':name,'tested_directions':len(dirs),'minimum_largest_overlap':minmax,'pass':minmax>.0002})
R['retention']=held
# Whole-period, ideal conjugate gear trajectories; quantify actual mesh envelope.
YS=math.sqrt(5.7**2-2.35**2)-4.157
sweeps=[]
for na,nb,pa,axisa,pb,axisb,ratio,span,shift in [('winding_pinion','barrel_gear',[0,0,0],[1,0,0],[2.15,4.157,0],[0,0,1],-.2,360,0),('setting_intermediate','minute_wheel',[7,YS,0],[0,0,1],[4.65,-4.157,0],[0,0,1],-21/36,120,0),('crown_stem','setting_intermediate',[0,0,0],[1,0,0],[7,YS,0],[0,0,1],-12/18,180,.9)]:
 vals=[]
 for angle in np.arange(0,span+1,3):
  a=rot(mans[na].translate([shift,0,0]),angle,pa,axisa);b=rot(mans[nb],angle*ratio,pb,axisb)
  vals.append(vol(a,b))
 sweeps.append({'pair':[na,nb],'sample_count':len(vals),'maximum_overlap':max(vals),'pass':max(vals)<=.0002})
R['gear_sweeps']=sweeps
# Friction cones. A ramp can lift its radial/axial follower when slope<1/mu;
# above this value the flank is self-locking under the specified static mu.
mu=.51
R['friction_screen']={'mu_static':mu,'mu_sliding':.44,'locking_slope_threshold':1/mu,'clutch_coast_max_slope':.04/(.32*math.radians(10)),'clutch_drive_min_slope':(.04*11/12)/(.50*math.radians(10/12)),'click_coast_slope_approx':.25/(2.85*math.radians(10)),'click_lock_slope_approx':.245/(3.1*math.radians(.2)),'crossed_helical_drive_margin':math.cos(math.atan(math.tan(math.radians(20))/math.cos(pi/4)))/math.sqrt(2)-mu/math.sqrt(2)}
R['assemble_pass']=len(files)<=40 and not overlaps and all(f['watertight'] and f['components']==1 and f['volume']>0 and f['triangles']<=200000 and f['binary_size_valid'] and f['z_min']>=-3.4 and f['z_max']<=3.4 and (f['name']=='crown_stem' or f['max_case_radius']<=8.7) for f in files) and all(x['pass'] for x in held)
(ROOT/'scripts/audit_results.json').write_text(json.dumps(R,indent=2))
print(json.dumps({k:v for k,v in R.items() if k!='files'},indent=2),flush=True)
