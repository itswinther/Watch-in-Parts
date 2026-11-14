from check import *
import re,struct
results={'parts':{},'manifest':{},'friction':{}}
assert len(k['mobiles'])==7
listed=k['fixed']+sum([v['parts'] for v in k['mobiles'].values()],[])
assert len(listed)==len(set(listed))==12
assert set(listed)=={f[:-4] for f in os.listdir(P+'parts') if f.endswith('.stl')}
for n in listed:
 assert re.fullmatch('[A-Za-z0-9_-]{1,40}',n)
 path=P+'parts/'+n+'.stl';raw=open(path,'rb').read();nf=struct.unpack('<I',raw[80:84])[0]
 assert len(raw)==84+nf*50 and nf<=200000
 m=meshes[n];s=shapes[n]
 assert m.is_watertight and m.volume>0 and len(s.decompose())==1
 results['parts'][n]={'triangles':nf,'volume':m.volume,'closed':m.is_watertight,'components':len(s.decompose())}
rad=np.linalg.norm(meshes['stem'].vertices[:,:2]-[3.5,0],axis=1)
assert rad.max()>=9.2
stat=json.load(open('/app/scripts/static_checks.json'))
assert not stat['collisions'] and not stat['bounds']
assert min(v for vs in stat['held'].values() for v in vs)>.0002
results['manifest']={'parts':len(listed),'mobiles':len(k['mobiles']),'triangles_total':sum(x['triangles'] for x in results['parts'].values()),'stem_reaches_beyond_case':rad.max()-8.7,'minimum_retention_overlap':min(v for vs in stat['held'].values() for v in vs)}
# Conservative two-interface wedge-release condition tan(alpha)<(1-mu^2)/(2mu).
mu=.51
results['friction']={'static_coefficient':mu,'two_interface_release_limit_degrees':math.degrees(math.atan((1-mu*mu)/(2*mu))),'clutch_ramp_worst_degrees':math.degrees(math.atan(.025/(.26*(2*pi/36-.0002)))),'clutch_drive_flank_min_degrees':math.degrees(math.atan(.025/(.54*.0002))),'click_ramp_degrees':math.degrees(math.atan(.22/(3.43*2*pi/36)))}
json.dump(results,open('/app/scripts/final_validation.json','w'),indent=2)
print(json.dumps({'manifest':results['manifest'],'friction':results['friction']},indent=2))
