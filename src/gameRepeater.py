from tkinter import *
from MeshEnvViewer import *
from environments.meshWorld import *
from environments.triMesherEnv import *

# tri = input('TriMesh (y/n):')
tri = "y"
if tri == "y":
    pass
    env = triMesherEnv(size=14, seedValue=2, nLinesX = 3, nLinesY=3)
else:
    print("Using Quads")
    env = meshEnv(size=25, seedValue=2)
master = Tk()
viewer = meshEnvViewer(master,env,20)
env.reset()
actions = [5, 5, 2, 8, 5, 2, 5, 8, 4, 4, 4, 8, 8, 8, 8, 4, 5, 2, 8, 5, 2, 8, 4, 8, 8, 8, 4, 2, 5, 4, 4, 2, 8, 5, 5, 5, 5, 5, 5, 5, 8, 5, 5, 5, 5, 8, 4, 4, 5, 2,8, 2, 8, 5, 8, 5, 8]

for action in actions:
    viewer.doAction(action)

env.printStats()

mainloop()