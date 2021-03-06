from ctypes import *
import os
from environments.AbstractMeshEnv import *

class triMesherEnvCpp(AbstractMeshEnv):

    def __init__(self,size, seedValue = 0, nLinesY = 3, nLinesX = 3, sharedLibPath = "lib/bin/ReLeMeshInterface.so"):
        self._nLinesX = nLinesX
        self._nLinesY = nLinesY
        actions = 9
        AbstractMeshEnv.__init__(self, False, size, actions, seedValue)
        self.setWorldGenerator(simpleMeshWorldGenerator(nLinesX,nLinesY, 0, 0))
        print(os.system("ls"))
        exists = os.path.isfile(sharedLibPath)
        if not exists:
            print("Shared object not found!")
            print("Expected path: ", sharedLibPath)
            exit()
        self._reLeMeshLib = CDLL(sharedLibPath)


        self._reLeMeshLib.createTriMeshEnvironment.restype = c_void_p
        self._reLeMeshLib.deleteEnvironment.restype = None
        self._reLeMeshLib.step.restype = None
        self._reLeMeshLib.getSizeX.restype = c_int
        self._reLeMeshLib.getSizeY.restype = c_int
        self._reLeMeshLib.getChannelCount.restype = c_int

        self._reLeMeshLib.step.argtypes = [c_void_p,c_int,POINTER(c_float)]

        self._testTriEnv = self._reLeMeshLib.createTriMeshEnvironment(size,size)
        xSize = self._reLeMeshLib.getSizeX(self._testTriEnv)
        ySize = self._reLeMeshLib.getSizeY(self._testTriEnv)
        if size != xSize:
            print("Error creating c++ triMesherEnv: Size does match python size")
        if size != ySize:
            print("Error creating c++ triMesherEnv: Size does match python size")
        nChannels = self._reLeMeshLib.getChannelCount(self._testTriEnv)
        data = (c_float*(ySize*xSize*nChannels))()
        self._reLeMeshLib.step(self._testTriEnv,0,data)
        index = 0
        for i in range(nChannels):
            for j in range(xSize):
                myString = "E  "
                for k in range(ySize):
                    myString += str(int(data[index])) + " "
                    index += 1
                print(myString)
            print("\n\n")
        # TODO Clean up this and move to unit Tester

    def getMaxNumberOfHeros(self):
        return self._nLinesX * self._nLinesY/2 # TODO access through cpp lib  

    def createNewHero(self):
        print("createNewHero")

    def reset(self):
        pass # TODO reset using cpp

    def step(self,action):
        nChannels = self._reLeMeshLib.getChannelCount(self._testTriEnv)
        data = (c_float*(self.getSizeX()*self.getSizeY()*nChannels))()
        self._reLeMeshLib.step(self._testTriEnv,int(action),data)
        state = np.zeros([self._yRes,self._xRes,2])
        index = 0
        for i in range(nChannels):
            for j in range(self.getSizeX()):
                for k in range(self.getSizeY()):
                    state[j,k,i] = data[index]
                    index += 1
        reward = 0.5
        done = False
        return self.getState(),reward,done
    
    def getState(self):
        nChannels = self._reLeMeshLib.getChannelCount(self._testTriEnv)
        print(nChannels)
        print(self.getSizeX())
        print(self.getSizeY())
        data = (c_float*(self.getSizeX()*self.getSizeY()*nChannels))()
        print("Created Memory")
        self._reLeMeshLib.getState(self._testTriEnv,data)
        print("Got State")
        index = 0

        state = np.zeros([self._yRes,self._xRes,2])
        for i in range(nChannels):
            for j in range(self.getSizeX()):
                for k in range(self.getSizeY()):
                    state[j,k,i] = data[index]
                    index += 1
        return state
    def getActionCount(self):
        return 3 #TODO
    def getMaxNumberOfHeros(self):
        return 1000 #TODO