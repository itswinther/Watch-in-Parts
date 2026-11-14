import math,sys,json,shutil
sys.path.insert(0,'scripts'); sys.path.insert(0,'tools')
import gears, kernel
# w1 on train1 (11.2,0), g_in on minute (11.2,8.4); distance 8.4 along +y
m=0.4
w=gears.gear(21,m,1.2,2.0,math.pi/2).translate((11.2,0,0))
# g_in: gap toward -y => tooth at -y + half pitch
g=gears.gear(21,m,1.2,2.0,-math.pi/2+math.pi/21).translate((11.2,8.4,0))
kernel.write_step('work/parts/w1.step',w); kernel.write_step('work/parts/g_in.step',g)
