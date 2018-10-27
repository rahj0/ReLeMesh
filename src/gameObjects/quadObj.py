# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 23:17:07 2018

@author: Rasmus
"""
from gameObj import *

class quadObj(gameOb):
    def __init__(self,coord1,coord2,intensity,channel,reward,name):
        southWest = (coord1[0],coord1[1])
        southEast = (coord2[0],coord2[1])
        xDif = coord2[0] - coord1[0]
        yDif = coord2[1] - coord1[1] 
        southWest = coord1
        southEast = coord2
        northWest = (coord1[0]-yDif,coord1[1]+xDif)
        northEast = (coord2[0]-yDif,coord2[1]+xDif)
#        print("P",southWest,southEast,northWest,northEast)
        gameOb.__init__(self,southWest,southEast,northWest,northEast,intensity,channel,reward,name)

    def isNewShapeValid(self):
        angleTolerance = 1e-6
        maxAngle = 180.0 - angleTolerance
        minAngle = 0 + angleTolerance
        southWestAngle =self.calculateSouthWestCornerAngle()
        if southWestAngle > maxAngle or southWestAngle < minAngle:
            print("Not valid because of south west corner angle")
            return False
        southEastAngle = self.calculateSouthEastCornerAngle()
        if southEastAngle > maxAngle or southEastAngle < minAngle:
            print("Not valid because of south east corner angle")
            return False
        northWestAngle =self.calculateNorthWestCornerAngle()
        if northWestAngle > maxAngle or northWestAngle < minAngle:
            print("Not valid because of north west corner angle")
            return False
        norEastAngle = self.calculateNorthEastCornerAngle()
        if norEastAngle > maxAngle or norEastAngle < minAngle:
            print("Not valid because of north east corner angle")
            return False
        
        return True
