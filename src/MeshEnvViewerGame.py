# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 19:46:09 2018

@author: Rasmus
"""

from tkinter import *
from MeshEnvViewer import *
from environments.triMesherEnv import *
from environments.triMesherEnvCpp import *
from environments.meshWorld import *
from environments.PartialViewEnv import *

print("Select Environment: \np: Partial View Environment")
print("t: Triangle Objects Environment\nq: Quad Objects Environment")
print("c: C++ Triangle Objects Environment (Not fully implemented)")
userInput = input('Enter choice:')
if userInput == "t":
    pass
    env = triMesherEnv(size=17, seedValue=4, nLinesX = 4, nLinesY=4)
elif userInput == "p":
    env = PartialViewEnv(triMesherEnv(size=26, seedValue=2, nLinesX = 5, nLinesY=5),15)
elif userInput == "c":
    env = triMesherEnvCpp(size=17, seedValue=4, nLinesX = 4, nLinesY=4)
else:
    print("Using Quads")
    env = meshEnv(size=25, seedValue=2)
master = Tk()
pixelSize = 15 # X and Y Size of each pixel; used for painting canvas
viewer = meshEnvViewer(master,env,pixelSize)

mainloop()
