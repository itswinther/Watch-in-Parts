import sys, math; sys.argv=['x','none']
exec(open('scripts/check.py').read().split('# speeds')[0])
a,b='third','centre'; A0=ld('a_wheel'); B0=ld('m_pinion')
for i in range(0,40):
    da=i*360/(8*35); A=rot(A0,axis[a],da); B=rot(B0,axis[b],-da)
    print(i, round(kernel.ivol(A,B),4), round(kernel.min_distance(A,B,0.5),4))
