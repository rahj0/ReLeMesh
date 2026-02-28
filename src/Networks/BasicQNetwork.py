# -*- coding: utf-8 -*-
import numpy as np
import random
import tensorflow as tf


class Qnetwork(tf.keras.Model):
    def __init__(self, h_size, envActions, sizeEnv, nChannels):
        super().__init__()
        self.sizeEnv = sizeEnv
        self.nChannels = nChannels
        self.h_size = h_size
        self.envActions = envActions

        self.conv1 = tf.keras.layers.Conv2D(
            64, [4, 4], strides=[2, 2], padding='valid', use_bias=False)
        self.conv2 = tf.keras.layers.Conv2D(
            128, [4, 4], strides=[2, 2], padding='valid', use_bias=False)
        self.conv3 = tf.keras.layers.Conv2D(
            h_size, [2, 2], strides=[1, 1], padding='valid', use_bias=False)
        self.flat = tf.keras.layers.Flatten()
        # Dueling streams: advantage and value
        self.advantage_dense = tf.keras.layers.Dense(
            envActions, use_bias=False, kernel_initializer='glorot_uniform')
        self.value_dense = tf.keras.layers.Dense(
            1, use_bias=False, kernel_initializer='glorot_uniform')

    def call(self, x):
        x = tf.cast(x, tf.float32)
        x = tf.reshape(x, [-1, self.sizeEnv, self.sizeEnv, self.nChannels])
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        # Split along channel axis into advantage and value streams
        streamA, streamV = tf.split(x, 2, axis=3)
        streamA = self.flat(streamA)
        streamV = self.flat(streamV)
        advantage = self.advantage_dense(streamA)
        value = self.value_dense(streamV)
        qout = value + (advantage - tf.reduce_mean(advantage, axis=1, keepdims=True))
        return qout

    def predict_action(self, x):
        return tf.argmax(self(x), axis=1)


class experience_buffer():
    def __init__(self, buffer_size=10000):
        self.buffer = []
        self.buffer_size = buffer_size

    def add(self, experience):
        if len(self.buffer) + len(experience) >= self.buffer_size:
            self.buffer[0:(len(experience) + len(self.buffer)) - self.buffer_size] = []
        self.buffer.extend(experience)

    def sample(self, size):
        return np.reshape(np.array(random.sample(self.buffer, size), dtype=object), [size, 5])


def processState(states, sizeEnv, nChannels):
    return np.reshape(states, [sizeEnv * sizeEnv * nChannels])


def updateTarget(mainQN, targetQN, tau):
    for main_var, target_var in zip(mainQN.trainable_variables, targetQN.trainable_variables):
        target_var.assign(tau * main_var + (1 - tau) * target_var)
