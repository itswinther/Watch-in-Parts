"""Geometry primitives built twice: as manifold (fast checks) and as CadQuery (STEP)."""
import numpy as np, manifold3d as m3, cadquery as cq
from gear import gear_pts
SEG=128
class Shape:
    """list of (kind, params) primitives unioned, minus list of cuts; positioned in world coords"""
    def __init__(self): self.add=[]; self.cut=[]
    def cyl(self,x,y,r,z0,z1,cut=False):
        (self.cut if cut else self.add).append(('poly',self._circ(x,y,r),z0,z1,('circle',x,y,r))); return self
    def poly(self,pts,z0,z1,cut=False):
        (self.cut if cut else self.add).append(('poly',np.asarray(pts,float),z0,z1,None)); return self
    def gear(self,x,y,z,m,phase,z0,z1,delta=0.02):
        p=gear_pts(z,m,phase,delta)+np.array([x,y]); self.add.append(('poly',p,z0,z1,None)); return self
    @staticmethod
    def _circ(x,y,r,n=SEG):
        t=np.linspace(0,2*np.pi,n,endpoint=False); return np.c_[x+r*np.cos(t),y+r*np.sin(t)]
    def manifold(self):
        def mk(item):
            _,p,z0,z1,_c=item
            return m3.CrossSection([p.tolist()]).extrude(z1-z0).translate([0,0,z0])
        a=m3.Manifold.batch_boolean([mk(i) for i in self.add],m3.OpType.Add) if len(self.add)>1 else mk(self.add[0])
        if self.cut:
            c=m3.Manifold.batch_boolean([mk(i) for i in self.cut],m3.OpType.Add) if len(self.cut)>1 else mk(self.cut[0])
            a=a-c
        return a
    def cadquery(self):
        def mk(item):
            _,p,z0,z1,c=item
            wp=cq.Workplane('XY').workplane(offset=z0)
            if c is not None:
                _,x,y,r=c; s=wp.center(x,y).circle(r).extrude(z1-z0)
            else:
                s=wp.polyline([tuple(q) for q in p]).close().extrude(z1-z0)
            return s.val()
        solids=[mk(i) for i in self.add]
        res=solids[0]
        if len(solids)>1: res=res.fuse(*solids[1:]).clean()
        if self.cut:
            cuts=[mk(i) for i in self.cut]
            res=res.cut(*cuts).clean()
        return res
