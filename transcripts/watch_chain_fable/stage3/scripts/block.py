import sys,json,os,numpy as np,pickle
sys.path.insert(0,'tools'); import kernel
doc=json.load(open('work/movement.json'))
mob={}; names=[]
for n in doc['fixed']: mob[n]='fixed:'+n; names.append(n)
for k,m in doc['mobiles'].items():
    for n in m['parts']: mob[n]=k; names.append(n)
mob['barrel']='barrel'; names.append('barrel')
P={n:kernel.load_part('meshes/barrel.stl' if n=='barrel' else 'work/parts/%s.stl'%n,200000,1<<25,0.005) for n in names}
if __name__=='__main__':
    # assembled overlaps
    for i,a in enumerate(names):
        for b in names[i+1:]:
            v=kernel.ivol(P[a],P[b])
            if v>1e-6: print('assembled overlap',a,b,round(v,5), 'same mobile' if mob[a]==mob[b] else '')
    dirs={'+z':(0,0,1),'-z':(0,0,-1)}
    blk={}
    for a in names:
        A=P[a].bounding_box()
        for dn,d in dirs.items():
            s=set()
            for b in names:
                if b==a or mob[a]==mob[b]: continue
                B=P[b].bounding_box()
                if not (A[0]<B[3] and B[0]<A[3] and A[1]<B[4] and B[1]<A[4]): continue
                # travel until clear in z
                T=(B[5]-A[2]) if d[2]>0 else (A[5]-B[2])
                if T<=0: continue
                mx=0
                for t in np.arange(0,T+0.1,0.1):
                    v=kernel.ivol(P[a].translate([0,0,d[2]*t]),P[b])
                    mx=max(mx,v)
                    if v>0.01: break
                if mx>0.002: print(a,dn,b,round(mx,4))
                if mx>0.01: s.add(b)
            blk[(a,dn)]=s
    pickle.dump(blk,open('scripts/blk.pkl','wb'))
    for k,v in blk.items(): print(k,sorted(v))
