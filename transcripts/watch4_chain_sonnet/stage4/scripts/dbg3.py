exec(open('scripts/plan.py').read().split("ORDER=")[0])
for z in (7.5,8.0,9.0,9.8,10.0,10.2,10.3,10.45,10.6,10.75,10.9):
    sl=S['day_cock'].slice(z)
    print(z,[np.round(np.array(p),1).tolist() if len(p)<9 else (len(p),np.round(np.array(p).min(0),1).tolist(),np.round(np.array(p).max(0),1).tolist()) for p in sl.to_polygons()])
