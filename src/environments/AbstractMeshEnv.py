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

from MeshWorldGenerator import *

class AbstractMeshEnv():
    def __init__(self,partial,size, seedValue = 0):
        self._nHeros = 0
        self._xRes = size
        self._yRes = size
        self.actions = 4
        self.objects = []
        self.startObjects = []
        self.partial = partial
        self._seed = seedValue
        self._score = 0
#        self._a = []
        self.reset()
#        plt.imshow(a,interpolation="nearest")
        
    def getSizeX(self):
        return self._xRes 
    def getSizeY(self):
        return self._yRes 
    def getState(self):
        return self._state
    def setSeed(seedValue):
        self._seed = seedValue
        
    def reset(self):
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
    
    def saveHeroAsWall(self):
        self.objects[-1].channel = 1
        self._score += self.objects[-1].calculateReward()
        if (self._nHeros > 0):
            northWest = self.objects[-1].getNorthWest()
            northEast = self.objects[-1].getNorthEast()
            channel = 1
            valueWest = self._state[northWest[0],northWest[1],channel]
            valueEast = self._state[northEast[0],northEast[1],channel]
            if((valueWest == 0.0) or (valueEast == 0.0)):
                self.startObjects.append(self.objects[-1])
                return
            else:
                for pixel in self.computePixelsFromLine(northWest[0],northWest[1],northEast[0],northEast[1]):
                    if(self._state[pixel[0],pixel[1],1] == 0.0 ):
                        self.startObjects.append(self.objects[-1])
                        return

    def createNewHero(self):
        raise
    
    def checkStartObject():
        raise
        nextIsInvalid = True
        while(nextIsInvalid):
            nextObj = self.startObjects[0]
  
    def calculateLockObjectReward(self):
        (northWestCornerX,northWestCornerY) = self.objects[-1].getNorthWest()
        (northEastCornerX,northEastCornerY) = self.objects[-1].getNorthEast()
        reward = 0.0
        rewardPerCorner = 10.0
        if self._state[northWestCornerX,northWestCornerY,1] == 1.0:
            reward += rewardPerCorner
        if self._state[northEastCornerX,northEastCornerY,1] == 1.0:
            reward += rewardPerCorner
        return reward            
    
    def moveChar(self,direction):
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

        reward = 0.0
        if direction == 8:
            reward = self.calculateLockObjectReward()
            self.saveHeroAsWall()
            if (len(self.startObjects) > 0):
                hero= self.createNewHero() 
            else:
#                print("done")
                done = True
        else:
            hero.changeNorthEast(changeNorthWestX,changeNorthWestY)            
            hero.changeNorthWest(changeNorthEastX,changeNorthEastY)
                        
        (hero,outOfbound) = self.resizeObjToFitEnv(hero)
        
        if self.renderEnv():
            self.objects[-1] = hero
        else:
            hero.changeNorthEast(-changeNorthWestX,-changeNorthWestY)            
            hero.changeNorthWest(-changeNorthEastX,-changeNorthEastY)  
            self.objects[-1] = hero
        return reward,done

    def checkGoal(self):
        return (self.objects[0].calculateReward(),False)
        
    def valueLeft(self,index,minValue,maxValue,maxIndex):
        difference = maxValue - minValue
        if difference < 0:
            direction = -1
        else:
            direction = 1
        
        maxIndexOdd = ((maxIndex+1) % 2 != 0 )
        differenceOdd = ((difference+1) % 2 != 0 )       
        midSectionIndex = int(maxIndex/2)
        valueSectionSize = int(abs(difference)/2)
        value = -1
        if (index == midSectionIndex): #Middsection
            if(maxIndexOdd and differenceOdd):
                value = minValue+valueSectionSize*direction
            elif(maxIndexOdd):
                value = minValue+valueSectionSize*direction
                return [value,value+direction]
            else:
                value = minValue+valueSectionSize*direction 
        elif (index < midSectionIndex):
            if(index < valueSectionSize ):
                value = minValue + index*direction
            else:
                value = minValue + valueSectionSize*direction
        elif (index >= midSectionIndex):
            if(index > maxIndex - valueSectionSize ):
                value = maxValue - (maxIndex - index)*direction
            else:
                value = maxValue - valueSectionSize*direction
            pass

        return [value]
        
    
    def computePixelsFromLine(self,x1,y1,x2,y2):
       #print("computePixelsFromLine")
        lengthX = x2-x1
        lengthY = y2-y1
       #print("lengthX",lengthX)
       #print("lengthY",lengthY)
        lengthMax = max(abs(lengthX),abs(lengthY))
       #print("max ", lengthMax)
        xOdd = (lengthX % 2 != 0 )
        yOdd = (lengthY % 2 != 0 )
        maxOdd = (lengthMax % 2 != 0 )
        
        if (maxOdd):
            firstSection = int(lengthMax/2)
        else:
            firstSection = int((lengthMax-1)/2)
