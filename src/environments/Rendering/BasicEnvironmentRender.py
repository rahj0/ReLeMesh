
import numpy as np
from gameObjects.squareObj import *
from gameObjects.triObj import *

class BasicEnvironmentRender():
    def __init__(self, xRes, yRes ):
        self._xRes = xRes
        self._yRes = yRes

    def calculateXYmoveUnitVector(self, point1x, point1y, point2x, point2y):
        xDiff = point2x-point1x
        yDiff = point2y-point1y  
        if (abs(xDiff) > abs(yDiff)):
            xMove = 0
            if xDiff != 0:
                yMove = -int(xDiff/abs(xDiff))
            else:
                yMove = 0
        else:
            if yDiff != 0:
                xMove = int(yDiff/abs(yDiff))
            else:
                xMove = 0
            yMove = 0
            
        return (xMove,yMove)
                
    @staticmethod
    def valueLeft(index,minValue,maxValue,maxIndex):
        difference = maxValue - minValue
        if difference < 0:
            direction = -1
        else:
            direction = 1
        
        maxIndexOdd = ((maxIndex+1) % 2 != 0 )
        differenceOdd = ((difference+1) % 2 != 0 )       
        midSectionIndex = int(maxIndex/2)
        valueSectionSize = int(abs(difference)/2)
        value = -1
        if (index == midSectionIndex): #Middsection
            if(maxIndexOdd and differenceOdd):
                value = minValue+valueSectionSize*direction
            elif(maxIndexOdd):
                value = minValue+valueSectionSize*direction
                return [value,value+direction]
            else:
                value = minValue+valueSectionSize*direction 
        elif (index < midSectionIndex):
            if(index < valueSectionSize ):
                value = minValue + index*direction
            else:
                value = minValue + valueSectionSize*direction
        elif (index >= midSectionIndex):
            if(index > maxIndex - valueSectionSize ):
                value = maxValue - (maxIndex - index)*direction
            else:
                value = maxValue - valueSectionSize*direction
            pass

        return [value]
        
    @staticmethod
    def computePixelsFromLine(x1,y1,x2,y2):
       #print("computePixelsFromLine")
        lengthX = x2-x1
        lengthY = y2-y1
       #print("lengthX",lengthX)
       #print("lengthY",lengthY)
        lengthMax = max(abs(lengthX),abs(lengthY))
       #print("max ", lengthMax)
        xOdd = (lengthX % 2 != 0 )
        yOdd = (lengthY % 2 != 0 )
        maxOdd = (lengthMax % 2 != 0 )
        
        if (maxOdd):
            firstSection = int(lengthMax/2)
        else:
            firstSection = int((lengthMax-1)/2)
