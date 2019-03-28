# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 19:46:09 2018

@author: Rasmus
"""

from tkinter import *
from MeshEnvViewer import *
from environments.meshWorld import *
from environments.triMesherEnv import *
from environments.PartialViewEnv import * 

print("Select Environment: \np: Partial View Environment")
print("t: Triangle Objects Environment\nq: Quad Objects Environment")
userInput = input('Enter choice:')
pixelSize = 15
if userInput == "t":
    pass
    env = triMesherEnv(size=17, seedValue=4, nLinesX = 4, nLinesY=4)
elif userInput == "p":
    env = PartialViewEnv(triMesherEnv(size=26, seedValue=2, nLinesX = 5, nLinesY=5),15)
else:
    print("Using Quads")
    env = meshEnv(size=25, seedValue=2)
master = Tk()
viewer = meshEnvViewer(master,env,pixelSize)

mainloop()
