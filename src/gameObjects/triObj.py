# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 23:17:07 2018

@author: Rasmus
"""
from gameObj import *

class triObj(gameOb):
    def __init__(self,coord1,coord2,intensity,channel,reward,name = "triObj"):
        southWest = (coord1[0],coord1[1])
        southEast = (coord2[0],coord2[1])
        xDif = (coord2[0] - coord1[0] ) / 2
        yDif = (coord2[1] - coord1[1] ) / 2
        southWest = coord1
        southEast = coord2
#        northWest = (coord1[0]-yDif,coord1[1]+xDif)
#        northEast = (coord2[0]-yDif,coord2[1]+xDif)
        northX = int(((coord1[0]-yDif)+(coord2[0]-yDif))/2)
#        northX = int((coord1[0]-yDif/2))
#        northY = int((coord1[1]+xDif/2))
        northY = int(((coord1[1]+xDif)+(coord2[1]+xDif))/2)
        
        northWest = (northX,northY)
        northEast = (northX,northY)
        #print("P",southWest,southEast,northWest,northEast)
        gameOb.__init__(self,southWest,southEast,northWest,northEast,intensity,channel,reward,name)

    def changeNorthWest(self,xChange, yChange):
        oldCoordinate = self._northWest
        self._northWest = (self._northWest[0]+xChange,self._northWest[1]+yChange)
        if not self.isNewShapeValid():
            self._northWest = oldCoordinate
        else:
            self._northEast = self._northWest

    def changeNorthEast(self,xChange, yChange):
        oldCoordinate = self._northEast
        self._northEast = (self._northEast[0]+xChange,self._northEast[1]+yChange)
        self.printAngles()
        if not self.isNewShapeValid():
            self._northEast = oldCoordinate
        else:
            self._northWest = self._northEast

    def setNorthWest(self, x, y):
        self._northWest = (x,y)
        self._northEast = (x,y)
        
    def setNorthEast(self, x, y):
        self._northEast = (x,y)
        self._northWest = (x,y)

    def calculateFinishedObjectBonusReward(self):
        (northEastCornerX,northEastCornerY) = self.objects[-1].getNorthEast()
        reward = 0.0
        rewardPerCorner = 10.0
        if self._state[northEastCornerX,northEastCornerY,1] == 1.0:
            reward += rewardPerCorner
        return reward      

    def isNewShapeValid(self):
#        return True
        angleTolerance = 1e-6
        maxAngle = 165.0 - angleTolerance
        minAngle = 0 + angleTolerance
        southWestAngle =self.calculateSouthWestCornerAngle()
        if southWestAngle > maxAngle or southWestAngle < minAngle:
            print("Not valid because of south west corner angle")
            return False
        southEastAngle = self.calculateSouthEastCornerAngle()
        if southEastAngle > maxAngle or southEastAngle < minAngle:
            print("Not valid because of south east corner angle")
            return False
#        northWestAngle =self.calculateNorthWestCornerAngle()
#        if northWestAngle > maxAngle or northWestAngle < minAngle:
#            print("Not valid because of north west corner angle")
#            return False
#        norEastAngle = self.calculateNorthEastCornerAngle()
#        if norEastAngle > maxAngle or norEastAngle < minAngle:
#            print("Not valid because of north east corner angle")
#            return False
        
        return True
