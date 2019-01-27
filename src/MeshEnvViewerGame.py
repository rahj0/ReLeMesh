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
    env = triMesherEnv(size=26, seedValue=2, nLinesX = 5, nLinesY=5)
elif tri == "p":
    env = AbstractPartialViewEnv(triMesherEnv(size=29, seedValue=2, nLinesX = 7, nLinesY=7),15)
else:
    print("Using Quads")
    env = meshEnv(size=25, seedValue=2)
master = Tk()
viewer = meshEnvViewer(master,env,pixelSize)

mainloop()
