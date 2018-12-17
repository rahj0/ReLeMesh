from tkinter import *
from MeshEnvViewer import *
from environments.meshWorld import *
from environments.triMesherEnv import *

tri = input('TriMesh (y/n):')
if tri == "y":
    pass
    env = triMesherEnv(size=12, seedValue=2, nLinesX = 2, nLinesY=2)
else:
    print("Using Quads")
    env = meshEnv(size=25, seedValue=2)
master = Tk()
viewer = meshEnvViewer(master,env,20)
env.reset()
actions = [1, 2, 4, 2, 1, 1, 2, 2, 2, 4, 4, 2, 4, 1, 1, 1, 4, 1, 2, 2, 0, 4, 1, 1, 1, 2, 2, 2, 2, 4, 2, 1, 4, 3, 0, 0, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1]
actions = [2, 1, 4, 2, 2, 2, 2, 1, 1, 4, 4, 2, 4, 1, 1, 1, 4, 2, 2, 4, 0, 2, 1, 1, 2, 2, 1, 1, 2, 4, 1, 2, 4, 0, 3, 0, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1]
actions = [1, 2, 4, 1, 1, 2, 2, 2, 0, 1, 2, 4, 4, 0, 2, 4, 1, 1, 1, 4, 2, 1, 0, 2, 4, 1, 1, 2, 2, 2, 1, 2, 4, 1, 0, 1, 4, 3, 0, 0, 3, 3, 1, 1, 1, 4]
actions = [2, 1, 4, 2, 2, 2, 2, 2, 1, 1, 3, 4, 4, 2, 4, 1, 1, 1, 4, 2, 2, 4, 2, 2, 2, 1, 2, 1, 0, 1, 1, 0, 1, 4, 2, 1, 4, 0, 0, 3, 3, 3, 1, 1, 1, 1, 1, 1,1, 1]

for action in actions:
    viewer.doAction(action)

env.printStats()

mainloop()