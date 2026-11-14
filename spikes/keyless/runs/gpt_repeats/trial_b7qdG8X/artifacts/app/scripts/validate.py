from check import *
import re,struct
OUT=P/'submission';own=list((OUT/'parts').glob('*.stl'));assert len(own)<=40
refs=[p for m in D['mobiles'].values() for p in m['parts']]+D['fixed'];assert len(set(refs))==len(refs)
assert set(refs)=={p.stem for p in own}
assert D['mobiles']['stem']['kind']=='stem' and D['mobiles']['barrel']['kind']=='barrel'
info={};maxr=0;tri=0
for p in own:
 assert p.is_file() and not p.is_symlink() and re.fullmatch('[A-Za-z0-9_-]{1,40}',p.stem)
 raw=p.read_bytes();n=struct.unpack('<I',raw[80:84])[0];assert len(raw)==84+50*n and n<=200000
 m=trimesh.load(p);assert m.is_watertight and m.is_winding_consistent and m.volume>0
 assert len(S[p.stem].decompose())==1
 r=np.linalg.norm(m.vertices[:,:2]-[3.5,0],axis=1)
 assert np.max(np.abs(m.vertices[:,2]))<=3.40001
 if p.stem!='crown_stem':assert r.max()<=8.70001;maxr=max(maxr,float(r.max()))
 else:assert m.vertices[:,0].max()>=12.7
 tri+=n;info[p.stem]={'triangles':n,'volume_mm3':float(m.volume)}
fixed_names=set(D['fixed'])|{'main_plate','dial_plate','minute_post'}
max_overlap=0
for i,a in enumerate(S):
 for b in list(S)[i+1:]:
  if a in fixed_names and b in fixed_names:continue
  if {a,b}=={'barrel_winding_wheel','barrel_arbor'}:continue
  v=vol(S[a],S[b]);max_overlap=max(max_overlap,v);assert v<=.0002,(a,b,v)
held=[]
for name,mob in D['mobiles'].items():
 if mob['kind'] not in ['free','spring']:continue
 axis=np.argmax(np.abs(mob['direction']))
 for i in range(3):
  if i==axis and mob['dof']!='rot':continue
  for sign in [-1,1]:
   off=np.eye(3)[i]*sign*.3
   overlap=max(vol(S[p].translate(off),b) for p in mob['parts'] for n,b in S.items() if n not in mob['parts'])
   assert overlap>.0002,(name,off,overlap)
   held.append(float(overlap))
rp=OUT/'report.json';assert rp.is_file() and not rp.is_symlink() and rp.stat().st_size<=100000
r=json.loads(rp.read_text());assert set(r['steps'])=={'assemble','wind','hold','run','backward','set','return'}
assert set(r['steps'].values())<= {'pass','fail','not_tested'}
result={'parts':len(own),'total_triangles':tri,'largest_triangle_count':max(x['triangles'] for x in info.values()),'max_nonstem_case_radius':maxr,'max_rest_overlap_mm3':max_overlap,'retention_probes':len(held),'smallest_retention_overlap_mm3':min(held),'part_details':info}
(P/'scripts/final_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='part_details'},indent=2))
