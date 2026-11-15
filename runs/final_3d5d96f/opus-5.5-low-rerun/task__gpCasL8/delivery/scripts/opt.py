from lay import *
import itertools,sys,json
B=np.array([-2.84,0.]);C=np.zeros(2)
G=[('pA','A',1.4,'drum'),('wA','A',4.17,'pX|pX2'),('pX','X',1.42,'wA'),('pX2','X2',1.42,'wA'),('x2m','X2',1.05,'dm1'),
('xs','X',3.525,'y1'),('dm1','DM',1.95,'x2m'),('dm2','DM',1.05,'gM'),('gM','M',1.95,'dm2'),('y1','Y',1.05,'xs'),('y2','Y',3.75,'pS'),('pS','S',1.05,'y2'),
('pA2','A2',2.6,'drum'),('aq','A2',1.275,'q1'),('q1','Q',3.75,'aq'),('q2','Q',1.75,'dh1'),('dh1','DH',3.25,'q2'),('dh','DH',2.1,'gH|gT'),('gH','H',2.1,'dh'),('gT','T',3.9,'dh')]
CEN={'M','H'}
def build2(p,signs):
    phA,phA2,thm,psx,psy,sr,thh=p
    sx2,st,sq=signs
    P={}
    P['A']=B+pol(10.8,phA);P['A2']=B+pol(12.0,phA2)
    P['DM']=pol(2.7,thm);P['X2']=circ(P['A'],5.0,P['DM'],2.7,sx2)
    P['X']=P['A']+pol(5.0,psx);P['Y']=P['X']+pol(4.275,psy)
    P['S']=circ(C,sr,P['Y'],4.5,st)
    P['DH']=pol(3.9,thh);P['T']=circ(C,8.35,P['DH'],5.85,sq)
    P['Q']=circ(P['A2'],4.5,P['DH'],4.5,-sq)
    P['M']=C;P['H']=C
    return P
def viol(P,verbose=False):
    bad=0;m=9;out=[]
    def add(tag,d,lim=0.05):
        nonlocal bad,m
        m=min(m,d)
        if d<lim:
            bad+=lim-d; out.append((tag,round(d,2)))
    if np.linalg.norm(P['A2'])>10.0: add('A2far',10-np.linalg.norm(P['A2']))
    for g,mo,r,mate in G:
        c=P[mo]
        add('case '+g,12.6-(np.linalg.norm(c)+r))
        for m2,c2 in P.items():
            if m2==mo or (mo in CEN and m2 in CEN): continue
            if g in('gM','gH') and m2 in CEN: continue
            ar=(0.3 if g=='dh1' else 0.6) if m2 in CEN else 0.35
            add('cover %s %s'%(g,m2),np.linalg.norm(c-c2)-r-ar)
        if mo not in CEN and g not in('pA','pA2'):
            add('post '+g,np.linalg.norm(c-B)-r-0.5)
    for mo,c in P.items():
        if mo in CEN: continue
        add('arbpost '+mo,np.linalg.norm(c-B)-0.4-1.0)
    add('drumpin',np.linalg.norm(P['A']-P['A2'])-1.4-2.6,0.1)
    if verbose: print(out)
    return bad,m
def f(p,signs):
    try: P=build2(p,signs)
    except Exception: return 100
    b,m=viol(P)
    return b*10-min(m,0.3)
if __name__=="__main__" and sys.argv[1]=='opt':
    from scipy.optimize import differential_evolution
    for signs in itertools.product([-1,1],repeat=3):
        r=differential_evolution(f,[(0,90),(-40,0),(0,360),(0,360),(0,360),(5.5,7.5),(0,360)],args=(signs,),seed=1,maxiter=300,popsize=30,tol=1e-8)
        print(signs,r.fun,np.round(r.x,2).tolist(),flush=True)
if __name__=="__main__" and sys.argv[1]=='show':
    P=build2(json.loads(sys.argv[2]),json.loads(sys.argv[3]))
    for k,v in P.items(): print(k,np.round(v,2),round(np.linalg.norm(v),2))
    viol(P,True)