#        for i = 0:
        pixels = [[x1,y1]]
        
        for i in range(1,lengthMax):
            x = self.valueLeft(i,x1,x2,lengthMax)
            y = self.valueLeft(i,y1,y2,lengthMax)

            pixels.append([x[0],y[0]])
            if(len(x) == 2 and len(y) == 1):
                pixels.append([x[1],y[0]])
            elif(len(x) == 1 and len(y) == 2):
                pixels.append([x[0],y[1]])
            elif(len(x) == 2 and len(y) == 2):
                pixels.append([x[1],y[1]])
            
        pixels.append([x2,y2])

        return pixels
    def calculateXYmoveUnitVector(self, point1x, point1y, point2x, point2y):
        xDiff = point2x-point1x
        yDiff = point2y-point1y  
        if (abs(xDiff) > abs(yDiff)):
            xMove = 0
            if xDiff != 0:
                yMove = -int(xDiff/abs(xDiff))
            else:
                yMove = 0
        else:
            if yDiff != 0:
                xMove = int(yDiff/abs(yDiff))
            else:
                xMove = 0
            yMove = 0
            
        return (xMove,yMove)
                
    def renderEnv(self):
        bufferX = 0
        bufferY = 0
        a = np.zeros([self._yRes+2,self._xRes+2,3])
        maxIndexX = self._yRes+1
        maxIndexY = self._xRes+1

        for item in self.objects:
            item.intensity = 0.75
            
            (southWestCornerX,southWestCornerY) = (item.getSouthWest()[0] + bufferX,item.getSouthWest()[1] + bufferY)
            (southEastCornerX,southEastCornerY) = (item.getSouthEast()[0] + bufferX,item.getSouthEast()[1] + bufferY)

            (northWestCornerX,northWestCornerY) = item.getNorthWest()
            (northEastCornerX,northEastCornerY) = item.getNorthEast()
            
            pixelsSouth = self.computePixelsFromLine(southEastCornerX,southEastCornerY,southWestCornerX,southWestCornerY)
            pixelsWest = self.computePixelsFromLine(southWestCornerX,southWestCornerY,northWestCornerX,northWestCornerY)
            pixelsNorth = self.computePixelsFromLine(northEastCornerX,northEastCornerY,northWestCornerX,northWestCornerY)
            pixelsEast = self.computePixelsFromLine(southEastCornerX,southEastCornerY,northEastCornerX,northEastCornerY)
            
            if item.getName() == "hero":
                wrongMove = False
                if [northWestCornerX,northWestCornerY] in pixelsWest[:-1]:
                    wrongMove = True
                if [northWestCornerX,northWestCornerY] in pixelsEast[:-1]:
                    wrongMove = True
                if [northEastCornerX,northEastCornerY] in pixelsWest[:-1]:
                    wrongMove = True
                if [northEastCornerX,northEastCornerY] in pixelsEast[:-1]:
                    wrongMove = True
                if wrongMove:
                    return False
                
            for pixel in pixelsWest:
                a[pixel[0],pixel[1],item.channel] = item.intensity

            for pixel in pixelsNorth:
                a[pixel[0],pixel[1],item.channel] = item.intensity

            for pixel in pixelsEast:
                a[pixel[0],pixel[1],item.channel] = item.intensity
                            
            for pixel in pixelsSouth:
                a[pixel[0],pixel[1],item.channel] = item.intensity
             
            a[pixelsWest[0][0],pixelsWest[0][1],item.channel] = 1
            a[pixelsWest[-1][0],pixelsWest[-1][1],item.channel] = 1
            a[pixelsEast[0][0],pixelsEast[0][1],item.channel] = 1
            a[pixelsEast[-1][0],pixelsEast[-1][1],item.channel] = 1
                        
            # Inside square
            (xMove,yMove) = self.calculateXYmoveUnitVector(southWestCornerX,southWestCornerY,
            southEastCornerX,southEastCornerY)  
            (xMove,yMove) = self.calculateXYmoveUnitVector(southWestCornerX,southWestCornerY,
            northWestCornerX,northWestCornerY) 
            if abs(xMove)+abs(yMove) > 0:
                for i in range(len(pixelsWest))[1:-1]:
                    move = True
                    j = 0
    
                    while(move and j < 100):
    
                        x = pixelsWest[i][0]+xMove*j
                        y = pixelsWest[i][1]+yMove*j
                        if x < 0 or y < 0 or y > maxIndexY or x > maxIndexY:
                            move = False
                            continue                        
                        if [x,y] in pixelsNorth:
                            move = False
                            continue
                        if [x,y] in pixelsSouth:
                            move = False
                            continue
                        if [x,y] in pixelsEast:
                            move = False
                            continue
    
                        if (a[x,y,item.channel] == 0):
                            a[x,y,item.channel] = 0.5
                        j +=1 
                        
            (xMove,yMove) = self.calculateXYmoveUnitVector(southEastCornerX,southEastCornerY,
            northEastCornerX,northEastCornerY) 
            #yMove *= -1
            #xMove *= -1
            if abs(xMove)+abs(yMove) > 0:
                for i in range(len(pixelsEast))[1:-1]:
                    move = True
                    j = 0
                    
                    while(move and j < 100):
                        x = pixelsEast[i][0]-xMove*j
                        y = pixelsEast[i][1]-yMove*j
                        if x < 0 or y < 0 or y > maxIndexY or x > maxIndexY:
                            move = False
                            continue    
                        if [x,y] in pixelsNorth:
                            move = False
                            continue
                        if [x,y] in pixelsSouth:
                            move = False
                            continue
                        if [x,y] in pixelsWest:
                            move = False
                            continue
                        if (a[x,y,item.channel] == 0):
                            a[x,y,item.channel] = 0.5
                        j +=1 
        b = a[:,:,0]
        c = a[:,:,1]
        d = a[:,:,2]
        self._state = np.stack([b,c,d],axis=2)
        return True
    
    
    def getScore(self):
        return self._score + self.objects[-1].calculateReward()
    
    def step(self,action):
        penalty,done = self.moveChar(action)
        reward,done1 = self.checkGoal()
        self._score += penalty
        if reward == None:
           #print(done)
           #print(reward)
           #print(penalty)
            return self.getState(),(reward+penalty),done
        else:
            return self.getState(),(reward+penalty),done
 
def doAction(action, states, env):
    (state,reward,done) =env.step(action)
    #print(reward)
    a = env.renderEnv()
    #print(state)
    states = np.concatenate([states,a],axis=1)
    return states

def test():
    env = meshEnv(partial=False,size=12, seedValue=2)
    
def valueLeftUnitTester():
#    print("0 == ",env.valueLeft(0,0,3,4))
#    print("1 == ",env.valueLeft(1,0,3,4))
#    print("1,2 == ",env.valueLeft(2,0,3,4))
#    print("2 == ",env.valueLeft(3,0,3,4))
#    print("3 == ",env.valueLeft(4,0,3,4))
    pass

