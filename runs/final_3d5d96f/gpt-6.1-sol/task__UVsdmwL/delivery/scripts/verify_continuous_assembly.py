exec(open('/app/check_more.py').read().split('# Exact process-sheet')[0])
assy=json.load(open(D+'/assembly.json')); installed=[]
for name in assy['order']:
 m=sol[name];v=verts(m);z=np.unique(np.round(v[:,2],6));pieces=[]
 for lo,hi in zip(z[:-1],z[1:]):
  if hi-lo<1e-5:continue
  cs=m.slice((lo+hi)/2)
  if not cs.is_empty():pieces.append(cs.extrude(25+hi-lo).translate([0,0,float(lo)]))
 swept=union(pieces);worst=0;obstacle=None
 for n in installed:
  vol=ivol(swept,sol[n])
  if vol>worst:worst=vol;obstacle=n
 print('SWEPT_INSERT',name,worst,obstacle,flush=True)
 installed.append(name)
