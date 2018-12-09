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
from abc import abstractmethod
from squareObj import *
from triObj import *
from BasicEnvironmentRender import *
from MeshWorldGenerator import *

class AbstractMeshEnv():
    def __init__(self,partial,size, seedValue = 0, cornerMatchBonus = 20):
        if size < 4:
            raise ValueError('Size of Environment is too small.')
        self._nHeros = 0
        self._xRes = size
        self._yRes = size
        self.actions = 4
        self.objects = []
        self.startObjects = []
        self.partial = partial
        self._seed = seedValue
        self._cornerMatchBonus = cornerMatchBonus
        self._score = 0
        self._lastHeroScore = 0.0
        self._currentBonusValue = 0.0
        self._done = False
        self.reset()
        
    def getSizeX(self):
        return self._xRes 
    def getSizeY(self):
        return self._yRes 
    def getState(self):
        return self._state
    def setSeed(seedValue):
        self._seed = seedValue

    def getMaxNumberOfHeros(self):
        raise

    def reset(self):
        self.resetConcreteClassSpecifics()
        self._currentBonusValue = self.objects[-1].getBonusValue()
        
    def getStartScore(self):
        return self._currentBonusValue

    @abstractmethod
    def resetConcreteClassSpecifics(self):
        raise
    
    def resizeObjToFitEnv(self,hero):
        outOfBound = False
        (northWestX,northWestY) = hero.getNorthWest()
        (northEastX,northEastY) = hero.getNorthEast()
        if (northEastX >= self._xRes+2):
            northEastX = self._xRes+1
            outOfBound = True
        elif (northEastX < 0):
            northEastX = 0
            outOfBound = True
        if (northEastY >= self._yRes+2):
            northEastY = self._yRes+1
            outOfBound = True
        elif (northEastY < 0):
            northEastY = 0            
            outOfBound = True
        if (northWestX >= self._xRes+2):
            northWestX = self._xRes+1
            outOfBound = True
        elif (northWestX < 0):
            northWestX = 0
            outOfBound = True
        if (northWestY >= self._yRes+2):
            northWestY = self._yRes+1
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


    def createNewHero(self):
        raise
    
    def checkStartObject():
        raise
        nextIsInvalid = True
        while(nextIsInvalid):
            nextObj = self.startObjects[0]
  
    def calculateFinishedObjectBonusReward(self):
        (northWestCornerX,northWestCornerY) = self.objects[-1].getNorthWest()
        (northEastCornerX,northEastCornerY) = self.objects[-1].getNorthEast()
        reward = 0.0
        if self._state[northWestCornerX,northWestCornerY,1] == 1.0:
            reward += self._cornerMatchBonus
        if self._state[northEastCornerX,northEastCornerY,1] == 1.0:
            reward += self._cornerMatchBonus
        return reward            
    
    def moveChar(self,direction):
        if self._done:
            return 0, True
        # 0 - up, 1 - down, 2 - left, 3 - right
        hero = self.objects[-1]
        heroBackup = self.objects[-1]
        done = False
        changeNorthWestX = 0
        changeNorthWestY = 0
        changeNorthEastX = 0
        changeNorthEastY = 0
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

        reward = -0.1
        if direction == 8:
            reward += self.calculateFinishedObjectBonusReward()
            self.saveHeroAsWall()
            if (len(self.startObjects) > 0 and self._nHeros < self.getMaxNumberOfHeros()):
                hero= self.createNewHero() 
                self._nHeros += 1
                self._currentBonusValue = hero.getBonusValue() 
                reward += self._currentBonusValue 
                        
            else:
                done = True
        else:
            hero.changeNorthEast(changeNorthWestX, changeNorthWestY)            
            hero.changeNorthWest(changeNorthEastX, changeNorthEastY)
            idealArea = self.getIdealObjectArea(0,0)
            actualArea = hero.getArea()
            newBonusValue = idealArea - abs(actualArea-idealArea)
            reward += newBonusValue- self._currentBonusValue 
            self._currentBonusValue = newBonusValue
                        
        (hero,outOfbound) = self.resizeObjToFitEnv(hero)
        
        if self.renderEnv():
            self.objects[-1] = hero
        else:
            hero.changeNorthEast(-changeNorthWestX,-changeNorthWestY)            
            hero.changeNorthWest(-changeNorthEastX,-changeNorthEastY)  
            self.objects[-1] = hero
        return reward,done
 
    def renderEnv(self):
        render = BasicEnvironmentRender(self._xRes, self._yRes)

        (status,self._state) =  render.renderEnv(self.objects)
        return True
    
    def step(self,action):
        reward,done = self.moveChar(action)
        return self.getState(),reward,done

def test():
    env = meshEnv(partial=False,size=12, seedValue=2)
    
def valueLeftUnitTester():
#    print("0 == ",env.valueLeft(0,0,3,4))
#    print("1 == ",env.valueLeft(1,0,3,4))
#    print("1,2 == ",env.valueLeft(2,0,3,4))
#    print("2 == ",env.valueLeft(3,0,3,4))
#    print("3 == ",env.valueLeft(4,0,3,4))
    pass

