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
sys.path.append('gameObjects')
sys.path.append('worldGenerators')
import numpy as np
import random
import itertools
import scipy.misc
from abc import abstractmethod
from triObj import *
from simpleMeshWorldGenerator import *
from AbstractMeshEnv import *

class triMesherEnv(AbstractMeshEnv):
    def __init__(self,partial,size, seedValue = 0):
        AbstractMeshEnv.__init__(self, partial, size, seedValue)
        
    def reset(self):
        self.objects = []
        
        xLines = 3
        yLines = 3

        obj = simpleMeshWorldGenerator(xLines, yLines, 2, 2)
        obj.generate(self._xRes+2,self._yRes+2)
        self.objects.extend(obj.getObjects())
        self.startObjects.extend(obj.getStartObjects())
        
        hero = self.createNewHero()
        self.objects.append(hero)        
#        
        self._state = self.renderEnv()  
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



    def convertHeroToStartObjects(self): 
        north = self.objects[-1].getNorthWest()
        southWest = self.objects[-1].getSouthWest()
        southEast = self.objects[-1].getSouthEast()
        self.cleanupStarterObjects(self.objects[-1])
        channel = 1
        valueNorth = self._state[north[0],north[1],channel]
        valueSouthWest = self._state[southWest[0],southWest[1],channel]
        valueSouthEast = self._state[southEast[0],southEast[1],channel]
        print(valueSouthEast)
        print(valueSouthWest)
        print(valueNorth)

        westObj = lineOb(southWest,north)
        eastObj = lineOb(north,southEast)

        if((valueNorth == 0.0) or (valueSouthWest == 0.0)):
            self.startObjects.append(westObj)
        else:
            for pixel in BasicEnvironmentRender.computePixelsFromLine(southWest[0],southWest[1],north[0],north[1]):
                if(self._state[pixel[0],pixel[1],channel] == 0.0 ):
                    self.startObjects.append(westObj)
                    break

        if((valueNorth == 0.0) or (valueSouthEast == 0.0)):
            self.startObjects.append(eastObj)
        else:
            for pixel in BasicEnvironmentRender.computePixelsFromLine(north[0],north[1],southEast[0],southEast[1]):
                if(self._state[pixel[0],pixel[1],channel] == 0.0 ):
                    self.startObjects.append(eastObj)
                    break

    def calculateFinishedObjectBonusReward(self):
        (northEastCornerX,northEastCornerY) = self.objects[-1].getNorthEast()
        reward = 0.0
        rewardPerCorner = 10.0
        if self._state[northEastCornerX,northEastCornerY,1] == 1.0:
            reward += rewardPerCorner
        return reward   
        
    def createNewHero(self):

        starter = self.startObjects[0]
        self.startObjects.pop(0)
        
        hero = triObj(starter.getNorthWest(),starter.getNorthEast(),1,2,None,'hero')
        (hero,outOfbound) = self.resizeObjToFitEnv(hero)
    
        self.objects.append(hero)
        self._nHeros += 1
        return hero
    
