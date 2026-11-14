import sys; sys.path.insert(0,'tools'); sys.path.insert(0,'scripts')
import kernel as K, numpy as np, gear
H=K.load_part('work/parts/h_wheel.stl',200000,1<<25,.005)
b=H.bounding_box(); print(b)
g=gear.gear(48,9.247085729384876,5.79555495773441,b[2],b[5])
print('vol mine',g.volume(),'h_wheel',H.volume(), 'xor', (g-H).volume(), (H-g).volume())
for ph in np.linspace(0,2*np.pi/48,9):
    g=gear.gear(48,9.247085729384876,5.79555495773441,b[2],b[5],phase=ph)
    print(round(ph*180/np.pi,3),(g-H).volume())
