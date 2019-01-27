# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 19:46:09 2018

@author: Rasmus
"""

from tkinter import *
from MeshEnvViewer import *
from environments.meshWorld import *
from environments.triMesherEnv import *
from environments.AbstractPartialViewEnv import * 

# tri = input('TriMesh (y/n):')
pixelSize = 15
tri = "p"
if tri == "y":
    pass
    env = triMesherEnv(size=15, seedValue=2, nLinesX = 4, nLinesY=4)
elif tri == "p":
    env = AbstractPartialViewEnv(triMesherEnv(size=31, seedValue=2, nLinesX = 8, nLinesY=8),15)
else:
    print("Using Quads")
    env = meshEnv(size=25, seedValue=2)
master = Tk()
viewer = meshEnvViewer(master,env,pixelSize)

mainloop()
