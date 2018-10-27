# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 19:46:09 2018

@author: Rasmus
"""

from tkinter import *
from MeshEnvViewer import *
master = Tk()

env = meshEnv(partial=False,size=25, seedValue=2)
viewer = meshEnvViewer(master,env,20)

mainloop()
