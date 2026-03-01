# -*- coding: utf-8 -*-
import numpy as np
import os
from tkinter import *
from MeshEnvViewer import meshEnvViewer
from environments.triMesherEnv import triMesherEnv
from environments.PartialViewEnv import PartialViewEnv
from Networks.BasicQNetwork import Qnetwork, processState
from worldGenerators.simpleMeshWorldGenerator import simpleMeshWorldGenerator

sizeEnv = 15; xLines = 4; yLines = 4
nChannels = 2
fullEnv = triMesherEnv(size=25, seedValue=2, nLinesX=xLines, nLinesY=yLines)
fullEnv.setWorldGenerator(simpleMeshWorldGenerator(xLines, yLines, 0, 0))
env = PartialViewEnv(fullEnv, sizeEnv)

saveModelPath = "./dqn"
h_size = 512
showFinalState = True  # After running, open a second window showing the full 25x25 result

mainQN = Qnetwork(h_size, env.getActionCount(), sizeEnv, env.getNumberOfChannels())

# Build weights with a dummy forward pass, then load checkpoint.
dummy = np.zeros([1, sizeEnv * sizeEnv * nChannels], dtype=np.float32)
mainQN(dummy)

if not os.path.exists(saveModelPath + '/model-final.weights.h5'):
    print("No saved model found at:", saveModelPath)
    print("Train first with: python3 gameTrainingMain.py --episodes 5000")
    exit()

mainQN.load_weights(saveModelPath + '/model-final.weights.h5')
print("Model loaded from", saveModelPath)

master = Tk()
viewer = meshEnvViewer(master, env, 20, qNetwork=mainQN)
mainloop()

if showFinalState:
    master = Tk()
    viewer = meshEnvViewer(master, fullEnv, 20)
    mainloop()
