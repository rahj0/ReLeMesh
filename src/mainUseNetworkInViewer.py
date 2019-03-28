# -*- coding: utf-8 -*-
"""
Created on Tue May  8 22:33:20 2018

@author: Rasmus
"""
import tensorflow as tf
import os
from tkinter import *
from MeshEnvViewer import *
from environments.triMesherEnv import triMesherEnv
from environments.PartialViewEnv import PartialViewEnv
from Networks.BasicQNetwork import *
from worldGenerators.ObjectInTheMiddleWorldGenerator import *
from worldGenerators.simpleMeshWorldGenerator import *

sizeEnv = 15; xLines = 4; yLines = 4
nChannels = 2
fullEnv = triMesherEnv(size=25, seedValue=2, nLinesX = xLines, nLinesY=yLines)
# fullEnv.setWorldGenerator(ObjectInTheMiddleWorldGenerator(xLines,yLines,0,0))
fullEnv.setWorldGenerator(simpleMeshWorldGenerator(xLines,yLines,0,0))
env = PartialViewEnv(fullEnv,sizeEnv)

load_on_init = True #Load saved model on start
saveModelPath = "./dqn" #The path to save our model to.
h_size = 512 #The size of the final convolutional
showFinalState = True # Show the final state after in new window after running
tf.reset_default_graph()
mainQN = Qnetwork(h_size,env.getActionCount(),sizeEnv,env.getNumberOfChannels())

init = tf.global_variables_initializer()
saver = tf.train.Saver()

#Make a path for saving if not already there
if not os.path.exists(saveModelPath):
    os.makedirs(saveModelPath)

envRenderTime = 0.0
networkTime = 0.0
actions_ = []
with tf.Session() as sess:
    sess.run(init)
    if load_on_init == True:
        model = tf.train.get_checkpoint_state(saveModelPath)
        saver.restore(sess,model.model_checkpoint_path)
    master = Tk()
    viewer = meshEnvViewer(master,env,20,sess, mainQN)

    mainloop()

if showFinalState:
    master = Tk()
    viewer = meshEnvViewer(master,fullEnv,20,sess,False)
    mainloop()


