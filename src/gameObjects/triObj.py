# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 23:17:07 2018

@author: Rasmus
"""
from gameObjects.gameObj import *

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

    def getArea(self):
        x1 = self._southWest[0]
        y1 = self._southWest[1]
        x2 = self._northEast[0]
        y2 = self._northEast[1]
        x3 = self._southEast[0]
        y3 = self._southEast[1]
        return abs(0.5*(abs(x2-x1)*abs(y3-y1)-abs(x3-x1)*abs(y2-y1)))

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
