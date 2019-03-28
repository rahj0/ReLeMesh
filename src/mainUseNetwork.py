# Script for loading model and use it in an environemnt.
# Use for evaluating model performance in a single run.

import tensorflow as tf
import os
import time
from environments.triMesherEnv import triMesherEnv
from Networks.BasicQNetwork import *
from environments.PartialViewEnv import PartialViewEnv
from worldGenerators.ObjectInTheMiddleWorldGenerator import *
from worldGenerators.simpleMeshWorldGenerator import *

sizeEnv = 15; xLines = 4; yLines = 4
nChannels = 2
fullEnv = triMesherEnv(size=25, seedValue=2, nLinesX = xLines, nLinesY=yLines)
fullEnv.setWorldGenerator(simpleMeshWorldGenerator(xLines,yLines,0,0))
env = PartialViewEnv(fullEnv,sizeEnv)
    
load_model = True #Whether to load a saved model.
path = "./dqn" #The path to save our model to.
h_size = 512 #The size of the final convolutional layer before splitting it into Advantage and Value streams.
num_episodes = 1
nEpisodesMax = 110 # Maximum number of 

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
    for i in range(num_episodes):

        s = env.reset()
        s = processState(s, sizeEnv, env.getNumberOfChannels())
        d = False
        rAll = 0
        j = 0
        #The Q-Network
        while j < nEpisodesMax: #If the agent takes longer than 200 moves to reach either of the blocks, end the trial.
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