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

from environments.triMesherEnv import triMesherEnv
from Networks.BasicQNetwork import *

sizeEnv = 16
# sizeEnv = 14, xLines = 2, xLines = 2 -> maxHumanScore ~ 3200
nChannels = 2
env = triMesherEnv((sizeEnv-2), 0, 3, 3)
print(env.actions)
    
load_model = True #Whether to load a saved model.
path = "./dqn" #The path to save our model to.
h_size = 1024 #The size of the final convolutional layer before splitting it into Advantage and Value streams.
num_episodes = 1
max_epLength = 100

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
    for i in range(num_episodes):

        s = env.reset()
        s = processState(s, sizeEnv, env.getNumberOfChannels())
        d = False
        rAll = 0
        j = 0
        #The Q-Network
        while j < max_epLength: #If the agent takes longer than 200 moves to reach either of the blocks, end the trial.
            j+=1
            #Choose an action by greedily (with e chance of random action) from the Q-network
            start = time.time()
            a = sess.run(mainQN.predict,feed_dict={mainQN.scalarInput:[s]})[0]
            networkTime += time.time() - start
            actions_.append(a)
            start = time.time()
            s,r,d = env.step(a)
            s = processState(s, sizeEnv, env.getNumberOfChannels())
            envRenderTime += time.time() - start
            if d == True:
                break
env.printStats()
print("Total steps: ", total_steps)
print("Env time: ", envRenderTime)
print("Network time: ", networkTime)
print(actions_)