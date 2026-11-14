import pickle
res = pickle.load(open("deps.pkl","rb"))
names = sorted({n for n,_ in res})
remaining = set(names); dis = []
while remaining:
    for n in sorted(remaining):
        ok = [d for d in (1,-1) if not (set(res[(n,d)]) & remaining)]
        if ok:
            dis.append((n, ok[0])); remaining.remove(n); break
    else:
        print("stuck", remaining); break
order = dis[::-1]
print(order)
pickle.dump(order, open("order.pkl","wb"))
