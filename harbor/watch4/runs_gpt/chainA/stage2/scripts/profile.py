import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_CurveType
s=cq.importers.importStep('work/parts/hour_driver16.step').val()
for f in s.Faces():
 if f.geomType()=='PLANE' and f.Center().z>5.69:
  for w in f.Wires():
   print('WIRE',len(w.Edges()))
   for e in w.Edges()[:15]:
    print(e.geomType(),[(round(v.X,5),round(v.Y,5)) for v in e.Vertices()])
