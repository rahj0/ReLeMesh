# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 19:13:13 2018

@author: Rasmus
"""

from math import atan, atan2
from math import degrees, radians, pi

class gameOb():
    def __init__(self,southWest,southEast,northWest,northEast,intensity,channel,reward,name):
#        self.x = coordinates[0]
#        self.y = coordinates[1]
#        self.size = size
        
        self.intensity = intensity
        self.channel = channel
        self.reward = reward
        self.name = name

        self._southWest = southWest
        self._southEast = southEast
        self._northWest = northWest
        self._northEast = northEast
    def getCenterPoint(self):
        x = self._southWest[0] + self._southEast[0] + self._northWest[0] + self._northEast[0]
        y = self._southWest[1] + self._southEast[1] + self._northWest[1] + self._northEast[1]
        return (int(x/4),int(y/4))
        
    def calculateSouthWestCornerAngle(self):
        angle1 = self.calculateAngle(self._southWest,self._southEast)
        angle2 = self.calculateAngle(self._southWest,self._northWest) 
        angle = angle2 - angle1
        if (angle2 < angle1):
            angle += 360.0
        return angle
    
    def calculateSouthEastCornerAngle(self):
        angle1 = self.calculateAngle(self._southEast,self._southWest)
        angle2 = self.calculateAngle(self._southEast,self._northEast) 
        angle = angle1-angle2
        if (angle1 < angle2):
            angle += 360.0
        return angle

    def calculateNorthWestCornerAngle(self):
        angle1 = self.calculateAngle(self._northWest,self._northEast)
        angle2 = self.calculateAngle(self._northWest,self._southWest) 
        angle = angle1 - angle2
        if (angle1 < angle2):
            angle += 360.0
        return angle
    
    def calculateNorthEastCornerAngle(self):
        angle1 = self.calculateAngle(self._northEast,self._northWest)
        angle2 = self.calculateAngle(self._northEast,self._southEast) 
        angle = angle2-angle1
        if (angle2 < angle1):
            angle += 360.0
        return angle
    def getArea(self):
        x1 = self._southWest[0]
        y1 = self._southWest[1]
        x2 = self._northWest[0]
        y2 = self._northWest[1]

        x3 = self._northEast[0]
        y3 = self._northEast[1]
        x4 = self._southEast[0]
        y4 = self._southEast[1]

        a123 = abs(0.5*((x2-x1)*(y3-y1)-(x3-x1)*(y2-y1)))
        a341 = abs(0.5*((x4-x1)*(y3-y1)-(x3-x1)*(y4-y1)))
        return a123+a341

    def getBonusValue(self):
        bonusValue = 0
        bonusValue += self.getArea()
        return bonusValue
    
    def isNewShapeValid(self):
        return True
    
    def calculateAngle(self, originPoint, secondPoint):
        difX = secondPoint[0] - originPoint[0]
        difY = secondPoint[1] - originPoint[1]
#    
#        angle = atan(abs(difY)/abs(difX))
#        if(difX < 0.0 and difY > 0.0):
#            print("1")
#            angle += 0.5*pi
#        if(difX < 0.0 and difY < 0.0):
#            print("2")
#            angle += pi
#        if(difX > 0.0 and difY < 0.0):
#            print("3")
#            angle += 1.5*pi
        angle = atan2(difY,difX)
        if (angle<0.0):
            angle = 2*pi + angle
        return degrees(angle)
        # ---------- 0 deg
        #
        #      /
        #     / 
        #   /   45 ish deg
        #  /______
        #  \
        #   \
        #    \  - 55 ish deg
        
    def getName(self):
        return self.name
    
    def printAngles(self):
        pass
#        print("SouthWest: ", self.calculateSouthWestCornerAngle())
#        print("SouthEast: ", self.calculateSouthEastCornerAngle())
#        print("NorthWest: ", self.calculateNorthWestCornerAngle())
#        print("NorthEast: ", self.calculateNorthEastCornerAngle())
#        print("")
    
    def changeNorthWest(self,xChange, yChange):
        oldCoordinate = self._northWest
        self._northWest = (self._northWest[0]+xChange,self._northWest[1]+yChange)
        if not self.isNewShapeValid():
            self._northWest = oldCoordinate

    def changeNorthEast(self,xChange, yChange):
        oldCoordinate = self._northEast
        self._northEast = (self._northEast[0]+xChange,self._northEast[1]+yChange)
        if not self.isNewShapeValid():
            self._northEast = oldCoordinate   
            
    def changeSouthWest(self,xChange, yChange):
        oldCoordinate = self._southWest
        self._southWest = (self._southWest[0]+xChange,self._southWest[1]+yChange)
        if not self.isNewShapeValid():
            self._northEast = oldCoordinate 
            
    def changeSouthEast(self,xChange, yChange):
        oldCoordinate = self._southEast
        self._southEast = (self._southEast[0]+xChange,self._southEast[1]+yChange)
        if not self.isNewShapeValid():
            self._southEast = oldCoordinate 
            
    def setNorthWest(self, x, y):
        self._northWest = (x,y)
        
    def setNorthEast(self, x, y):
        self._northEast = (x,y)     
        
    def calculateReward(self):
        area = self.calculateArea()
        penalty = self.skewnessPenalty()
        return area-penalty
    
    def calculateArea(self):
        length = abs(self._southWest[0] - self._northEast[0])
        height = abs(self._southWest[1] - self._northEast[1])
        print("length", length)
        print("height", height)
        return length*height
    
    def skewnessPenalty(self):
        penalty = 0.0
        multiplier = 1.5
        penalty += abs(90-self.calculateSouthWestCornerAngle())*multiplier
        penalty += abs(90-self.calculateNorthWestCornerAngle())*multiplier
        penalty += abs(90-self.calculateSouthEastCornerAngle())*multiplier
        penalty += abs(90-self.calculateNorthEastCornerAngle())*multiplier
        return penalty

    def getNorthWest(self):
        return self._northWest
    
    def getNorthEast(self):
        return self._northEast
    
    def getSouthWest(self):
        return self._southWest
    
    def getSouthEast(self):
        return self._southEast
    
def calculateAngle(originPoint, secondPoint):
    difX =secondPoint[0] - originPoint[0]
    difY =secondPoint[1] - originPoint[1]
#    
#    angle = atan(abs(difY)/abs(difX))
#    
#    if(difX < 0.0 and difY > 0.0):
#        print("1")
#        angle += 0.5*pi
#    if(difX < 0.0 and difY < 0.0):
#        print("2")
#        angle += pi
#    if(difX > 0.0 and difY < 0.0):
#        print("3")
#        angle += 1.5*pi
    return degrees(atan2(difY,difX))
    
    # ---------- 0 deg
    #
    #      /
    #     / 
    #   /   45 ish deg
    #  /______
    
