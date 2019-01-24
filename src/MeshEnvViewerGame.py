# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 19:46:09 2018

@author: Rasmus
"""

from tkinter import *
from MeshEnvViewer import *
from environments.meshWorld import *
from environments.triMesherEnv import *

# tri = input('TriMesh (y/n):')
tri = "y"
if tri == "y":
    pass
    env = triMesherEnv(size=15, seedValue=2, nLinesX = 4, nLinesY=4)
else:
    print("Using Quads")
    env = meshEnv(size=25, seedValue=2)
master = Tk()
viewer = meshEnvViewer(master,env,20)

mainloop()
