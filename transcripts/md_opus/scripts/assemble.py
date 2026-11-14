from common import *
import pickle, glob
paths = {}
for f in sorted(glob.glob("*.pkl")):
    paths.update(pickle.load(open(f, "rb")))
order = [n for n in ["sofa", "bookcase", "wardrobe", "chest"] if n in paths]
save(order, paths)
print(order)
