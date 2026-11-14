exec(open('scripts/check.py').read().split("m=json.loads")[0])
doc=json.loads(Path('work/movement.json').read_text())
names=doc['fixed']+sum([v['parts'] for v in doc['mobiles'].values()],[])
for n in names:
 man=load(n);bb=man.bounding_box()
 for j in [0,.017,.033]:
  o,sz=k.grid_for(bb[:3],bb[3:],.05,np.array([.15+j]*3))
  solid=k.voxelize(man,o,sz,.05);pieces,dev=k.opening_test(solid,1.5,1.)
  print(n,'jitter',j,'pieces',pieces,'max_distance',dev*.05,'pass',pieces>0 and dev*.05<=.2,flush=True)
