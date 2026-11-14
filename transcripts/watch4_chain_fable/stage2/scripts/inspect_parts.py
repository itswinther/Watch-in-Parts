import sys,json
sys.path.insert(0,'tools')
import cadquery as cq
m=json.load(open('previous/movement.json'))
import glob,os
for f in sorted(glob.glob('previous/parts/*.step')):
    s=cq.importers.importStep(f).val()
    b=s.BoundingBox()
    print(os.path.basename(f),'x %.3f %.3f y %.3f %.3f z %.3f %.3f'%(b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax),'vol %.3f'%s.Volume())
