import numpy as np, sys
from scipy.optimize import minimize
C=np.array([2.8,0.]); O=np.zeros(2)
def inter(p1,r1,p2,r2,s):
    d=np.linalg.norm(p2-p1); a=(r1**2-r2**2+d**2)/(2*d); h2=r1**2-a**2
    if h2<0 or d==0: return None
    h=np.sqrt(h2); u=(p2-p1)/d; v=np.array([-u[1],u[0]])
    return p1+a*u+s*h*v
def pol(c,r,a): return c+r*np.array([np.cos(a),np.sin(a)])
ar=0.35
WT=(45,6); MO={'1/4':(9,36,10,30,42,7),'1/3':(12,36,8,32,48,6),'1/6':(7,42,15,30,28,7),'1/4b':(9,36,10,30,36,6)}
def geo(x,Iside,mopt):
    pT,mx,my,sx,sy,dx,dy=x
    T=pol(C,5.4,pT); M=np.array([mx,my]); S=np.array([sx,sy]); D=np.array([dx,dy])
    return T,M,S,D
def evaluate(x,Iside,mopt,verbose=False):
    T,M,S,D=geo(x,Iside,mopt)
    cpn,Mwn,Mpn,Hn,Dn,Mp2n=MO[mopt]
    I8=inter(O,10.5,C,8.4,Iside); I6=inter(O,10.8,C,8.4,Iside)
    dM=np.linalg.norm(M-C); dS=np.linalg.norm(S-T); dD=np.linalg.norm(D-M)
    m1=2*dM/(cpn+Mwn); m2=2*dM/(Mpn+Hn); ms=2*dS/sum(WT); m3=2*dD/(Dn+Mp2n)
    info=[]
    for m,nm in ((m1,'m1'),(m2,'m2'),(ms,'ms'),(m3,'m3')): info.append(((m-0.15)*10,nm))
    mob={'B':(O,{'A':.99,'U':.5}),
      'C':(C,{'A':.45,'U':.45,'L1':4.95,'L2':m1*cpn/2+m1}),
      'H':(C,{'L3':m2*Hn/2+m2}),
      'M':(M,{'U':.35,'L1':m3*Mp2n/2+m3,'L2':m1*Mwn/2+m1,'L3':m2*Mpn/2+m2}),
      'T':(T,{'A':ms*WT[0]/2+ms,'U':.35,'L1':.75}),
      'S':(S,{'A':ms*WT[1]/2+ms,'U':.35,'L1':ar,'L2':ar,'L3':ar}),
      'D':(D,{'U':.35,'L1':m3*Dn/2+m3,'L2':ar,'L3':ar}),
      'I8':(I8,{'A':.45,'U':.45,'L1':3.75}),
      'I6':(I6,{'A':.45,'U':.45,'L1':3.75})}
    mesh={('I8','C','L1'),('I6','C','L1'),('C','T','L1'),('T','S','A'),('C','M','L2'),('M','H','L3'),('M','D','L1')}
    names=list(mob)
    for i in range(len(names)):
        a=names[i]; pa,ra=mob[a]
        if a!='B':
            for l,r in ra.items(): info.append((12.55-(np.linalg.norm(pa-C)+r),'case',a,l))
        for j in range(i+1,len(names)):
            b=names[j]; pb,rb=mob[b]
            if {a,b}=={'I8','I6'} or {a,b}=={'C','H'}: continue
            dd=np.linalg.norm(pa-pb)
            for l in ra:
                if l in rb and (a,b,l) not in mesh and (b,a,l) not in mesh:
                    info.append((dd-ra[l]-rb[l],a,b,l))
    dsc=np.linalg.norm(S-C); ddc=np.linalg.norm(D-C)
    info += [(np.linalg.norm(D-S)-3.75,'DS'),(dsc-5.65,'Sc1'),(7.25-dsc,'Sc2'),(ddc-8.7,'Dc1'),(9.25-ddc,'Dc2')]
    info.sort(key=lambda t:t[0])
    if verbose:
        for t in info[:14]: print(t)
        print(dict(T=T,M=M,S=S,D=D,m1=m1,m2=m2,ms=ms,m3=m3))
    return info[0][0], info
def obj(x,Iside,mopt):
    w,info=evaluate(x,Iside,mopt)
    return -sum(min(t[0],0.3) for t in info[:6])
if __name__=='__main__':
    rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 0)
    best=(-9,)
    for Iside in (1,-1):
     for mopt in MO:
      for k in range(60):
        x0=np.array([rng.uniform(-np.pi,np.pi)]+list(rng.uniform(-10,14,6)))
        r=minimize(obj,x0,args=(Iside,mopt),method='Nelder-Mead',options=dict(maxiter=3000,xatol=1e-4,fatol=1e-6))
        w,_=evaluate(r.x,Iside,mopt)
        if w>best[0]: best=(w,Iside,mopt,r.x); print(round(w,3),Iside,mopt,list(np.round(r.x,4)),flush=True)
    evaluate(best[3],best[1],best[2],True)
