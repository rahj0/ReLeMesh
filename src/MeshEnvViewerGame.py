# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 19:46:09 2018

@author: Rasmus
"""

from tkinter import *
from MeshEnvViewer import *
sys.path.append('environments')
from meshWorld import *
from triMesherEnv import *

tri = input('TriMesh (y/n):')
if tri == "y":
    pass
    env = triMesherEnv(partial=False,size=25, seedValue=2)
else:
    print("Using Quads")
    env = meshEnv(partial=False,size=25, seedValue=2)
master = Tk()
viewer = meshEnvViewer(master,env,20)

mainloop()
