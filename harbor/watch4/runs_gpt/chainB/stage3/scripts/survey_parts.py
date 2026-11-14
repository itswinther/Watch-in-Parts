import cadquery as cq, json
from pathlib import Path
for p in Path('work/parts').glob('*.step'):
 s=cq.importers.importStep(str(p)).val(); b=s.BoundingBox()
 print(p.stem, 'bounds',*[round(v,4) for v in (b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax)],'vol',round(s.Volume(),3))
