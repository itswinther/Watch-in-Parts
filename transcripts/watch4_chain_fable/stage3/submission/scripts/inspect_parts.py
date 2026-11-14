from common import *
mv = json.load(open(os.path.join(ROOT, 'previous/movement.json')))
names = mv['fixed'] + [p for m in mv['mobiles'].values() for p in m['parts']]
for n in names:
    m = load(n, 'previous')
    b = m.bounding_box()
    print(n, np.round(b, 3), round(m.volume(), 3), m.num_tri())
