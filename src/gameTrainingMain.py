# -*- coding: utf-8 -*-
"""
Created on Tue May  8 22:33:20 2018

@author: Rasmus
"""

from __future__ import division

import argparse
import numpy as np
import random
import tensorflow as tf
import os
import time

from environments.triMesherEnv import triMesherEnv
from worldGenerators.ObjectInTheMiddleWorldGenerator import *
from environments.PartialViewEnv import PartialViewEnv
from Networks.BasicQNetwork import *

num_episodes = 0  #How many episodes of game environment to train network with.

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--episodes', dest='nEpisodes', default=5000,
                    help='Number of episodes to run in training.')
    args = parser.parse_args()
    num_episodes = int(args.nEpisodes)

# For testing device location
with tf.Session(config=tf.ConfigProto(log_device_placement=True)) as sess:
    a = tf.constant([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[2, 3], name='a')
    sess.run(a)

sizeEnv = 15; xLines = 4; yLines = 4
nChannels = 2
fullEnv = triMesherEnv(size=25, seedValue=2, nLinesX = xLines, nLinesY=yLines)
# fullEnv.setWorldGenerator(ObjectInTheMiddleWorldGenerator(xLines,yLines,0,0))
fullEnv.setWorldGenerator(simpleMeshWorldGenerator(xLines,yLines,0,0))
env = PartialViewEnv(fullEnv,sizeEnv)

multi = 1
batch_size = 32*multi #How many experiences to use for each training step.
update_freq = 4*multi #How often to perform a training step.
y = .92 #Discount factor on the target Q-values
startE = 0.6 #Starting chance of random action
endE = 0.01 #Final chance of random action
max_epLength = 175 #The max allowed length of our episode.

multi2 = 5
annealing_steps = int(400000*multi2*0.3) #How many steps of training to reduce startE to endE.
num_episodes = int(5000*multi2) #How many episodes of game environment to train network with.

 #How many steps of training to reduce startE to endE.
print("Annealing steps: ", annealing_steps)

load_model = False #Whether to load a saved model.
path = "./dqn" #The path to save our model to.
h_size = 512 #The size of the final convolutional layer before splitting it into Advantage and Value streams.
tau = 0.001 #Rate to update target network toward primary   
bufferSize = 100000
pre_train_steps = bufferSize #How many steps of random actions before training begins.

tf.reset_default_graph()
mainQN = Qnetwork(h_size,env.getActionCount(),sizeEnv,env.getNumberOfChannels())
targetQN = Qnetwork(h_size,env.getActionCount(),sizeEnv,env.getNumberOfChannels())

init = tf.global_variables_initializer()

saver = tf.train.Saver()

trainables = tf.trainable_variables()

targetOps = updateTargetGraph(trainables,tau)

myBuffer = experience_buffer(buffer_size= bufferSize)

#Set the rate of random action decrease. 
e = startE
stepDrop = (startE - endE)/annealing_steps

#create lists to contain total rewards and steps per episode
jList = []
rList = []
total_steps = 0

#Make a path for our model to be saved in.
if not os.path.exists(path):
    os.makedirs(path)

last_avg = 0
maxScore = 0
last_max500 = 0
bestActions = []
envResetTime = 0.0
envRenderTime = 0.0
networkTime = 0.0
startComplete = time.time()
with tf.Session(config=tf.ConfigProto(log_device_placement=False)) as sess:
    sess.run(init)
    if load_model == True:
        print('Loading Model...')
        ckpt = tf.train.get_checkpoint_state(path)
        saver.restore(sess,ckpt.model_checkpoint_path)
    for i in range(num_episodes):
        episodeBuffer = experience_buffer()
        #Reset environment and get first new observation
        start = time.time()
        s = env.reset()
        envResetTime += time.time() - start
        s = processState(s, sizeEnv, env.getNumberOfChannels())
        d = False
        rAll = 0
        j = 0
        #The Q-Network
        while j < max_epLength: #If the agent takes longer than 200 moves to reach either of the blocks, end the trial.
            j+=1
            #Choose an action by greedily (with e chance of random action) from the Q-network
            if np.random.rand(1) < e or total_steps < pre_train_steps:
                a = np.random.randint(0,env.getActionCount())
            else:
                start0 = time.time()
                a = sess.run(mainQN.predict,feed_dict={mainQN.scalarInput:[s]})[0]
                networkTime += time.time() - start0
            
            start = time.time()
            s1,r,d = env.step(a)
            envRenderTime += time.time() - start
            
            s1 = processState(s1, sizeEnv, env.getNumberOfChannels())
            total_steps += 1
            episodeBuffer.add(np.reshape(np.array([s,a,r,s1,d]),[1,5])) #Save the experience to our episode buffer.
            
            if total_steps > pre_train_steps:
                if e > endE:
                    e -= stepDrop
                
                if total_steps % (update_freq) == 0:
                    start0 = time.time()
                    trainBatch = myBuffer.sample(batch_size) #Get a random batch of experiences.
                    #Below we perform the Double-DQN update to the target Q-values
                    Q1 = sess.run(mainQN.predict,feed_dict={mainQN.scalarInput:np.vstack(trainBatch[:,3])})
                    Q2 = sess.run(targetQN.Qout,feed_dict={targetQN.scalarInput:np.vstack(trainBatch[:,3])})
                    end_multiplier = -(trainBatch[:,4] - 1)
                    doubleQ = Q2[range(batch_size),Q1]
                    targetQ = trainBatch[:,2] + (y*doubleQ * end_multiplier)
                    #Update the network with our target values.
                    _ = sess.run(mainQN.updateModel, \
                        feed_dict={mainQN.scalarInput:np.vstack(trainBatch[:,0]),mainQN.targetQ:targetQ, mainQN.actions:trainBatch[:,1]})
                    
                    updateTarget(targetOps,sess) #Update the target network toward the primary network.

                    networkTime += time.time() - start0
            rAll += r
            if rAll < -5.0:
                d = True
            s = s1
            
            if d == True:
                break
        if rAll > maxScore:
            env.printStats()
            maxScore = rAll
            bestActions = env.getActionCount()
        myBuffer.add(episodeBuffer.buffer)
        jList.append(j)
        rList.append(rAll)
        #Periodically save the model. 
        if i % 1000 == 0:
            saver.save(sess,path+'/model-'+str(i)+'.ckpt')
            print("Saved Model")
            print("i: ", i)
            print("e: ", e)
            print("Total steps: ", total_steps)
            print("Env time: ", envRenderTime)
            print("Network time: ", networkTime)
        if len(rList) % 100 == 0:
            mean500 = np.mean(rList[-500:])
            max500 = np.max(rList[-500:])
            # if last_avg > 0:
            print("Average (500 /",i,"): ", mean500 , " Diff:", mean500 - last_avg)
            # print("Max (500): ", max500 , " Last:", last_max500)
            last_avg = mean500
            last_max500 = max500
    saver.save(sess,path+'/model-'+str(i)+'.ckpt')
print("Percent of succesful episodes: " + str(sum(rList)/num_episodes) + "%")
print("Best Score: ", maxScore)
print("Best Score Action list: ", bestActions)
print("Total steps: ", total_steps)
print("Env time: ", envRenderTime)
print("Reset time: ", envResetTime)
print("Network time: ", networkTime)
print("Total time: ",  time.time()-startComplete)
