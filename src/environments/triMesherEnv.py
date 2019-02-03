# -*- coding: utf-8 -*-
"""
Created on Thu May 24 22:40:03 2018

@author: Rasmus
"""

# -*- coding: utf-8 -*-
"""
Created on Tue May  8 22:44:07 2018

@author: Rasmus
"""
import sys

import numpy as np
import random
import itertools
import scipy.misc
from abc import abstractmethod
from gameObjects.triObj import *
from environments.AbstractMeshEnv import *

class triMesherEnv(AbstractMeshEnv):
    ''' Create Mesh Environment using triangles.
    :param size: Number of pixels in x and y direction
    '''
    def __init__(self,size, seedValue = 0, nLinesY = 3, nLinesX = 3):
        self._nLinesX = nLinesX
        self._nLinesY = nLinesY
        actions = 9
        AbstractMeshEnv.__init__(self, False, size, actions, seedValue)
        self.setWorldGenerator(simpleMeshWorldGenerator(nLinesX,nLinesY, 0, 0))

    def getMaxNumberOfHeros(self):
        return self._nLinesX * self._nLinesY * 2

    def cleanupStarterObjects(self, newObject):
        north = self.objects[-1].getNorthWest()
        southWest = self.objects[-1].getSouthWest()
        southEast = self.objects[-1].getSouthEast()

        pixels = []
        pixels.extend(BasicEnvironmentRender.computePixelsFromLine(southWest[0],southWest[1],north[0],north[1]))
        pixels.extend(BasicEnvironmentRender.computePixelsFromLine(southEast[0],southEast[1],north[0],north[1]))

        objectsToDelete = []

        for startObject in self.startObjects:
            northWest = startObject.getNorthWest()
            northEast = startObject.getNorthEast()
            eastFound = False
            westFound = False
            for pixel in pixels:
                if northWest[0] == pixel[0] and northWest[1] == pixel[1]: #can we compare directly ?
                    westFound = True
                if northEast[0] == pixel[0] and northEast[1] == pixel[1]: #can we compare directly ?
                    eastFound = True
            if eastFound and westFound:
                objectsToDelete.append(startObject)
        for objectToDelete in objectsToDelete:
             self.startObjects.remove(objectToDelete)


    def convertStepInput(self,direction):
        changeNorthWestX = 0
        changeNorthWestY = 0
        changeNorthEastX = 0
        changeNorthEastY = 0
        newHero = False
        if direction == 0:
            changeNorthWestX = 1
        elif direction == 1:
            changeNorthWestX = -1
        elif direction == 2:
            changeNorthWestY = 1
        elif direction == 3:
            changeNorthWestY = -1
        elif direction == 4:          
            changeNorthWestX = 1
            changeNorthWestY = 1
        elif direction == 5:
            changeNorthWestX = -1
            changeNorthWestY = 1
        elif direction == 6:
            changeNorthWestX = 1
            changeNorthWestY = -1
        elif direction == 7:
            changeNorthWestX = -1
            changeNorthWestY = -1
        elif direction == 8: # 8 is used by the viewer
            newHero = True
        return (changeNorthWestX, changeNorthWestY, changeNorthEastX, changeNorthEastY, newHero) 

    def convertHeroToStartObjects(self): 
        north = self.objects[-1].getNorthWest()
        southWest = self.objects[-1].getSouthWest()
        southEast = self.objects[-1].getSouthEast()
        self.cleanupStarterObjects(self.objects[-1])
        channel = 1
        valueNorth = self._state[north[0],north[1],channel]
        valueSouthWest = self._state[southWest[0],southWest[1],channel]
        valueSouthEast = self._state[southEast[0],southEast[1],channel]

        westObj = lineOb(southWest,north)
        eastObj = lineOb(north,southEast)

        westUsed = False
        eastUsed = False
        if((valueNorth == 0.0) or (valueSouthWest == 0.0)):
            if(southWest[0] != 0 and north[0] != 0):
                self.startObjects.append(westObj)
                westUsed = True
        if not westUsed:
            for pixel in BasicEnvironmentRender.computePixelsFromLine(southWest[0],southWest[1],north[0],north[1]):
                if(self._state[pixel[0],pixel[1],channel] == 0.0 ):
                    if(pixel[0] != 0):
                        self.startObjects.append(westObj)
                        break

        if((valueNorth == 0.0) or (valueSouthEast == 0.0)):
            if(southEast[0] != self._xRes+1 and north[0] != self._xRes+1):
                self.startObjects.append(eastObj)
                eastUsed = True
        if not eastUsed:
            for pixel in BasicEnvironmentRender.computePixelsFromLine(north[0],north[1],southEast[0],southEast[1]):
                if(self._state[pixel[0],pixel[1],channel] == 0.0 ):
                    if(pixel[0] != self._xRes+1):
                        self.startObjects.append(eastObj)
                        break

    def calculateFinishedObjectBonusReward(self):
        (northEastCornerX,northEastCornerY) = self.objects[-1].getNorthEast()
        reward = 0.0
        if self._state[northEastCornerX,northEastCornerY,1] == 1.0:
            reward += self._cornerMatchBonus
        elif self._state[northEastCornerX,northEastCornerY,1] > 0.0:
            reward -= self._cornerMatchBonus
        return reward   

    def createNewHero(self):

        starter = self.startObjects[0]
        self.startObjects.pop(0)
        
        hero = triObj(starter.getNorthWest(),starter.getNorthEast(),1,0,None,'hero')
        (hero,outOfbound) = self.resizeObjToFitEnv(hero)
    
        self.objects.append(hero)
        return hero
    
