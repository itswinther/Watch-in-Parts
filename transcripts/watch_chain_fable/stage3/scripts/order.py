import pickle
blk=pickle.load(open('scripts/blk.pkl','rb'))
names=sorted({a for a,_ in blk})
rem=set(names); dis=[]
while rem:
    ok=[(a,d) for a in sorted(rem) for d in ('+z','-z') if not (blk[(a,d)]&rem)]
    if not ok: print('STUCK',{a:{d:sorted(blk[(a,d)]&rem) for d in('+z','-z')} for a in rem}); break
    a,d=ok[0]; dis.append((a,d)); rem.discard(a)
print(dis[::-1])
