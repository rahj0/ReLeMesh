# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 20:25:51 2018

@author: Rasmus
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 20:16:09 2018

@author: Rasmus
"""
from lineObj import *
from triObj import *
from AbstractMeshWorldGenerator import *

class WorldGeneratorForSecondConvNetworkTest(AbstractMeshWorldGenerator):
    def __init__(self,gameObjIndexX, gameObjIndexY,
                 realCorner, slasForward, horiMove, vertMove):
        self._gameObjIndexX = gameObjIndexX
        self._gameObjIndexY = gameObjIndexY
        self._realCorner = realCorner
        self._slasForward = slasForward
        self._horiMove = horiMove
        self._vertMove = vertMove
        self._gridPoints =[]
        self._hLines = 6
        self._vLines = 6
        deviationProbability = 0.5
        AbstractMeshWorldGenerator.__init__(self, deviationProbability)
        
    def generate(self, worldSizeX, worldSizeY):
        minX = 0
        minY = 0
        maxX = worldSizeX - 1
        maxY = worldSizeY - 1
        lineSizeX = int((worldSizeX-1)/self._hLines)
        lineSizeY = int((worldSizeY-1)/self._vLines)

            
        for i in range(self._hLines+1):
            vec = []
            for j in range(self._vLines+1):
                x = i*lineSizeX
                y = j*lineSizeY
                x1 = x
                y1 = y
                if(i==int(self._hLines/2) and j>0 and j<self._vLines):
                    x = x + self._vertMove[0]
                    y = y + self._vertMove[1]
                if(j==int(self._vLines/2) and i>0 and i<self._hLines):
                    x = x + self._horiMove[0]
                    y = y + self._horiMove[1]
                vec.append((x,y))
                
            self._gridPoints.append(vec)
        

        # horisontal lines
        for i in range(self._hLines):
            for j in range(self._vLines+1):
                point1 = self._gridPoints[i][j]
                point2 = self._gridPoints[i+1][j]
                self._objects.append(lineOb((point1[0],point1[1]),(point2[0],point2[1])))
#       # vertical lines
        for i in range(self._hLines+1):
            for j in range(self._vLines):
                point1 = self._gridPoints[i][j]
                point2 = self._gridPoints[i][j+1]
                self._objects.append(lineOb((point1[0],point1[1]),(point2[0],point2[1])))    
                
                
        for i in range(self._hLines):
            for j in range(self._vLines):
                if(self._gameObjIndexX == i-1 and self._gameObjIndexY == j-1):
                    continue
                point1 = self._gridPoints[i][j]
                point2 = self._gridPoints[i+1][j]
                point3 = self._gridPoints[i+1][j+1]
                point4 = self._gridPoints[i][j+1]
                self._objects.append(triObj((point1[0],point1[1]),(point2[0],point2[1]),0,1,None))
                self._objects.append(triObj((point3[0],point3[1]),(point4[0],point4[1]),0,1,None))
                if self._slasForward:
                    self._objects[-2].setNorthWest(point4[0],point4[1])
                    self._objects[-1].setNorthWest(point2[0],point2[1])
                else:
                    self._objects[-2].setNorthWest(point3[0],point3[1])
                    self._objects[-1].setNorthWest(point1[0],point1[1])

            
        for i in [self._gameObjIndexX +1]:
            for j in [self._gameObjIndexY+1]:
                pointSW = self._gridPoints[i][j]
                pointSE = self._gridPoints[i+1][j]
                pointNE = self._gridPoints[i+1][j+1]
                pointNW = self._gridPoints[i][j+1]  
                if self._realCorner ==2: # Real corner: NE
                    point1 = pointSE
                    point2 = pointNW
                    point3 = pointSW
                    point4 = pointNE
                if self._realCorner ==3: # Real corner: SE
                    point1 = pointSW
                    point2 = pointNE
                    point3 = pointNW
                    point4 = pointSE
                if self._realCorner ==0: # Real corner: SW
                    point1 = pointNW
                    point2 = pointSE
                    point3 = pointNE
                    point4 = pointSW
                if self._realCorner ==1: # Real corner: NW
                    point1 = pointNE
                    point2 = pointSW
                    point3 = pointSE
                    point4 = pointNW
                self._objects.append(triObj((point1[0],point1[1]),(point2[0],point2[1]),0,1,None))
                self._objects[-1].setNorthWest(point3[0],point3[1])
                self._objects.append(lineOb((point1[0],point1[1]),(point4[0],point4[1])))
                self._objects.append(lineOb((point2[0],point2[1]),(point1[0],point1[1])))
   
        self._startObjects.append(self._objects[-1])           
         
       
gameObjIndexX = 1
gameObjIndexY = 1
realCorner = 0
slashSame = False
horiMove = [1,0]
vertMove = [0,0]
gen = WorldGeneratorForSecondConvNetworkTest(gameObjIndexX, gameObjIndexY,
                 realCorner, slashSame, horiMove, vertMove)

gen.generate(25,25)
