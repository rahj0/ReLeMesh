# -*- coding: utf-8 -*-
"""
Created on Tue May  8 22:33:20 2018

@author: Rasmus
"""

from __future__ import division

import numpy as np
import random
import tensorflow as tf
import tensorflow.contrib.slim as slim
import matplotlib.pyplot as plt
import scipy.misc
import os
import time
"matplotlib inline"

from tkinter import *
from MeshEnvViewer import *
from environments.meshWorld import *
from environments.triMesherEnv import triMesherEnv
from environments.AbstractPartialViewEnv import AbstractPartialViewEnv
from Networks.BasicQNetwork import *
from worldGenerators.ObjectInTheMiddleWorldGenerator import *

sizeEnv = 15; xLines = 5; yLines = 5
nChannels = 2
fullEnv = triMesherEnv(size=31, seedValue=2, nLinesX = xLines, nLinesY=yLines)
fullEnv.setWorldGenerator(ObjectInTheMiddleWorldGenerator(xLines,yLines,0,0))
env = AbstractPartialViewEnv(fullEnv,sizeEnv)

load_model = True #Whether to load a saved model.
path = "./dqn" #The path to save our model to.
h_size = 750 #The size of the final convolutional layer before splitting it into Advantage and Value streams.
num_episodes = 1
max_epLength = 110

tf.reset_default_graph()
mainQN = Qnetwork(h_size,env.getActionCount(),sizeEnv,env.getNumberOfChannels())

init = tf.global_variables_initializer()

saver = tf.train.Saver()

total_steps = 0

#Make a path for our model to be saved in.
if not os.path.exists(path):
    os.makedirs(path)

envRenderTime = 0.0
networkTime = 0.0
actions_ = []
with tf.Session() as sess:
    sess.run(init)
    if load_model == True:
        print('Loading Model...')
        ckpt = tf.train.get_checkpoint_state(path)
        saver.restore(sess,ckpt.model_checkpoint_path)
    master = Tk()
    viewer = meshEnvViewer(master,env,20,sess, mainQN)

    mainloop()

if 1:
    master = Tk()
    viewer = meshEnvViewer(master,fullEnv,20,sess,False)

    mainloop()


