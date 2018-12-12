# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 22:39:57 2018

@author: Rasmus
"""

from gameObjects.lineObj import *
import random

class AbstractMeshWorldGenerator():
    def __init__(self, deviationProbability):
        if deviationProbability < 1:
            deviationProbability *= 100.0
        self._deviationProbability = deviationProbability
        self._objects = []
        self._startObjects = []
        
    def generateRandomDeviation(self,minDeviation, maxDeviation ):
        if int(random.randint(0, 100)) < int(self._deviationProbability):
            return random.randint(minDeviation, maxDeviation)
        return 0
    
    def getObjects(self):
        return self._objects
    
    def getStartObjects(self):
        return self._startObjects
    

#
#xSize = 2
#ySize = 3
#devX = 2
#devY = 1
#obj = simpleMeshWorldGenerator(xSize, ySize, devX, devY)
#obj.generate(10,10)
