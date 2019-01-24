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
env.reset()
actions = [5, 5, 8, 5, 5, 8, 4, 4, 8, 5, 5, 8, 8, 8, 8, 8, 5, 5, 8, 5, 5, 8, 4, 4, 8, 5, 5, 8, 8, 8, 8, 8, 5, 5, 8, 5, 5, 8, 4, 4, 8, 5, 5, 8, 8, 8, 8, 8, 8, 1,5, 5, 8, 1, 1, 1, 1, 1, 1, 1, 5, 1, 1, 5, 8, 1, 5, 1, 1, 1, 1, 2, 8, 5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 8, 8, 8, 8]

for action in actions:
    viewer.doAction(action)

env.printStats()

mainloop()