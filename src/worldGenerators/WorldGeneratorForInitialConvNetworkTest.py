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

class WorldGeneratorForInitialConvNetworkTest(AbstractMeshWorldGenerator):
    def __init__(self,cornerMovement, solidTipMovement,
                 solidPosition, gameObjPosIncrement, gapFilled):
        self._cornerMovement = cornerMovement
        self._solidTipMovement = solidTipMovement
        self._solidPosition = solidPosition
        self._gameObjPosIncrement = gameObjPosIncrement
        self._gapFilled = gapFilled
        if(self._gameObjPosIncrement == 0 ):
            raise
        # cornerMovement - 4x2 vector: ((SWxPlus,SWyPlus),(SExPlus,SEyPlus),(NWxPlus,NWyPlus),(NExPlus,NEyPlus))
        # solidTipMovement -  vector[2] (tipXmovement,tipYmovement)
        # solidPosition - int (0-3) 0: South 1: West, 2: North, 3: East
        # gameObjPosIncrement wrt solid position - int (1-3) 
        # gapFilled - bool
        # gameObj tip movement length int (0-)

        
        # label will be the inverse of gameObj tip direction 
        # e.g.   0->2     2->0     1->3      3->1
        deviationProbability = 0.5
        AbstractMeshWorldGenerator.__init__(self, deviationProbability)
        
    def generate(self, worldSizeX, worldSizeY):
        minX = 0
        minY = 0
        maxX = worldSizeX - 1
        maxY = worldSizeY - 1
        
        # TODO: Add checks that worldSizeX is bigger than _maxDeviations for x and y
        
        baseXLineLength = worldSizeX
        baseYLineLength = worldSizeY

        lastX = minX
        lastY = minY
        
        self.generateBorder(minX, minY, maxX, maxY, self._cornerMovement)
        
        self._objects.append(triObj(self._objects[self._solidPosition].getSouthWest(),self._objects[self._solidPosition].getSouthEast(),1,1,None))
        self._objects[-1].changeNorthEast(self._solidTipMovement[0], self._solidTipMovement[1])
            
        startObjectIndex = self._solidPosition+self._gameObjPosIncrement
        if(startObjectIndex > 3):
            startObjectIndex -= 3
            
            
        self._startObjects.append(self._objects[startObjectIndex]) 
        
        
        if self._gapFilled:
            gaps = self._gameObjPosIncrement - 1
            increment = 1
            solidNorthX = self._objects[-1].getNorthWest()[0]
            solidNorthY = self._objects[-1].getNorthWest()[1]
#            print(solidNorthX,solidNorthY)
            while(gaps > 0):
                self._objects.append(triObj(self._objects[self._solidPosition+increment].getSouthWest(),self._objects[self._solidPosition+increment].getSouthEast(),1,1,None))
                
                self._objects[-1].setNorthEast(solidNorthX,solidNorthY)
                gaps -=  1
                increment += 1