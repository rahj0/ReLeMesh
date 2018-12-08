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
sys.path.append('gameObjects')
sys.path.append('worldGenerators')
import numpy as np
import random
import itertools
import scipy.misc
from abc import abstractmethod
from squareObj import *
from quadObj import *

from simpleMeshWorldGenerator import *
from AbstractMeshEnv import *

class meshEnv(AbstractMeshEnv):
    def __init__(self,size, seedValue = 0):
        AbstractMeshEnv.__init__(self, False, size, seedValue)
        
    def resetConcreteClassSpecifics(self):
        self.objects = []
        
        xLines = 3
        yLines = 3

        obj = simpleMeshWorldGenerator(xLines, yLines, 2, 2)
        obj.generate(self._xRes+2,self._yRes+2)
        self.objects.extend(obj.getObjects())
        self.startObjects.extend(obj.getStartObjects())
        
        hero = self.createNewHero()
        self.objects.append(hero)        
#        
        self._state = self.renderEnv()  
        
    def createNewHero(self):

        starter = self.startObjects[0]
        self.startObjects.pop(0)
        
        hero = quadObj(starter.getNorthWest(),starter.getNorthEast(),1,2,None,'hero')
        (hero,outOfbound) = self.resizeObjToFitEnv(hero)
    
        self.objects.append(hero)
        self._nHeros += 1
        return hero
    
