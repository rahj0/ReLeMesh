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
import sys
import numpy as np
import random
import itertools
import scipy.misc
from abc import abstractmethod
from gameObjects.squareObj import *
from gameObjects.quadObj import *

from worldGenerators.simpleMeshWorldGenerator import *
from environments.AbstractMeshEnv import *

class meshEnv(AbstractMeshEnv):
    def __init__(self,size, seedValue = 0, nLinesX = 3, nLinesY = 3):
        self._nLinesX = nLinesX
        self._nLinesY = nLinesY
        AbstractMeshEnv.__init__(self, False, size, 17)

    def resetConcreteClassSpecifics(self):
        self.objects = []

        obj = simpleMeshWorldGenerator(self._nLinesX , self._nLinesY, 0, 0)
        obj.generate(self._xRes,self._yRes)
        self.objects.extend(obj.getObjects())
        self.startObjects.extend(obj.getStartObjects())
        
        hero = self.createNewHero()
        self.objects.append(hero)        
#        
        self._state = self.renderEnv()  
    def getMaxNumberOfHeros(self):
        return self._nLinesX * self._nLinesY * 2

    def getIdealObjectArea(self,x,y):
        nObjects = self._nLinesX*self._nLinesY
        return (self._yRes+1) * (self._xRes+1) / nObjects

    def createNewHero(self):

        starter = self.startObjects[0]
        self.startObjects.pop(0)
        
        hero = quadObj(starter.getNorthWest(),starter.getNorthEast(),1,0,None,'hero')
        (hero,outOfbound) = self.resizeObjToFitEnv(hero)
    
        self.objects.append(hero)
        return hero
    
