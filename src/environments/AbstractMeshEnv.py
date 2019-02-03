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

import numpy as np
import random
import itertools
import scipy.misc
import math
from abc import abstractmethod, ABC
from gameObjects.squareObj import *
from gameObjects.triObj import *
from environments.Rendering.BasicEnvironmentRender import *
from worldGenerators.AbstractMeshWorldGenerator import *
from worldGenerators.simpleMeshWorldGenerator import *
from random import shuffle

class AbstractMeshEnv(ABC):
    def __init__(self,partial,size, actions, seedValue = 0, cornerMatchBonus = 30):
        if size < 4:
            raise ValueError('Size of Environment is too small.')
        self._useCenterOfFocus = False
        self._overlappingPixelPenalty = 8
        self._xRes = size
        self._yRes = size
        self._nChannels = 2
        self._actionCount = actions
        self.partial = partial
        self._seed = seedValue
        self._cornerMatchBonus = cornerMatchBonus
        self._normaliseValue = (self._cornerMatchBonus+self.getIdealObjectArea(0,0) )
        self._render = BasicEnvironmentRender(self._xRes, self._yRes)
        self._worldGenerator = simpleMeshWorldGenerator(2, 2, 0, 0)
        self.reset()

    def getNumberOfChannels(self):
        return self._nChannels
    def getSizeX(self):
        return self._xRes 
    def getSizeY(self):
        return self._yRes 
    def getState(self):
        return self._state
    def setSeed(seedValue):
        self._seed = seedValue

    def setCenterOfFocus(self,newCenterOfFocus):
        self._useCenterOfFocus = True
        self._centerOfFocus = newCenterOfFocus

    def setWorldGenerator(self, newAbstractMeshWorldGenerator):
        self._worldGenerator = newAbstractMeshWorldGenerator
        self.reset()

    @abstractmethod
    def getMaxNumberOfHeros(self):
        raise
    
    def getHero(self):
        return self.objects[-1]

    def printStats(self):
        print("Steps:" + str(self._totalSteps))
        print("Reward:" + str(self._totalReward))
        print("Actions:" + str(self._actions))

    def getActionCount(self):
        return self._actionCount

    def resetVariables(self):
        self._centerOfFocus = (0,0)
        self._totalSteps = 0
        self._totalReward = 0
        self._actions = []
        self._nHeros = 0
        self.objects = []
        self.startObjects = []
        self._score = 0
        self._lastHeroScore = 0.0
        self._currentBonusValue = 0.0
        self._done = False

    def reset(self):
        self.resetVariables()
        self._worldGenerator.generate(self._xRes,self._yRes)
        self.objects.extend(self._worldGenerator.getObjects())
        self.startObjects.extend(self._worldGenerator.getStartObjects())
        shuffle(self.startObjects)
        hero = self.createNewHero()
        self._nHeros += 1
        self.objects.append(hero) 
        for gameObject in self.objects:
            self.resizeObjToFitEnv(gameObject)
        self.renderEnv()  

        actualArea = self.objects[-1].getArea()
        self._currentBonusValue = actualArea- pow(abs(actualArea-self.getIdealObjectArea(0,0)),1.50)
        self._currentBonusValue /= self._normaliseValue
        return self._state

    def getStartScore(self):
        return self._currentBonusValue

    def pushToFrontStarterObjectNearestToPoint(self, coord):
        x, y = coord
        nObjs = len(self.startObjects)
        if nObjs < 2:
            return
        nearestObj = 0
        smallestDistance =  math.inf
        for i in range(nObjs):
            (xObj,yObj) = self.startObjects[i].getCenterPoint()
            distance = math.sqrt((xObj-x)**2+(yObj-y)**2 )
            if distance < smallestDistance:
                nearestObj = i
                smallestDistance = distance
        self.startObjects.insert(0, self.startObjects.pop(nearestObj))
        
    def getIdealObjectArea(self,x,y):
        nObjects = self.getMaxNumberOfHeros()
        return (self._xRes-1) * (self._yRes-1)/ nObjects

    def resizeObjToFitEnv(self,hero):
        outOfBound = False
        (northWestX,northWestY) = hero.getNorthWest()
        (northEastX,northEastY) = hero.getNorthEast()
        if (northEastX >= self._xRes):
            northEastX = self._xRes-1
            outOfBound = True
        elif (northEastX < 0):
            northEastX = 0
            outOfBound = True
        if (northEastY >= self._yRes):
            northEastY = self._yRes-1
            outOfBound = True
        elif (northEastY < 0):
            northEastY = 0            
            outOfBound = True
        if (northWestX >= self._xRes):
            northWestX = self._xRes-1
            outOfBound = True
        elif (northWestX < 0):
            northWestX = 0
            outOfBound = True
        if (northWestY >= self._yRes):
            northWestY = self._yRes-1
            outOfBound = True
        elif (northWestY < 0):
            northWestY = 0 
            outOfBound = True
        hero.setNorthWest(northWestX,northWestY)
        hero.setNorthEast(northEastX,northEastY)
        return hero,outOfBound

    def convertHeroToStartObjects(self):       
        northWest = self.objects[-1].getNorthWest()
        northEast = self.objects[-1].getNorthEast()
        channel = 1
        valueWest = self._state[northWest[0],northWest[1],channel]
        valueEast = self._state[northEast[0],northEast[1],channel]
        if((valueWest == 0.0) or (valueEast == 0.0)):
            self.startObjects.append(self.objects[-1])
            return
        else:
            for pixel in BasicEnvironmentRender.computePixelsFromLine(northWest[0],northWest[1],northEast[0],northEast[1]):
                if(self._state[pixel[0],pixel[1],1] == 0.0 ):
                    self.startObjects.append(self.objects[-1])
                    return

    def saveHeroAsWall(self):
        self.objects[-1].channel = 1
        self._score += self.objects[-1].calculateReward()
        if (self._nHeros > 0):
            self.convertHeroToStartObjects()
        return

    @abstractmethod
    def createNewHero(self):
        raise
  
    def calculateFinishedObjectBonusReward(self):
        (northWestCornerX,northWestCornerY) = self.objects[-1].getNorthWest()
        (northEastCornerX,northEastCornerY) = self.objects[-1].getNorthEast()
        reward = 0.0
        if self._state[northWestCornerX,northWestCornerY,1] == 1.0:
            reward += self._cornerMatchBonus
        elif self._state[northWestCornerX,northWestCornerY,1] > 0.0:
            reward -= self._cornerMatchBonus
        if self._state[northEastCornerX,northEastCornerY,1] == 1.0:
            reward += self._cornerMatchBonus
        elif self._state[northEastCornerX,northEastCornerY,1] > 0.0:
            reward -= self._cornerMatchBonus
        return reward 

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
            changeNorthEastX = 1
        elif direction == 5:
            changeNorthEastX = -1
        elif direction == 6:
            changeNorthEastY = 1
        elif direction == 7:
            changeNorthEastY = -1
        elif direction == 8:
            newHero = True
        return (changeNorthWestX, changeNorthWestY, changeNorthEastX, changeNorthEastY, newHero) 

    def moveChar(self,direction):
        if self._done:
            return 0, True
        # 0 - up, 1 - down, 2 - left, 3 - right
        hero = self.objects[-1]
        heroBackup = self.objects[-1]
        done = False
        (changeNorthWestX, changeNorthWestY, changeNorthEastX, changeNorthEastY, newHero) = self.convertStepInput(direction)
        reward = -0.5
        if newHero:
            self.saveHeroAsWall()
            if self._useCenterOfFocus == True:
                self.pushToFrontStarterObjectNearestToPoint(self._centerOfFocus) 

            if (len(self.startObjects) > 0 and self._nHeros < self.getMaxNumberOfHeros()):
                hero= self.createNewHero() 
                self._nHeros += 1   
            else:
                done = True
        else:
            hero.changeNorthEast(changeNorthWestX, changeNorthWestY)            
            hero.changeNorthWest(changeNorthEastX, changeNorthEastY)
       
        (hero,outOfbound) = self.resizeObjToFitEnv(hero)

        if newHero:
            self._currentBonusValue = 0 
        self.renderEnv()
        # else:
        #     self.refreshEnv() TODO Fix 

        idealArea = self.getIdealObjectArea(0,0) # atm ideal area is not a function of the coordinates
        actualArea = hero.getArea()
        
        newBonusValue = actualArea 
        newBonusValue -= pow(abs(actualArea-idealArea),1.5) 
        # print("Area: ",actualArea)
        # print("idealArea:", idealArea)
        # print("Penalty: ", pow(abs(actualArea-idealArea),1.5))
        newBonusValue -= self.countOverlappingPixels()*self._overlappingPixelPenalty
        newBonusValue += self.calculateFinishedObjectBonusReward()
        reward += newBonusValue- self._currentBonusValue* self._normaliseValue
        self._currentBonusValue = newBonusValue / self._normaliseValue

        reward =  reward / self._normaliseValue
        self.objects[-1] = hero
        return reward,done
        
    def countFilledPixels(self):
        count = 0
        for i in range(self._state.shape[0]):
            for j in range(self._state.shape[0]):
                if self._state[i,j,1] > 0.0:
                    count += 1
                elif self._state[i,j,0] > 0.0:
                    count += 1
        return count 

    def countOverlappingPixels(self):
        count = 0
        for i in range(self._state.shape[0]):
            for j in range(self._state.shape[0]):
                value = self._state[i,j,0]
                if value > 0.0:
                    if value < 0.51: # TODO: Remove hardcoded value
                        if self._state[i,j,1] > 0.0:
                            count += 1
        print(count)
        return count
    def renderEnv(self):
        [status,state] =  self._render.renderEnv(self.objects)
        if status:
            self._state = state
            # self._state[0] = state[0]
            # self._state[1] = state[1]

    def refreshEnv(self):
        [status,state] =  self._render.renderEnvObject(self.objects[-1],np.zeros([self._yRes,self._xRes]))
        if status:
            self._state[:,:,self.objects[-1].channel] = state
    
    def step(self,action):
        self._actions.append(action)
        reward,done = self.moveChar(action)
        self._totalReward += reward
        self._totalSteps += 1
        return self.getState(),reward,done

