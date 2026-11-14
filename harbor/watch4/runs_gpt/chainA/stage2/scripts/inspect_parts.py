import cadquery as cq,json
m=json.load(open('work/movement.json'))
for n in m['fixed']+sum([v['parts'] for v in m['mobiles'].values()],[]):
 s=cq.importers.importStep('work/parts/'+n+'.step').val(); b=s.BoundingBox()
 print(n, 'bb',tuple(round(v,4) for v in (b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax)), 'vol',round(s.Volume(),4))
