from tkinter import *
from MeshEnvViewer import *
from environments.meshWorld import *
from environments.triMesherEnv import *

tri = input('TriMesh (y/n):')
if tri == "y":
    pass
    env = triMesherEnv(size=13, seedValue=2, nLinesX = 2, nLinesY=2)
else:
    print("Using Quads")
    env = meshEnv(size=25, seedValue=2)
master = Tk()
viewer = meshEnvViewer(master,env,20)
env.reset()
actions = [2, 5, 5, 5, 8, 4, 4, 4, 4, 8, 8, 8, 2, 5, 5, 5, 8, 4, 4, 4, 4, 8, 8, 8]
actions = [4, 4, 4, 4, 8, 2, 5, 5, 5, 8, 8, 8, 4, 4, 4, 4, 8, 4, 4, 4, 4, 8, 8, 8]

for action in actions:
    viewer.doAction(action)

env.printStats()

mainloop()