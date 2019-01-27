from environments.AbstractMeshEnv import *

class AbstractPartialViewEnv(AbstractMeshEnv): 
    def __init__(self, environment, viewSize=15 , seedValue = 0, cornerMatchBonus = 30):
        self._fullEnv = environment
        AbstractMeshEnv.__init__(self, False, viewSize, environment.getActions(), seedValue, cornerMatchBonus)
        self._centerOfFocus = (4,0)
        self._fullEnv.setCenterOfFocus(self._centerOfFocus)

    def reset(self):
        return self._fullEnv.reset()

    def resetConcreteClassSpecifics(self):
        pass

    def renderEnv(self):
        return self._fullEnv.renderEnv()

    def getIdealObjectArea(self,x,y):
        return self._fullEnv.getIdealObjectArea(x,y)

    def getState(self):
        state = self._fullEnv.getState()
        print(state.shape)
        return state

    def calculateRangeFromCenterPoint(self, centerValue, frameSize, fullEnvSize):
        
        lowerValue = centerValue-int(frameSize*0.5)-1
        if lowerValue < 0:
            lowerValue = 0
        elif lowerValue+frameSize+1 > fullEnvSize:
            diff = lowerValue+frameSize+1 - fullEnvSize
            lowerValue -= diff
        upperValue = lowerValue + frameSize+2

        return (lowerValue, upperValue)
    # def updateStarterObjectList(self):
    #     xC,yC = self._centerOfFocus
    #     self._fullEnv.pushToFrontStarterObjectNearestToPoint(xC,yC)

    def updateCenterOfFocus(self,x,y):
        xC,yC = self._centerOfFocus
        updateRatio = 0.7
        xC = int(xC*(1.-updateRatio) + x * updateRatio)
        yC = int(yC*(1.-updateRatio) + y * updateRatio)
        self._centerOfFocus = (xC,yC)

    def step(self,action):
        (_,_,_,_,newHero) = self._fullEnv.convertStepInput(action)
        (state,reward,done) = self._fullEnv.step(action)
        xMax = self._fullEnv.getSizeX()+1
        yMax = self._fullEnv.getSizeY()+1
        
        (x,y) = self._fullEnv.getHero().getCenterPoint()
        if (newHero):
            self._fullEnv.setCenterOfFocus(self._centerOfFocus)
            self.updateCenterOfFocus(x,y)
        (xWest,xEast) = self.calculateRangeFromCenterPoint(x,self.getSizeX(),xMax)
        (ySouth,yNorth) = self.calculateRangeFromCenterPoint(y,self.getSizeY(),yMax)

        newState = state[xWest:xEast,ySouth:yNorth,:]
        return (newState,reward,done) 

    def createNewHero(self):
        raise