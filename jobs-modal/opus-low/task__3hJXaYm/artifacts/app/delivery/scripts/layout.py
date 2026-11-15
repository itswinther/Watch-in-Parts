import numpy as np
C=np.array([2.8,0.]); O=np.zeros(2)
def inter(p1,r1,p2,r2,s):
    d=np.linalg.norm(p2-p1); a=(r1**2-r2**2+d**2)/(2*d); h2=r1**2-a**2
    if h2<0: return None
    h=np.sqrt(h2); u=(p2-p1)/d; v=np.array([-u[1],u[0]])
    return p1+a*u+s*h*v
def pol(c,r,a): return c+r*np.array([np.cos(a),np.sin(a)])
I8=inter(O,10.5,C,8.4,1); I6=inter(O,10.8,C,8.4,1)
L=['A1','A2','A3','A4','L1','L2']
def build(pT,pM,sS,sD,dS=5.1,dD=3.675,dM=5.4):
    T=pol(C,5.4,pT); M=pol(C,dM,pM)
    S=inter(T,dS,C,6.4,sS) if sS is not None else None
    D=inter(M,dD,C,8.9,sD)
    return T,M,S,D
def check(T,M,S,D,verbose=False):
    if S is None or D is None: return -9
    ar=0.35
    mob={ 'B':(O,{'A1':.5,'A2':.5,'A3':.99,'A4':.99}),
      'C':(C,{'A1':1.6,'A2':.45,'A3':.45,'A4':.6,'L1':4.95}),
      'H':(C,{'L2':4.6}),
      'M':(M,{'A1':4.6,'A2':ar,'A3':.45,'A4':ar,'L1':ar,'L2':1.4}),
      'T':(T,{'A1':ar,'A2':4.65,'A3':ar,'A4':ar,'L1':.75}),
      'S':(S,{'A1':ar,'A2':.75,'A3':ar,'A4':ar,'L1':ar,'L2':ar}),
      'D':(D,{'A1':ar,'A2':ar,'A3':3.3,'A4':ar,'L1':ar,'L2':ar}),
      'I8':(I8,{k:.45 for k in L[:4]}|{'L1':3.75}),
      'I6':(I6,{k:.45 for k in L[:4]}|{'L1':3.75})}
    mesh={('C','T','L1'),('C','M','A1'),('M','H','L2'),('T','S','A2'),('M','D','A3'),('I8','C','L1'),('I6','C','L1')}
    worst=9; names=list(mob)
    for i in range(len(names)):
        a=names[i]; pa,ra=mob[a]
        for l,r in ra.items():
            e=12.6-(np.linalg.norm(pa-C)+r)
            if a!='B': worst=min(worst,e)
            if verbose and e<0.05: print('case',a,l,e)
        for j in range(i+1,len(names)):
            b=names[j]; pb,rb=mob[b]
            if {a,b}=={'I8','I6'} : continue
            if {a,b}=={'C','H'}: continue
            for l in L:
                if l in ra and l in rb and (a,b,l) not in mesh and (b,a,l) not in mesh:
                    e=np.linalg.norm(pa-pb)-ra[l]-rb[l]
                    worst=min(worst,e)
                    if verbose and e<0.1: print(a,b,l,round(e,3))
    # hands: S hand 5.3, |S-C| in [5.65,7.3]; D 8.7..9.3 ; D-S >= 3.3+0.35
    dsc=np.linalg.norm(S-C); worst=min(worst,dsc-5.65,7.3-dsc,np.linalg.norm(D-S)-3.7)
    return worst
best=(-9,)
for pT in np.radians(np.arange(-180,180,3)):
  for pM in np.radians(np.arange(-180,180,3)):
    for sS in (1,-1):
      for sD in (1,-1):
        T,M,S,D=build(pT,pM,sS,sD)
        w=check(T,M,S,D)
        if w>best[0]: best=(w,pT,pM,sS,sD)
print(best, np.degrees(best[1:3]))
T,M,S,D=build(*best[1:]); print(T,M,S,D); check(T,M,S,D,True)
