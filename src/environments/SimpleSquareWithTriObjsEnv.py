# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 21:22:09 2018

@author: Rasmus
"""

# -*- coding: utf-8 -*-
"""
Created on Thu May 24 22:40:03 2018

@author: Rasmus
"""

import numpy as np
import random
import itertools
import scipy.misc
from abc import abstractmethod
from squareObj import *
from triObj import *

from WorldGeneratorForInitialConvNetworkTest import *
from WorldGeneratorForSecondConvNetworkTest import *
from AbstractMeshEnv import *

class SimpleSquareWithTriObjsEnv(AbstractMeshEnv):
    def __init__(self,partial,size,
                 cornerMovement, solidTipMovement,
                 solidPosition, gameObjPosIncrement, gapFilled,
                 gameObjTipMovementLength, gameObjTipDirection,
                 seedValue = 0):
        self._cornerMovement = cornerMovement
        self._solidTipMovement = solidTipMovement
        self._solidPosition = solidPosition
        self._gameObjPosIncrement = gameObjPosIncrement
        self._gapFilled = gapFilled
        self._gameObjTipMovementLength = gameObjTipMovementLength
        self._gameObjTipDirection = gameObjTipDirection
        
        AbstractMeshEnv.__init__(self, partial, size, seedValue)

    def createNewHero(self):

        starter = self.startObjects[0]
        self.startObjects.pop(0)
        
        hero = triObj(starter.getNorthWest(),starter.getNorthEast(),1,2,None,'hero')
        (hero,outOfbound) = self.resizeObjToFitEnv(hero)
    
        self.objects.append(hero)
        self._nHeros += 1
        return hero
    def calculateTipMovementVector(self,gameObjTipDirection,gameObjTipMovementLength):
        # gameObj tip direction - int (0-4) 0: No MoveMent 1: South 2: West, 3: North, 4: East
        gameObjTipMoveX = 0
        gameObjTipMoveY = 0
        if(gameObjTipDirection == 1):
            gameObjTipMoveY = -1
        elif(gameObjTipDirection == 2):
            gameObjTipMoveX = -1
        elif(gameObjTipDirection == 3):
            gameObjTipMoveY = 1
        elif(gameObjTipDirection == 4):
            gameObjTipMoveX = 1
        gameObjTipMoveX *= gameObjTipMovementLength
        gameObjTipMoveY *= gameObjTipMovementLength

        return (gameObjTipMoveX,gameObjTipMoveY)
    
    def reset(self):
        self.objects = []
        
        xLines = 1
        yLines = 1

        if 0:
            obj = WorldGeneratorForInitialConvNetworkTest(self._cornerMovement, self._solidTipMovement,self._solidPosition, self._gameObjPosIncrement, self._gapFilled)
        else:
            gameObjIndexX = 1
            gameObjIndexY = 0
            realCorner = 3
            slashSame = False
            horiMove = [1,0]
            vertMove = [0,-1]
            obj = WorldGeneratorForSecondConvNetworkTest(gameObjIndexX, gameObjIndexY,
                             realCorner, slashSame, horiMove, vertMove)

        obj.generate(self._xRes+2,self._yRes+2)

        self.objects.extend(obj.getObjects())
        self.startObjects.extend(obj.getStartObjects())
        
        hero = self.createNewHero()
#        hero.setNorthEast(self.objects[-2].getNorthWest()[0], self.objects[-2].getNorthWest()[1])
        heroMoveVector = self.calculateTipMovementVector(self._gameObjTipDirection,self._gameObjTipMovementLength)
        hero.changeNorthEast(heroMoveVector[0],heroMoveVector[1])
#        print(self.objects[-1].getNorthWest()[0])  
        self._state = self.renderEnv()  