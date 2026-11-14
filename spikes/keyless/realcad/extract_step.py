"""NOT-FOR-AGENT (realcad test material; never copy into a task image).

List every leaf solid of a STEP assembly with its instance path, global bbox, volume; save each as STL.

    python -I extract_step.py IN.stp OUT_DIR
"""
import json
import os
import re
import sys

from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopLoc import TopLoc_Location
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.StlAPI import StlAPI_Writer
from OCP.BRepTools import BRepTools

src, out = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(out, "brep"), exist_ok=True)
doc = TDocStd_Document(TCollection_ExtendedString("doc"))
r = STEPCAFControl_Reader()
r.SetNameMode(True)
assert r.ReadFile(src) == IFSelect_RetDone
r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())


def name(lab):
    a = TDataStd_Name()
    if lab.FindAttribute(TDataStd_Name.GetID_s(), a):
        return a.Get().ToExtString()
    return "?"


rows = []


def walk(lab, loc, path):
    if st.IsReference_s(lab):
        ref = TDF_Label()
        st.GetReferredShape_s(lab, ref)
        loc = loc * st.GetLocation_s(lab)
        walk(ref, loc, path)
        return
    nm = name(lab)
    if st.IsAssembly_s(lab):
        comps = TDF_LabelSequence()
        st.GetComponents_s(lab, comps)
        for i in range(1, comps.Length() + 1):
            c = comps.Value(i)
            walk(c, loc, path + [nm])
        return
    shp = st.GetShape_s(lab).Moved(loc)
    ex = TopExp_Explorer(shp, TopAbs_SOLID)
    k = 0
    if not ex.More():
        print("NO SOLID:", nm, "/".join(path), shp.ShapeType(), shp.IsNull())
        from OCP.TopAbs import TopAbs_SHELL
        from OCP.TopoDS import TopoDS
        from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
        from OCP.ShapeFix import ShapeFix_Solid
        if shp.ShapeType() == TopAbs_SHELL:
            sew = BRepBuilderAPI_Sewing(1e-3)
            sew.Add(shp)
            sew.Perform()
            sh = sew.SewedShape()
            print("  sewed:", sh.ShapeType(), "free edges", sew.NbFreeEdges())
            try:
                ms = BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(sh) if sh.ShapeType() == TopAbs_SHELL else TopoDS.Shell_s(shp))
                sf = ShapeFix_Solid(ms.Solid())
                sf.Perform()
                shp = sf.Solid()
                ex = TopExp_Explorer(shp, TopAbs_SOLID)
                print("  made solid", ex.More())
            except Exception as e:
                print("  makesolid failed", e)
    while ex.More():
        s = ex.Current()
        ex.Next()
        bb = Bnd_Box()
        BRepBndLib.Add_s(s, bb, True)
        x0, y0, z0, x1, y1, z1 = bb.Get()
        g = GProp_GProps()
        BRepGProp.VolumeProperties_s(s, g)
        c = g.CentreOfMass()
        idx = len(rows)
        fn = "%03d_%s" % (idx, re.sub(r"[^A-Za-z0-9]+", "_", nm)[:40])
        BRepTools.Write_s(s, os.path.join(out, "brep", fn + ".brep"))
        rows.append(dict(i=idx, name=nm, path="/".join(path), sub=k, file=fn,
                         bbox=[round(v, 4) for v in (x0, y0, z0, x1, y1, z1)], vol=round(g.Mass(), 5),
                         com=[round(c.X(), 4), round(c.Y(), 4), round(c.Z(), 4)]))
        k += 1


roots = TDF_LabelSequence()
st.GetFreeShapes(roots)
for i in range(1, roots.Length() + 1):
    walk(roots.Value(i), TopLoc_Location(), [])
json.dump(rows, open(os.path.join(out, "solids.json"), "w"), indent=0)
print(len(rows), "solids")
