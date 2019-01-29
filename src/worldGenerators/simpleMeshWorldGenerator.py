# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 20:16:09 2018

@author: Rasmus
"""
from gameObjects.lineObj import *
from worldGenerators.AbstractMeshWorldGenerator import *

class simpleMeshWorldGenerator(AbstractMeshWorldGenerator):
    def __init__(self, xSize, ySize, maxDeviationX, maxDeviationY, deviationProbability = 0.4):
        AbstractMeshWorldGenerator.__init__(self, deviationProbability)
        self._xSize = xSize
        self._ySize = ySize
        self._maxDeviationX = maxDeviationX
        self._maxDeviationY = maxDeviationY
        self._idealAverageSquareArea = self._xSize * self._ySize 

    def generate(self, worldSizeX, worldSizeY):
        minX = 0
        minY = 0
        maxX = worldSizeX - 1
        maxY = worldSizeY - 1
        self._objects = []
        self._startObjects = [] 
        # TODO: Add checks that worldSizeX is bigger than _maxDeviations for x and y
        
        baseXLineLength = int(worldSizeX/self._xSize)
        baseYLineLength = int(worldSizeY/self._ySize)

        lastX = minX
        lastY = minY
        
        southWestX = lastX
        southWestY = lastY
        
        # print("southWest to southEast")
        
        for i in range(self._xSize):
            newX = lastX + baseXLineLength
            if i == self._xSize-1:
                newX = maxX
            else:
                newX += self.generateRandomDeviation(-self._maxDeviationX,self._maxDeviationX)
                
            newY = minY + self.generateRandomDeviation(0,self._maxDeviationX)
            
            oldObject1 = lineOb((lastX,lastY),(newX,newY))
            # print(lastX,lastY," - " ,newX,newY)
            
            lastY = newY
            lastX = newX
            self._objects.append(oldObject1)    
            self._startObjects.append(oldObject1) 

        southEastX = lastX
        southEastY = lastY
        lastX = southWestX
        lastY = southWestY
        
        # print("southWest to northWest")
        #### Y 
        if 1:
            for i in range(self._ySize):
                newY = lastY + baseYLineLength
                if i == self._ySize-1:
                    newY = maxY
                else:
                    newY += self.generateRandomDeviation(-self._maxDeviationY,self._maxDeviationY)
                    
                newX = minX + self.generateRandomDeviation(0,self._maxDeviationX)
                
                oldObject1 = lineOb((lastX,lastY),(newX,newY))
                # print(lastX,lastY," - " ,newX,newY)
                lastY = newY
                lastX = newX
                self._objects.append(oldObject1)    
    
            northWestX = lastX
            northWestY = lastY
        else:
            northWestX = minX
            northWestY = maxY
            lastX = northWestX
            lastY = northWestY

        if 1:
            # print("northWest to northEast")
            for i in range(self._xSize):
                newX = lastX + baseXLineLength
                if i == self._xSize-1:
                    newX = maxX
                else:
                    newX += self.generateRandomDeviation(-self._maxDeviationX,self._maxDeviationX)
                    
                newY = maxY - self.generateRandomDeviation(0,self._maxDeviationX)
                
                oldObject1 = lineOb((lastX,lastY),(newX,newY))
                # print(lastX,lastY," - " ,newX,newY)
                lastY = newY
                lastX = newX
                self._objects.append(oldObject1)   
                
            northEastX = lastX
            northEastY = lastY  


        lastX = southEastX
        lastY = southEastY

        if 1:
        # print("southEast to northEast")    
            for i in range(self._ySize):
                newY = lastY + baseYLineLength
                newX = maxX - self.generateRandomDeviation(0,self._maxDeviationX)
                if i == self._ySize-1:
                    newY = northEastY
                    newX = northEastX
                else:
                    newY += self.generateRandomDeviation(-self._maxDeviationY,self._maxDeviationY)
                
                oldObject1 = lineOb((lastX,lastY),(newX,newY))
                # print(lastX,lastY," - " ,newX,newY)
                lastY = newY
                lastX = newX
                self._objects.append(oldObject1)    
