import cadquery as c
for n in ['transfer_pinion','lower_bridge','middle_bridge']:
 s=c.importers.importStep('work/parts/'+n+'.step')
 for z in [-.85,-.5,.5,1.2,1.7,2,2.4,3.4,3.6,4.5,5.9]:
  try:
   sec=s.section(z); print(n,z,[(round(w.BoundingBox().xmin,2),round(w.BoundingBox().ymin,2),round(w.BoundingBox().xmax,2),round(w.BoundingBox().ymax,2)) for w in sec.vals()],flush=True)
  except Exception as e: print(e,flush=True)
