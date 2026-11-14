import cadquery as cq
import json
from pathlib import Path
for p in Path('work/parts').glob('*.step'):
 s=cq.importers.importStep(str(p)).val(); b=s.BoundingBox()
 print(p.stem, 'bounds',*[round(v,4) for v in (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax)],'vol',round(s.Volume(),4))
 cs=[]
 for f in s.Faces():
  if f.geomType()=='CYLINDER':
   from OCP.BRepAdaptor import BRepAdaptor_Surface
   c=BRepAdaptor_Surface(f.wrapped).Cylinder();a=c.Axis();l=a.Location()
   cs.append(tuple(round(v,4) for v in (c.Radius(),l.X(),l.Y(),l.Z(),f.BoundingBox().zmin,f.BoundingBox().zmax)))
 print(' cylinders',sorted(set(cs)))
