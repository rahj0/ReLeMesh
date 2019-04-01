import unittest
import sys
sys.path.append('src')
sys.path.append('src/environments')
sys.path.append('src/gameObjects')
sys.path.append('src/environments/Rendering')
sys.path.append('src/worldGenerators')
import os
cwd = os.getcwd()
print(cwd)
from environments.triMesherEnvCpp import *

class TriMesherEnvCppTest(unittest.TestCase):

    def env_tests(self,env):
        nMax = env.getMaxNumberOfHeros()
        for i in range(8):
            (state,reward,done) = env.step(i)
            self.assertFalse(done)
            print(reward)
            self.assertTrue(reward != 0.0)
            test = env.getActionCount()
            test = env.getMaxNumberOfHeros()
            test = env.getNumberOfChannels()
            test = env.getSizeX()
            test = env.getStartScore()
            test = env.getState()
            print(test)

    def test_triMeshEnvCpp(self):
        print("\nStarting test_triMeshEnvCpp")
        env = triMesherEnvCpp(20, sharedLibPath="src/lib/bin/ReLeMeshInterface.so")
         
        try:
            self.env_tests(env)    
        except:
            self.assertTrue(False)

        print("\Finished test_triMeshEnvCpp")

        self.assertFalse(False)
       
    # def test_constructor_tri_smallSize(self):
    #     env = triMesherEnv(7)
    #     with self.assertRaises(ValueError):
    #         tri = triMesherEnv(3)

    # def test_constructor_tri_zeroSize(self):
    #     with self.assertRaises(ValueError):
    #         env = triMesherEnv(0)

    # def test_constructor_tri_negativeSize(self):
    #     with self.assertRaises(ValueError):
    #         env = triMesherEnv(-5)

    # def test_constructor_tri(self):
    #     env = triMesherEnv(20)
    #     self.env_tests(env)
    # def test_constructor_quad(self):
    #     env = meshEnv(20)
    #     self.env_tests(env)


if __name__ == '__main__':
    unittest.main()
