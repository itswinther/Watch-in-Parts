from pathlib import Path
import numpy as np,trimesh
from PIL import Image,ImageDraw,ImageFont
colors={'stem':(115,130,148),'winding_pinion':(115,154,185),'sliding_clutch':(142,111,178),'winding_face_wheel':(201,164,75),'barrel':(222,183,81),'barrel_click':(177,102,113),'setting_face_wheel':(103,174,155),'bearing_bridge':(166,178,183),'minute_wheel':(137,183,145),'barrel_arbor':(130,143,158)}
W,H=1500,1420;im=Image.new('RGB',(W,H),(247,246,241));draw=ImageDraw.Draw(im)
u=np.array([1,0,0]);v=np.array([0,.838,.545]);dep=np.cross(u,v);scale=68
faces=[]
for n,col in colors.items():
 path=Path('/app/submission/parts')/(n+'.stl')
 if not path.exists():path=Path('/app/supplied')/(n+'.stl')
 m=trimesh.load(path);tris=m.triangles;norm=m.face_normals
 xy=np.stack([tris@u,tris@v],axis=-1);xy[:,:,0]=170+(xy[:,:,0]+1.4)*scale;xy[:,:,1]=600-xy[:,:,1]*scale
 dd=tris.mean(axis=1)@dep;light=np.maximum(0,norm@np.array([-.3,-.4,.866]));shade=.62+.38*light
 for k in range(len(tris)):
  rgb=tuple(int(x*shade[k]) for x in col);faces.append((tris[k]@dep,xy[k],rgb))
pix=np.asarray(im).copy();depth=np.full((H,W),-1e10)
for dd,xy,col in faces:
 lo=np.maximum(np.floor(xy.min(axis=0)).astype(int),0);hi=np.minimum(np.ceil(xy.max(axis=0)).astype(int),[W-1,H-1])
 if np.any(hi<lo):continue
 xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5)
 x0,y0=xy[0];x1,y1=xy[1];x2,y2=xy[2];den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
 if abs(den)<1e-9:continue
 a=((y1-y2)*(xx-x2)+(x2-x1)*(yy-y2))/den;b=((y2-y0)*(xx-x2)+(x0-x2)*(yy-y2))/den;c=1-a-b
 z=a*dd[0]+b*dd[1]+c*dd[2];sl=np.s_[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
 mask=(a>=-1e-7)&(b>=-1e-7)&(c>=-1e-7)&(z>depth[sl])
 depth[sl][mask]=z[mask];pix[sl][mask]=col
im=Image.fromarray(pix);draw=ImageDraw.Draw(im)
font=ImageFont.load_default(size=26);small=ImageFont.load_default(size=21)
draw.text((65,35),'KEYLESS WORKS  /  position 1',fill=(35,49,61),font=font)
draw.text((65,75),'Oblique view; plates omitted to expose the mechanism. Millimetres.',fill=(75,85,91),font=small)
for i,(name,c) in enumerate(colors.items()):
 x=65+(i%3)*470;y=1210+(i//3)*46
 draw.rounded_rectangle((x,y,x+28,y+23),radius=4,fill=c)
 draw.text((x+40,y-2),name.replace('_',' '),fill=(35,49,61),font=small)
im.save('/app/submission/assembly.png')
