import numpy as np
C=np.array([2.8,0.]); O=np.zeros(2)
def inter(p1,r1,p2,r2,s):
    d=np.linalg.norm(p2-p1); a=(r1**2-r2**2+d**2)/(2*d); h2=r1**2-a**2
    if h2<0 or d==0: return None
    h=np.sqrt(h2); u=(p2-p1)/d; v=np.array([-u[1],u[0]])
    return p1+a*u+s*h*v
def pol(c,r,a): return c+r*np.array([np.cos(a),np.sin(a)])
ar=0.35
def evaluate(Iside,pT,pM,rS,sS,rD,sD,verbose=False):
    I8=inter(O,10.5,C,8.4,Iside); I6=inter(O,10.8,C,8.4,Iside)
    T=pol(C,5.4,pT); M=pol(C,3.0,pM)
    S=inter(T,5.1,C,rS,sS); D=inter(M,5.25,C,rD,sD)
    if S is None or D is None: return -9,None
    mob={'B':(O,{'A':.99,'P':1.0}),
      'C':(C,{'L1':4.95,'L2':.75}),
      'H':(C,{'L3':2.44}),
      'M':(M,{'L2':2.55,'L3':.95}),
      'T':(T,{'A':4.65,'L1':.75,'P':.45}),
      'S':(S,{'A':.75,'L1':ar,'L2':ar,'L3':ar,'P':.45}),
      'D':(D,{'L2':ar,'L3':4.69}),
      'I8':(I8,{'A':.45,'L1':3.75,'P':1.25}),
      'I6':(I6,{'A':.45,'L1':3.75,'P':1.45}),
      }
    mesh={('I8','C','L1'),('I6','C','L1'),('C','T','L1'),('T','S','A'),('C','M','L2'),('M','H','L3'),('M','D','L3')}
    names=list(mob); info=[]
    for i in range(len(names)):
        a=names[i]; pa,ra=mob[a]
        if a!='B':
            for l,r in ra.items(): info.append((12.5-(np.linalg.norm(pa-C)+r),'case',a,l))
        for j in range(i+1,len(names)):
            b=names[j]; pb,rb=mob[b]
            if {a,b}=={'I8','I6'} or {a,b}=={'C','H'}: continue
            dd=np.linalg.norm(pa-pb)
            for l in ra:
                if l in rb and (a,b,l) not in mesh and (b,a,l) not in mesh:
                    info.append((dd-ra[l]-rb[l],a,b,l))
    dsc=np.linalg.norm(S-C)
    info += [(np.linalg.norm(D-S)-8.8,'DS'),(dsc-5.7,'Sc1'),(7.2-dsc,'Sc2')]
    info.sort(key=lambda t:t[0])
    if verbose:
        for t in info[:12]: print(t)
        print(dict(T=T,M=M,S=S,D=D,I8=I8,I6=I6))
    return info[0][0],(T,M,S,D,I8,I6)
best=(-9,)
for Iside in (1,-1):
 for pT in np.radians(np.arange(-180,180,3)):
  for pM in np.radians(np.arange(-180,180,5)):
   for rS in np.arange(5.7,7.21,0.25):
    for sS in (1,-1):
     for rD in np.arange(7.2,7.86,0.1):
      for sD in (1,-1):
        w,_=evaluate(Iside,pT,pM,rS,sS,rD,sD)
        if w>best[0]: best=(w,Iside,pT,pM,rS,sS,rD,sD)
print(best)
evaluate(*best[1:],verbose=True)
