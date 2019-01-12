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
from Networks.BasicQNetwork import *

sizeEnv = 16
# sizeEnv = 14, xLines = 2, xLines = 2 -> maxHumanScore ~ 3200
nChannels = 2
env = triMesherEnv((sizeEnv-2), 0, 3, 3)
print(env.actions)
    
load_model = True #Whether to load a saved model.
path = "./dqn" #The path to save our model to.
h_size = 512 #The size of the final convolutional layer before splitting it into Advantage and Value streams.
num_episodes = 1
max_epLength = 110

tf.reset_default_graph()
mainQN = Qnetwork(h_size,env.actions,sizeEnv,env.getNumberOfChannels())

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
