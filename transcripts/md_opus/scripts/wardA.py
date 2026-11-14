from common import *
from plan2d import plan2d
import pickle, time
B = R_of([(0,1,0),(0,0,1),(1,0,0)])
free = [((-400,-150),(0,400)), ((0,0),(20,205)), ((20,0),(170,258))]
piece = [((0,0),(232,45))]
thetas = np.arange(0, 91, 1.0)
t0=time.time()
res = plan2d(free, piece, thetas, (-300, 175, -100, 265), 1.5, (-252, 49.5, 0), (126, 4.5, 90), dil=2)
print(time.time()-t0, len(res) if res else None)
pickle.dump(res, open("wardA_res.pk", "wb"))
