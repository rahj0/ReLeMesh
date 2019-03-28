# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 23:17:07 2018

@author: Rasmus
"""
from gameObjects.gameObj import *

class triObj(gameObject):
    def __init__(self,coord1,coord2,intensity,channel,reward,name = "triObj"):
        southWest = (coord1[0],coord1[1])
        southEast = (coord2[0],coord2[1])
        xDif = (coord2[0] - coord1[0] ) / 2
        yDif = (coord2[1] - coord1[1] ) / 2
        southWest = coord1
        southEast = coord2
        northX = int(((coord1[0]-yDif)+(coord2[0]-yDif))/2)
        northY = int(((coord1[1]+xDif)+(coord2[1]+xDif))/2)
        
        northWest = (northX,northY)
        northEast = (northX,northY)
        gameObject.__init__(self,southWest,southEast,northWest,northEast,intensity,channel,reward,name)

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

    def getCenterPoint(self):
        x = self._southWest[0] + self._southEast[0] + self._northEast[0]
        y = self._southWest[1] + self._southEast[1] + self._northEast[1]
        return (int(x/3),int(y/3))

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
        return abs(0.5*((x2-x1)*(y3-y1)-(x3-x1)*(y2-y1)))

    def isNewShapeValid(self):
        angleTolerance = 1e-6
        maxAngle = 165.0 - angleTolerance
        minAngle = 0 + angleTolerance
        southWestAngle =self.calculateSouthWestCornerAngle()
        if southWestAngle > maxAngle or southWestAngle < minAngle:
            return False
        southEastAngle = self.calculateSouthEastCornerAngle()
        if southEastAngle > maxAngle or southEastAngle < minAngle:
            return False
        
        return True
