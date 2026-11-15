import numpy as np, itertools, sys
C=np.array([2.8,0.]); O=np.zeros(2)
def inter(p1,r1,p2,r2,s):
    d=np.linalg.norm(p2-p1); a=(r1**2-r2**2+d**2)/(2*d); h2=r1**2-a**2
    if h2<0 or d==0: return None
    h=np.sqrt(h2); u=(p2-p1)/d; v=np.array([-u[1],u[0]])
    return p1+a*u+s*h*v
def pol(c,r,a): return c+r*np.array([np.cos(a),np.sin(a)])
ar=0.35
# options
Topts={'45/6':(3.525,0.6,3.825),'60/8':(4.65,0.75,5.1)}   # wt tip, ps tip, dist (m .15)
# motion: vM=1/4 -> D/Mp2=6 (42/7 m.15: Dtip 3.3, p tip .675, dist 3.675) ; vM=1/3 -> 8 (48/6: 3.75,.6,4.05)
def run(Iside,topt,dopt,layers):
    wtt,pst,dS=Topts[topt]
    I8=inter(O,10.5,C,8.4,Iside); I6=inter(O,10.8,C,8.4,Iside)
    best=(-9,)
    for dM in (5.3,5.6,6.0):
      cpt = dM/(5 if dopt=='q' else 4)+0.24   # cp tip
      Mwt = dM-cpt+0.48
      Dt,Mp2t,dD = (3.3,.675,3.675) if dopt=='q' else (3.75,.6,4.05)
      for pT in np.radians(np.arange(-180,180,4)):
        T=pol(C,5.4,pT)
        for pM in np.radians(np.arange(-180,180,4)):
          M=pol(C,dM,pM)
          for rS in (5.7,6.3,7.0):
           for sS in (1,-1):
            S=inter(T,dS,C,rS,sS)
            if S is None: continue
            for rD in (8.75,9.0,9.25):
             for sD in (1,-1):
              D=inter(M,dD,C,rD,sD)
              if D is None: continue
              lw,lt,ld=layers
              mob={'B':(O,{'A1':.5,'A2':.5,'A3':.99,'A4':.99}),
                'C':(C,{'A1':cpt,'A2':.45,'A3':.45,'A4':.6,'L1':4.95}),
                'H':(C,{'L2':4.6}),
                'M':(M,{'A1':ar,'A2':ar,'A3':ar,'A4':ar,'L1':ar,'L2':1.4}),
                'T':(T,{'A1':ar,'A2':ar,'A3':ar,'A4':ar,'L1':.75}),
                'S':(S,{'A1':ar,'A2':ar,'A3':ar,'A4':ar,'L1':ar,'L2':ar}),
                'D':(D,{'A1':ar,'A2':ar,'A3':ar,'A4':ar,'L1':ar,'L2':ar}),
                'I8':(I8,{k:.45 for k in ['A1','A2','A3','A4']}|{'L1':3.75}),
                'I6':(I6,{k:.45 for k in ['A1','A2','A3','A4']}|{'L1':3.75})}
              mob['M'][1]['A1']=Mwt; mob['M'][1][ld]=max(mob['M'][1][ld],Mp2t)
              mob['T'][1][lt]=wtt; mob['S'][1][lt]=pst; mob['D'][1][ld]=Dt
              mesh={('C','T','L1'),('C','M','A1'),('M','H','L2'),('T','S',lt),('M','D',ld),('I8','C','L1'),('I6','C','L1')}
              worst=9; names=list(mob)
              for i in range(len(names)):
                a=names[i]; pa,ra=mob[a]
                if a!='B':
                  for l,r in ra.items(): worst=min(worst,12.55-(np.linalg.norm(pa-C)+r))
                for j in range(i+1,len(names)):
                  b=names[j]; pb,rb=mob[b]
                  if {a,b}=={'I8','I6'} or {a,b}=={'C','H'}: continue
                  dd=np.linalg.norm(pa-pb)
                  for l in ra:
                    if l in rb and (a,b,l) not in mesh and (b,a,l) not in mesh:
                      worst=min(worst,dd-ra[l]-rb[l])
                if worst<best[0]: break
              worst=min(worst,np.linalg.norm(D-S)-3.75)
              if worst>best[0]: best=(worst,dM,np.degrees(pT),np.degrees(pM),rS,sS,rD,sD,T,M,S,D)
    return best
for Iside in (1,-1):
  for topt in Topts:
    for dopt in ('q','t'):
      for layers in (('A1','A2','A3'),('A1','A3','A2'),('A1','A2','A4'),('A1','A4','A2')):
        b=run(Iside,topt,dopt,layers); print(Iside,topt,dopt,layers,np.round(b[0],3),b[1:8],flush=True)
