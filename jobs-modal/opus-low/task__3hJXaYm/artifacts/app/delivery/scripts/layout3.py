import numpy as np, sys
C=np.array([2.8,0.]); O=np.zeros(2)
def inter(p1,r1,p2,r2,s):
    d=np.linalg.norm(p2-p1); a=(r1**2-r2**2+d**2)/(2*d); h2=r1**2-a**2
    if h2<0 or d==0: return None
    h=np.sqrt(h2); u=(p2-p1)/d; v=np.array([-u[1],u[0]])
    return p1+a*u+s*h*v
def pol(c,r,a): return c+r*np.array([np.cos(a),np.sin(a)])
ar=0.35
Topts={'45/6':(3.525,0.6,3.825),'60/8':(4.65,0.75,5.1)}
Mopts={ # vM: (cp n, Mw n, Mp n, H n, D tip, Mp2 tip, dD)
 '1/4':(9,36,10,30,3.3,.675,3.675),
 '1/3':(12,36,8,32,3.75,.6,4.05),
 '1/6':(7,42,15,30,2.25,.675,2.625)}
def evaluate(Iside,topt,mopt,dM,pT,pM,rS,sS,rD,sD,verbose=False):
    wtt,pst,dS=Topts[topt]; cpn,Mwn,Mpn,Hn,Dt,Mp2t,dD=Mopts[mopt]
    I8=inter(O,10.5,C,8.4,Iside); I6=inter(O,10.8,C,8.4,Iside)
    m1=2*dM/(cpn+Mwn); m2=2*dM/(Mpn+Hn)
    T=pol(C,5.4,pT); M=pol(C,dM,pM)
    S=inter(T,dS,C,rS,sS); D=inter(M,dD,C,rD,sD)
    if S is None or D is None: return -9,None
    mob={'B':(O,{'A':.99,'U':.5}),
      'C':(C,{'A':.45,'U':.45,'L1':4.95,'L2':m1*cpn/2+m1}),
      'H':(C,{'L3':m2*Hn/2+m2}),
      'M':(M,{'U':.35,'L1':Mp2t,'L2':m1*Mwn/2+m1,'L3':m2*Mpn/2+m2}),
      'T':(T,{'A':wtt,'U':.35,'L1':.75}),
      'S':(S,{'A':pst,'U':.35,'L1':ar,'L2':ar,'L3':ar}),
      'D':(D,{'U':.35,'L1':Dt,'L2':ar,'L3':ar}),
      'I8':(I8,{'A':.45,'U':.45,'L1':3.75}),
      'I6':(I6,{'A':.45,'U':.45,'L1':3.75})}
    mesh={('I8','C','L1'),('I6','C','L1'),('C','T','L1'),('T','S','A'),('C','M','L2'),('M','H','L3'),('M','D','L1')}
    worst=9; names=list(mob); info=[]
    for i in range(len(names)):
        a=names[i]; pa,ra=mob[a]
        if a!='B':
            for l,r in ra.items():
                e=12.55-(np.linalg.norm(pa-C)+r); worst=min(worst,e); info.append((e,'case',a,l))
        for j in range(i+1,len(names)):
            b=names[j]; pb,rb=mob[b]
            if {a,b}=={'I8','I6'} or {a,b}=={'C','H'}: continue
            dd=np.linalg.norm(pa-pb)
            for l in ra:
                if l in rb and (a,b,l) not in mesh and (b,a,l) not in mesh:
                    e=dd-ra[l]-rb[l]; worst=min(worst,e); info.append((e,a,b,l))
    e=np.linalg.norm(D-S)-3.75; worst=min(worst,e); info.append((e,'DShand'))
    if verbose:
        for x in sorted(info,key=lambda t:t[0])[:12]: print(x)
    return worst,(T,M,S,D,I8,I6,m1,m2)
if __name__=='__main__':
  res=[]
  for Iside in (1,-1):
   for topt in Topts:
    for mopt in Mopts:
     best=(-9,)
     for dM in (5.35,5.6,6.0,6.5):
      for pT in np.radians(np.arange(-180,180,5)):
       for pM in np.radians(np.arange(-180,180,5)):
        for rS in (5.7,6.3,7.0):
         for sS in (1,-1):
          for rD in (8.75,9.0,9.25):
           for sD in (1,-1):
            w,_=evaluate(Iside,topt,mopt,dM,pT,pM,rS,sS,rD,sD)
            if w>best[0]: best=(w,Iside,topt,mopt,dM,pT,pM,rS,sS,rD,sD)
     print(np.round(best[0],3),best[1:],flush=True)
