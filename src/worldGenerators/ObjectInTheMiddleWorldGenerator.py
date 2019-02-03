# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 20:16:09 2018

@author: Rasmus
"""
from gameObjects.lineObj import *
from gameObjects.triObj import *
from random import randint
from worldGenerators.AbstractMeshWorldGenerator import *
from worldGenerators.simpleMeshWorldGenerator import *

class ObjectInTheMiddleWorldGenerator(AbstractMeshWorldGenerator):
    def __init__(self, xSize, ySize, maxDeviationX, maxDeviationY, deviationProbability = 0.4):
        AbstractMeshWorldGenerator.__init__(self, deviationProbability)
        self._boundaryGenerator = simpleMeshWorldGenerator(xSize, ySize, maxDeviationX, maxDeviationY, deviationProbability)

        self._xSize = xSize
        self._ySize = ySize
        self._maxDeviationX = maxDeviationX
        self._maxDeviationY = maxDeviationY
        self._idealAverageSquareArea = self._xSize * self._ySize 

    def generate(self, worldSizeX, worldSizeY):
        minX = 0
        minY = 0
        maxX = worldSizeX - 1
        maxY = worldSizeY - 1

        self._boundaryGenerator.generate(worldSizeX, worldSizeY)
        self._objects = self._boundaryGenerator.getObjects()
        self._startObjects = self._boundaryGenerator.getStartObjects()

        yInter = random.randint(1, 3) 
        xInter = random.randint(1, 3)
        x1 = (self._xSize*xInter,self._ySize*yInter)
        yInter = random.randint(-1, 1) 
        xInter = random.randint(-1, 1)
        x1 = (x1[0]+xInter,x1[1]+yInter)
        x2 = (x1[0]+self._xSize,x1[1])
        x3 = (x1[0],x2[1]+self._ySize)
        obj = triObj(x1,x2,1,1,0)
        obj.setNorthEast(x3[0],x3[1])

        self._objects.append(obj)