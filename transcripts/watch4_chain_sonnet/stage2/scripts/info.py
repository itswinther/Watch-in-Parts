import sys,glob,os
sys.path.insert(0,'tools')
import cadquery as cq
for f in sorted(glob.glob('work/parts/*.step')):
    s=cq.importers.importStep(f).val()
    b=s.BoundingBox()
    print(os.path.basename(f),"x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f vol %.2f"%(b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax,s.Volume()))
