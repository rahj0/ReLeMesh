from environments.AbstractMeshEnv import *

class PartialViewEnv(AbstractMeshEnv): 
    def __init__(self, environment, viewSize=15 , seedValue = 0, cornerMatchBonus = 30):
        self._fullEnv = environment
        AbstractMeshEnv.__init__(self, False, viewSize, environment.getActionCount(), seedValue, cornerMatchBonus)
        x,y = self._fullEnv.getHero().getCenterPoint()
        self._centerOfFocus = (x,y)
        self._fullEnv.setCenterOfFocus(self._centerOfFocus)
    def getFullEnvState(self):
        return self._fullEnv.getState()
        
    def reset(self):
        self.resetVariables()
        state = self._fullEnv.reset()
        x,y = self._fullEnv.getHero().getCenterPoint() # TODO Cleanup duplicate
        self._centerOfFocus = (x,y)
        self._fullEnv.setCenterOfFocus(self._centerOfFocus)
        return self.cutState(state)

    def resetConcreteClassSpecifics(self):
        pass

    def renderEnv(self):
        return self._fullEnv.renderEnv()

    def getIdealObjectArea(self,x,y):
        return self._fullEnv.getIdealObjectArea(x,y)

    def getState(self):
        state = self._fullEnv.getState()
        print(state.shape)
        return self.cutState(state)

    def calculateRangeFromCenterPoint(self, centerValue, frameSize, fullEnvSize):
        
        lowerValue = centerValue-int(frameSize*0.5)-1
        if lowerValue < 0:
            lowerValue = 0
        elif lowerValue+frameSize > fullEnvSize:
            diff = lowerValue+frameSize - fullEnvSize
            lowerValue -= diff
        upperValue = lowerValue + frameSize

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

    def cutState(self, state):
        xMax = self._fullEnv.getSizeX()
        yMax = self._fullEnv.getSizeY()
        xC,yC  = self._fullEnv.getHero().getMovingCenterPoint()
        # print("Center of focus", xC,yC)
        (xWest,xEast) = self.calculateRangeFromCenterPoint(xC,self.getSizeX(),xMax)
        (ySouth,yNorth) = self.calculateRangeFromCenterPoint(yC,self.getSizeY(),yMax)
        # print(xWest,xEast)
        # print(ySouth,yNorth)
        return state[xWest:xEast,ySouth:yNorth,:]

    def getMaxNumberOfHeros(self):
        pass

    def step(self,action):
        (_,_,_,_,newHero) = self._fullEnv.convertStepInput(action)
        (state,reward,done) = self._fullEnv.step(action)
        
        (x,y) = self._fullEnv.getHero().getCenterPoint()
        if (newHero):
            self._fullEnv.setCenterOfFocus(self._centerOfFocus)
            self.updateCenterOfFocus(x,y)
        newState = self.cutState(state)
        self._totalReward += reward
        self._totalSteps += 1
        return (newState,reward,done) 

    def createNewHero(self):
        raise