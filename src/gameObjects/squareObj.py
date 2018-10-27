# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 23:18:37 2018

@author: Rasmus
"""
from gameObj import *

class squareObj(gameOb):
    def __init__(self,coord,size,intensity,channel,reward,name):
        southWest = (coord[0],coord[1])
        southEast = (coord[0] + size - 1,coord[1]) # replace this
        northWest = (coord[0]  , coord[1] + size -1) # replace this
        northEast = (coord[0] + size -1,coord[1] + size  -1) # replace this
        gameOb.__init__(self,southWest,southEast,northWest,northEast,intensity,channel,reward,name)
