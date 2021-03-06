# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 22:39:57 2018

@author: Rasmus
"""
# Abstract class for generating starting point for the Environments

from abc import abstractmethod, ABC
import random
from gameObjects.lineObj import *

class AbstractMeshWorldGenerator(ABC):
    def __init__(self, deviationProbability):
        if deviationProbability < 1:
            deviationProbability *= 100.0
        self._deviationProbability = deviationProbability
        self._objects = []
        self._startObjects = []
        self._idealAverageSquareArea = 0.0
        
    def generateRandomDeviation(self,minDeviation, maxDeviation ):
        if int(random.randint(0, 100)) < int(self._deviationProbability):
            return random.randint(minDeviation, maxDeviation)
        return 0
    
    def getObjects(self):
        return self._objects
    
    def getStartObjects(self):
        return self._startObjects
        
    @abstractmethod
    def generate(self, worldSizeX, worldSizeY):
        raise

    def getIdealAverageSquareArea(self):
        if self._idealAverageObjectArea <= 0.0:
            raise
        return self._idealAverageSquareArea

    def generateBorder(self,minX, minY, maxX, maxY, cornerMovement = [[0,0],[0,0],[0,0],[0,0]]):
                
        southWestX = minX + cornerMovement[0][0]
        southWestY = minY + cornerMovement[0][1]
        southWest = (southWestX,southWestY)

        southEastX = maxX - cornerMovement[1][0]
        southEastY = minY + cornerMovement[1][1]
        southEast = (southEastX,southEastY)

        northWestX = minX + cornerMovement[2][0]
        northWestY = maxY - cornerMovement[2][1]   
        northWest = (northWestX,northWestY)

        northEastX = maxX - cornerMovement[3][0]
        northEastY = maxY - cornerMovement[3][1]  
        northEast = (northEastX,northEastY)

        self._objects.append(lineOb((southWestX,southWestY),(southEastX,southEastY))) # south
        self._objects.append(lineOb((northWestX,northWestY),(southWestX,southWestY))) # West
        self._objects.append(lineOb((northEastX,northEastY),(northWestX,northWestY))) # North
        self._objects.append(lineOb((southEastX,southEastY),(northEastX,northEastY))) # East
        
            