#        for i = 0:
        pixels = [[x1,y1]]
        
        for i in range(1,lengthMax):
            x = BasicEnvironmentRender.valueLeft(i,x1,x2,lengthMax)
            y = BasicEnvironmentRender.valueLeft(i,y1,y2,lengthMax)

            pixels.append([x[0],y[0]])
            if(len(x) == 2 and len(y) == 1):
                pixels.append([x[1],y[0]])
            elif(len(x) == 1 and len(y) == 2):
                pixels.append([x[0],y[1]])
            elif(len(x) == 2 and len(y) == 2):
                pixels.append([x[1],y[1]])
            
        pixels.append([x2,y2])

        return pixels

    def renderEnv(self, objects):
        bufferX = 0
        bufferY = 0
        a = np.zeros([self._yRes+2,self._xRes+2,2])
        maxIndexX = self._yRes+1
        maxIndexY = self._xRes+1

        for item in objects:
            item.intensity = 0.75
            
            (southWestCornerX,southWestCornerY) = (item.getSouthWest()[0] + bufferX,item.getSouthWest()[1] + bufferY)
            (southEastCornerX,southEastCornerY) = (item.getSouthEast()[0] + bufferX,item.getSouthEast()[1] + bufferY)

            (northWestCornerX,northWestCornerY) = item.getNorthWest()
            (northEastCornerX,northEastCornerY) = item.getNorthEast()
            
            pixelsSouth = self.computePixelsFromLine(southEastCornerX,southEastCornerY,southWestCornerX,southWestCornerY)
            pixelsWest = self.computePixelsFromLine(southWestCornerX,southWestCornerY,northWestCornerX,northWestCornerY)
            pixelsNorth = self.computePixelsFromLine(northEastCornerX,northEastCornerY,northWestCornerX,northWestCornerY)
            pixelsEast = self.computePixelsFromLine(southEastCornerX,southEastCornerY,northEastCornerX,northEastCornerY)
            
            if item.getName() == "hero":
                wrongMove = False
                if [northWestCornerX,northWestCornerY] in pixelsWest[:-1]:
                    wrongMove = True
                if [northWestCornerX,northWestCornerY] in pixelsEast[:-1]:
                    wrongMove = True
                if [northEastCornerX,northEastCornerY] in pixelsWest[:-1]:
                    wrongMove = True
                if [northEastCornerX,northEastCornerY] in pixelsEast[:-1]:
                    wrongMove = True
                if wrongMove:
                    return [False, 0]
                
            for pixel in pixelsWest:
                a[pixel[0],pixel[1],item.channel] = item.intensity

            for pixel in pixelsNorth:
                a[pixel[0],pixel[1],item.channel] = item.intensity

            for pixel in pixelsEast:
                a[pixel[0],pixel[1],item.channel] = item.intensity
                            
            for pixel in pixelsSouth:
                a[pixel[0],pixel[1],item.channel] = item.intensity

            if item.channel == 1: 
                a[pixelsWest[0][0],pixelsWest[0][1],item.channel] = 1
                a[pixelsEast[0][0],pixelsEast[0][1],item.channel] = 1
            
            
            a[pixelsWest[-1][0],pixelsWest[-1][1],item.channel] = 1
            a[pixelsEast[-1][0],pixelsEast[-1][1],item.channel] = 1
                        
            # Inside square
            (xMove,yMove) = self.calculateXYmoveUnitVector(southWestCornerX,southWestCornerY,
            southEastCornerX,southEastCornerY)  
            (xMove,yMove) = self.calculateXYmoveUnitVector(southWestCornerX,southWestCornerY,
            northWestCornerX,northWestCornerY) 
            if abs(xMove)+abs(yMove) > 0:
                for i in range(len(pixelsWest))[1:-1]:
                    move = True
                    j = 0
    
                    while(move and j < 100):
    
                        x = pixelsWest[i][0]+xMove*j
                        y = pixelsWest[i][1]+yMove*j
                        if x < 0 or y < 0 or y > maxIndexY or x > maxIndexY:
                            move = False
                            continue                        
                        if [x,y] in pixelsNorth:
                            move = False
                            continue
                        if [x,y] in pixelsSouth:
                            move = False
                            continue
                        if [x,y] in pixelsEast:
                            move = False
                            continue
    
                        if (a[x,y,item.channel] == 0):
                            a[x,y,item.channel] = 0.5
                        j +=1 
                        
            (xMove,yMove) = self.calculateXYmoveUnitVector(southEastCornerX,southEastCornerY,
            northEastCornerX,northEastCornerY) 
            #yMove *= -1
            #xMove *= -1
            if abs(xMove)+abs(yMove) > 0:
                for i in range(len(pixelsEast))[1:-1]:
                    move = True
                    j = 0
                    
                    while(move and j < 100):
                        x = pixelsEast[i][0]-xMove*j
                        y = pixelsEast[i][1]-yMove*j
                        if x < 0 or y < 0 or y > maxIndexY or x > maxIndexY:
                            move = False
                            continue    
                        if [x,y] in pixelsNorth:
                            move = False
                            continue
                        if [x,y] in pixelsSouth:
                            move = False
                            continue
                        if [x,y] in pixelsWest:
                            move = False
                            continue
                        if (a[x,y,item.channel] == 0):
                            a[x,y,item.channel] = 0.5
                        j +=1 
        b = a[:,:,0]
        c = a[:,:,1]

        return [True,np.stack([b,c],axis=2)]
