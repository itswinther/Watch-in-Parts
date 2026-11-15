import numpy as np, sys
sys.path.insert(0,'/app/work')
from lay import circ, pol
CC=np.array([2.84,0.0])          # case centre, world
B=np.array([-2.84,0.0])          # barrel axis rel C
x=[26.268, -23.119, 19.082, 101.696, 138.914, 196.593, 200.454, 265.464, 228.987, 334.364]
phA,phA2,thm,ax2,psx,psy,pss,thh,pst,psq=x
R={}
R['A']=B+pol(10.8,phA); R['A2']=B+pol(12.0,phA2)
R['DM']=pol(2.7,thm)
cand=[circ(R['A'],5.0,R['DM'],2.7,s) for s in (1,-1)]
g=R['DM']+pol(2.7,ax2); R['X2']=min(cand,key=lambda c:np.linalg.norm(c-g))
R['X']=R['A']+pol(5.0,psx); R['Y']=R['X']+pol(4.275,psy); R['S']=R['Y']+pol(4.5,pss)
R['DH']=pol(3.6,thh); R['T']=R['DH']+pol(5.4,pst)
cand=[circ(R['A2'],4.5,R['DH'],4.5,s) for s in (1,-1)]
g=R['DH']+pol(4.5,psq); R['Q']=min(cand,key=lambda c:np.linalg.norm(c-g))
R['M']=np.zeros(2); R['H']=np.zeros(2)
POS={k:v+CC for k,v in R.items()}   # world
Z={'g1':0.74,'g2':2.27,'g3':2.08,'g4':1.54,'g5':1.44,'g6':0.78,'g7':2.12,'g8':1.52}
TH={'g1':0.72,'g2':0.28,'g3':0.27,'g4':0.30,'g5':0.25,'g6':0.25,'g7':0.43,'g8':0.55}
if __name__=="__main__":
    for k,v in POS.items(): print(k,np.round(v,4))
    print(np.linalg.norm(R['X2']-R['A']),np.linalg.norm(R['Q']-R['A2']),np.linalg.norm(R['T']))
