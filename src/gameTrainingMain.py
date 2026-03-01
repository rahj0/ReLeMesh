# -*- coding: utf-8 -*-
import argparse
import json
import numpy as np
import random
import tensorflow as tf
import os
import time

from environments.triMesherEnv import triMesherEnv
from worldGenerators.ObjectInTheMiddleWorldGenerator import *
from environments.PartialViewEnv import PartialViewEnv
from Networks.BasicQNetwork import Qnetwork, experience_buffer, processState, updateTarget

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--episodes', dest='nEpisodes', default=5000, type=int,
                        help='Number of episodes to run in training.')
    parser.add_argument('--load-model', dest='loadModel', action='store_true',
                        help='Resume training from saved model checkpoint.')
    args = parser.parse_args()
    num_episodes = args.nEpisodes
    load_model = args.loadModel
else:
    num_episodes = 5000
    load_model = False

sizeEnv = 15; xLines = 4; yLines = 4
nChannels = 2
fullEnv = triMesherEnv(size=25, seedValue=2, nLinesX=xLines, nLinesY=yLines)
fullEnv.setWorldGenerator(simpleMeshWorldGenerator(xLines, yLines, 0, 0))
env = PartialViewEnv(fullEnv, sizeEnv)

batch_size = 32 * 5   # How many experiences to use for each training step.
update_freq = 4 * 5   # How often to perform a training step.
y = 0.92              # Discount factor on the target Q-values
startE = 0.6          # Starting chance of random action
endE = 0.01           # Final chance of random action
max_epLength = 175    # The max allowed length of an episode.
annealing_steps = int(400000 * 5 * 0.3)  # Steps to reduce startE to endE.
print("Annealing steps: ", annealing_steps)

path = "./dqn"        # The path to save our model to.
h_size = 512          # Size of the final conv layer before dueling split.
tau = 0.001           # Rate to update target network toward primary.
bufferSize = 100000
pre_train_steps = bufferSize  # Random steps before training begins.

mainQN = Qnetwork(h_size, env.getActionCount(), sizeEnv, env.getNumberOfChannels())
targetQN = Qnetwork(h_size, env.getActionCount(), sizeEnv, env.getNumberOfChannels())
optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)

myBuffer = experience_buffer(buffer_size=bufferSize)

# Set the rate of random action decrease.
e = startE
stepDrop = (startE - endE) / annealing_steps

# Create lists to contain total rewards and steps per episode.
jList = []
rList = []
total_steps = 0

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

# Warm up networks with a dummy forward pass to build weights before soft-update.
dummy = np.zeros([1, sizeEnv * sizeEnv * nChannels], dtype=np.float32)
mainQN(dummy)
targetQN(dummy)

if load_model:
    print('Loading Model...')
    mainQN.load_weights(path + '/model-final.weights.h5')
    targetQN.load_weights(path + '/model-final.weights.h5')
    state_path = path + '/train-state.json'
    if os.path.exists(state_path):
        with open(state_path) as f:
            train_state = json.load(f)
        total_steps = train_state['total_steps']
        e = max(endE, train_state['e'])
        print(f'Resumed: total_steps={total_steps}, e={e:.4f}')
    else:
        print('No train-state.json found, starting epsilon/steps from scratch.')

for i in range(num_episodes):
    episodeBuffer = experience_buffer()
    # Reset environment and get first observation.
    start = time.time()
    s = env.reset()
    envResetTime += time.time() - start
    s = processState(s, sizeEnv, env.getNumberOfChannels())
    d = False
    rAll = 0
    j = 0
    # The Q-Network loop.
    while j < max_epLength:
        j += 1
        # Choose action: epsilon-greedy from Q-network.
        if np.random.rand(1) < e or total_steps < pre_train_steps:
            a = np.random.randint(0, env.getActionCount())
        else:
            start0 = time.time()
            a = mainQN.predict_action(
                np.array([s], dtype=np.float32)).numpy()[0]
            networkTime += time.time() - start0

        start = time.time()
        s1, r, d = env.step(a)
        envRenderTime += time.time() - start

        s1 = processState(s1, sizeEnv, env.getNumberOfChannels())
        total_steps += 1
        episodeBuffer.add(np.reshape(np.array([s, a, r, s1, d], dtype=object), [1, 5]))

        if total_steps > pre_train_steps:
            if e > endE:
                e -= stepDrop

            if total_steps % update_freq == 0:
                start0 = time.time()
                trainBatch = myBuffer.sample(batch_size)

                # Double-DQN target Q-values.
                states_next = np.vstack(trainBatch[:, 3]).astype(np.float32)
                Q1 = mainQN.predict_action(states_next).numpy()
                Q2 = targetQN(states_next).numpy()
                end_multiplier = -(trainBatch[:, 4] - 1)
                doubleQ = Q2[range(batch_size), Q1]
                targetQ = (trainBatch[:, 2] + (y * doubleQ * end_multiplier)).astype(np.float32)

                # Update the network with target values.
                states_cur = np.vstack(trainBatch[:, 0]).astype(np.float32)
                actions = trainBatch[:, 1].astype(np.int32)
                with tf.GradientTape() as tape:
                    Qout = mainQN(states_cur)
                    actions_onehot = tf.one_hot(actions, env.getActionCount())
                    Q = tf.reduce_sum(tf.multiply(Qout, actions_onehot), axis=1)
                    loss = tf.reduce_mean(tf.square(targetQ - Q))
                grads = tape.gradient(loss, mainQN.trainable_variables)
                optimizer.apply_gradients(zip(grads, mainQN.trainable_variables))

                updateTarget(mainQN, targetQN, tau)
                networkTime += time.time() - start0

        rAll += r
        if rAll < -5.0:
            d = True
        s = s1

        if d:
            break

    if rAll > maxScore:
        env.printStats()
        maxScore = rAll
        bestActions = env.getActionCount()

    myBuffer.add(episodeBuffer.buffer)
    jList.append(j)
    rList.append(rAll)

    # Periodically save the model.
    if i % 1000 == 0:
        mainQN.save_weights(path + '/model-' + str(i) + '.weights.h5')
        print("Saved Model")
        print("i: ", i)
        print("e: ", e)
        print("Total steps: ", total_steps)
        print("Env time: ", envRenderTime)
        print("Network time: ", networkTime)
        with open(path + '/train-state.json', 'w') as f:
            json.dump({'total_steps': total_steps, 'e': e}, f)
    if len(rList) % 100 == 0:
        mean500 = np.mean(rList[-500:])
        max500 = np.max(rList[-500:])
        print("Average (500 /", i, "): ", mean500, " Diff:", mean500 - last_avg)
        last_avg = mean500
        last_max500 = max500

mainQN.save_weights(path + '/model-final.weights.h5')
with open(path + '/train-state.json', 'w') as f:
    json.dump({'total_steps': total_steps, 'e': e}, f)
print("Percent of succesful episodes: " + str(sum(rList) / num_episodes) + "%")
print("Best Score: ", maxScore)
print("Best Score Action list: ", bestActions)
print("Total steps: ", total_steps)
print("Env time: ", envRenderTime)
print("Reset time: ", envResetTime)
print("Network time: ", networkTime)
print("Total time: ", time.time() - startComplete)
