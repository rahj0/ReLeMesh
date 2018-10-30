# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 21:21:21 2018

@author: Rasmus
"""

from tkinter import *
from SimpleSquareWithTriObjsEnv import *
from SimpleSquareWithTriObjsEnvSecond import *
from MeshEnvViewer import *
import itertools
from tempfile import TemporaryFile
      
sizeOfFrame = 35

gameObjIndexXs = [0,1,2,3]
gameObjIndexYs = [0,1,2,3]
realCorners = [0,1,2,3]#[0,1,2,3]
slashForward = [False,True]
horiMoveXs = [-1,0,1]
horiMoveYs = [-1,0,1]
vertMoveXs = [-1,0,1]
vertMoveYs = [-1,0,1]
gameObjTipDirections = [0,1,2,3,4] # = [0,1,2,3,4] 
a = [gameObjIndexXs,gameObjIndexYs,realCorners,slashForward,horiMoveXs,horiMoveYs,vertMoveXs,vertMoveYs,gameObjTipDirections]
settingsList = list(itertools.product(*a))
print(len(settingsList))
print(len(settingsList[1]))

showGUI = False
#showGUI = True

yLabels = []
pixels = []
iSample = 0
settingsList = settingsList
for settings in settingsList:
    gameObjIndexX = settings[0]
    gameObjIndexY = settings[1]
    realCorner = settings[2]
    slashForward =  settings[3]
    horiMove = [ settings[4], settings[5]]
    vertMove = [ settings[6], settings[7]]
    gameObjTipDirection = settings[8] #
    
    if(1):
#        print(settings)
        iSample += 1
        if(iSample % 1000==0):
            print(iSample)
        yLabels.append(gameObjTipDirection)
        env = SimpleSquareWithTriObjsEnvSecond(False,sizeOfFrame, 
             gameObjIndexX, gameObjIndexY,
                 realCorner, slashForward, horiMove,
                 vertMove, gameObjTipDirection,
             seedValue=2)
        env.renderEnv()
        pixels.append(env.getState())
        if(showGUI):
            master = Tk()
            viewer = meshEnvViewer(master,env,20)
            master.state('zoomed')
            mainloop()
            
#%%%
if 1:          
    print(len(settingsList))
    print(len(settingsList[0]))
    
    npLabels = np.array(yLabels, dtype=np.int32)
    npPixels = np.array(pixels, dtype=np.float32)[:,:,:,1:]
    
    print(npLabels.shape)
    print(npPixels.shape)
    
    extension = "_" + str(sizeOfFrame+2)+ "x"+ str(sizeOfFrame+2)+"_" +str(npLabels.shape[0]) + ".dat"
    
    #np.savetxt('labels' + extension, npLabels, fmt='%d')
    fh1 = open('..\data\Problem2_labels' + extension, "bw")
    npLabels.tofile(fh1)
    
    fh2 = open('..\data\Problem2_pixels' + extension, "bw")
    npPixels.tofile(fh2)
    fh2.close()
    #
    #fh2 = open('pixels' + extension, "rb")
    #xx2 = np.fromfile(fh2)
    #
    #xx3 = xx2.reshape((104,28,28,3))
    
    #np.savetxt('pixels' + extension, npPixels)
    
    npPixels1 = npPixels[0,:,:,:]
