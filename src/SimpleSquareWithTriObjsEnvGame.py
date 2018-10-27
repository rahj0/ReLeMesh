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
      
sizeOfFrame = 23
   
cornerMovement = [[0,0],[0,0],[0,0],[0,0]]
solidTipMovement = (2,0)
solidPosition = 0
gameObjPosIncrement = 2
gapFilled = True
gameObjTipMovementLength = 2
# gameObj tip direction - int (0-4) 0: No MoveMent 1: South 2: West, 3: North, 4: East
gameObjTipDirection = 1 #

stepsForCornersSWx = [0] #= [0,3]
stepsForCornersNWx = [0] #= [0,3]
stepsForCornersNEx = [0] #= [0,3]
stepsForCornersSEx = [0] #= [0,3]
stepsForCornersSWy = [0] #= [0,3]
stepsForCornersNWy = [0] #= [0,3]
stepsForCornersNEy = [0] #= [0,3]
stepsForCornersSEy = [0] #= [0,3]
stepsForTipMovementsX = [-3,3] #= [0,3]
stepsForTipMovementsY = [-3,3] #= [0,3]
solidPositions = [0] #= [0,1,2,3]
gameObjPosIncrements = [1,2,3] #= [1,2,3]
#cornerMovements = [stepsForTipMovementsX,stepsForTipMovementsY,stepsForTipMovementsX,stepsForTipMovementsY,stepsForTipMovementsX,stepsForTipMovementsY,stepsForTipMovementsX,stepsForTipMovementsY]
#myCornerList = list(itertools.product(*cornerMovements))
#print(myCornerList)
gapFilled = [False,True] # = [False, True] 
gameObjTipMovementLengths = [1,2,4] # = [1,2]
gameObjTipDirections = [0,1,2,3,4] # = [0,1,2,3,4] 
a = [stepsForCornersSWx,stepsForCornersSWy,stepsForCornersNWx,stepsForCornersNWy,stepsForCornersNEx,stepsForCornersNEy,stepsForCornersSEx,stepsForCornersSEy,stepsForTipMovementsX,stepsForTipMovementsY,solidPositions,gameObjPosIncrements,gapFilled,gameObjTipMovementLengths,gameObjTipDirections]
settingsList = list(itertools.product(*a))
print(len(settingsList))
print(len(settingsList[1]))

showGUI = False
showGUI = True

yLabels = []
pixels = []
iSample = 0
settingsList = [settingsList[0]]
for settings in settingsList:
    cornerMovement = [[settings[0],settings[1]],[settings[2],settings[3]],[settings[4],settings[5]],[settings[6],settings[7]]]
    solidTipMovement = (settings[8],settings[9])
    solidPosition = settings[10]
    gameObjPosIncrement = settings[11]
    gapFilled = settings[12]
    gameObjTipMovementLength = settings[13]
    # gameObj tip direction - int (0-4) 0: No MoveMent 1: South 2: West, 3: North, 4: East
    gameObjTipDirection = settings[14] #
    
    if(gameObjTipDirection > 0 or (gameObjTipDirection == 0 and gameObjTipMovementLength == gameObjTipMovementLengths[0])):
#        print(settings)
        iSample += 1
        if(iSample % 1000==0):
            print(iSample)
        yLabels.append(gameObjTipDirection)

        env = SimpleSquareWithTriObjsEnv(False,sizeOfFrame, 
             cornerMovement, solidTipMovement,
             solidPosition, gameObjPosIncrement, gapFilled,
             gameObjTipMovementLength, gameObjTipDirection,
             seedValue=2)

        env.renderEnv()
        pixels.append(env.getState())
        if(showGUI):
            master = Tk()
            viewer = meshEnvViewer(master,env,20)
            master.state('zoomed')
            mainloop()
            
print(len(settingsList))
print(len(settingsList[0]))

npLabels = np.array(yLabels, dtype=np.int32)
npPixels = np.array(pixels, dtype=np.float32)[:,:,:,1:]

print(npLabels.shape)
print(npPixels.shape)

extension = "_" + str(sizeOfFrame+2)+ "x"+ str(sizeOfFrame+2)+"_" +str(npLabels.shape[0]) + ".dat"

#np.savetxt('labels' + extension, npLabels, fmt='%d')
fh1 = open('labels' + extension, "bw")
npLabels.tofile(fh1)

fh2 = open('pixels' + extension, "bw")
npPixels.tofile(fh2)
fh2.close()
#
#fh2 = open('pixels' + extension, "rb")
#xx2 = np.fromfile(fh2)
#
#xx3 = xx2.reshape((104,28,28,3))

#np.savetxt('pixels' + extension, npPixels)

npPixels1 = npPixels[0,:,:,:]