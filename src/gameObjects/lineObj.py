# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 23:17:59 2018

@author: Rasmus
"""
from squareObj import *

class lineOb(squareObj):
    def __init__(self,coord1,coord2):
        channel = 1
        intensity = 1
        reward = None
        name = "line"
        gameOb.__init__(self,coord1,coord2,coord1,coord2,intensity,channel,reward,name)
    def moveEast(self, xChange, yChange):
         self.changeNorthEast(self,xChange, yChange)
         self.changeNorthEast(self,xChange, yChange)
         
    def moveWest(self, xChange, yChange):
         self.changeNorthWest(self,xChange, yChange)
         self.changeNorthWest(self,xChange, yChange)
