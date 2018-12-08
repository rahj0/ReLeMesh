import unittest
import sys
sys.path.append('src/environments')
sys.path.append('src/gameObjects')
sys.path.append('src/environments/Rendering')
sys.path.append('src/worldGenerators')
import os
cwd = os.getcwd()
print(cwd)
from triMesherEnv import *
class TestTriMesherEnv(unittest.TestCase):

    def test_constructor(self):
        tri = triMesherEnv(20)
        with self.assertRaises(ValueError):
            tri = triMesherEnv(3)
    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
