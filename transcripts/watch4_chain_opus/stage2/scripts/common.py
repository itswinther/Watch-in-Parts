import sys, os, json, pickle
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT,'tools'))
import kernel, numpy as np
sys.path.insert(0, os.path.join(ROOT,'tools')); import submit
def load(name):
    return submit.load(os.path.join(ROOT,'work','parts',name+'.step'))
def barrel():
    return kernel.tris_to_manifold(kernel.read_stl(os.path.join(ROOT,'meshes','barrel.stl'),200000,33554432))
def mv(): return json.load(open(os.path.join(ROOT,'work','movement.json')))
