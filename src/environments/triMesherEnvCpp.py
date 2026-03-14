"""C++ backend wrapper for the ReLeMesh triangular mesh environment.

Delegates all environment logic to the compiled ReLeMeshInterface.so shared
library via ctypes.  The Python layer handles only buffer management and the
CHW→HWC state transposition required by the training pipeline.

C++ state layout:  [nChannels, sizeX, sizeY]  (channel-first, written by step())
Python pipeline:   [sizeX, sizeY, nChannels]  (HWC, consumed by processState())
"""

from ctypes import CDLL, c_int, c_float, c_bool, c_void_p, POINTER, byref
import numpy as np
import os

_DEFAULT_LIB = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    '../../../ReLeMeshCppv2/bin/ReLeMeshInterface.so'
))


class triMesherEnvCpp:
    """Thin Python wrapper around the C++ ReLeMesh environment.

    Implements the same public interface as triMesherEnv so it can be used
    as a drop-in replacement in the training script (without PartialViewEnv).
    """

    def __init__(self, size, nLinesX=3, nLinesY=3, lib_path=None):
        if lib_path is None:
            lib_path = _DEFAULT_LIB
        if not os.path.isfile(lib_path):
            raise FileNotFoundError(
                f'C++ library not found at: {lib_path}\n'
                f'Build with: cd ReLeMeshCppv2 && make bin/ReLeMeshInterface.so'
            )

        lib = CDLL(lib_path)
        lib.createTriMeshEnvironment.restype  = c_void_p
        lib.createTriMeshEnvironment.argtypes = [c_int, c_int]
        lib.reset.restype   = None
        lib.reset.argtypes  = [c_void_p]
        lib.step.restype    = None
        lib.step.argtypes   = [c_void_p, c_int, POINTER(c_float), POINTER(c_bool), POINTER(c_float)]
        lib.getState.restype   = None
        lib.getState.argtypes  = [c_void_p, POINTER(c_float)]
        lib.getActionCount.restype    = c_int
        lib.getActionCount.argtypes   = [c_void_p]
        lib.getMaxNumberOfHeros.restype  = c_int
        lib.getMaxNumberOfHeros.argtypes = [c_void_p, POINTER(c_float)]
        lib.getChannelCount.restype   = c_int
        lib.getChannelCount.argtypes  = [c_void_p]
        lib.getSizeX.restype  = c_int
        lib.getSizeX.argtypes = [c_void_p]
        lib.getSizeY.restype  = c_int
        lib.getSizeY.argtypes = [c_void_p]
        lib.deleteEnvironment.restype  = None
        lib.deleteEnvironment.argtypes = [c_void_p]

        self._lib = lib
        self._ptr = lib.createTriMeshEnvironment(size, size)
        self._size = size
        self._nChannels = lib.getChannelCount(self._ptr)
        self._buf    = (c_float * (size * size * self._nChannels))()
        self._reward = c_float(0.0)
        self._done   = c_bool(False)

        # Stats mirroring AbstractMeshEnv interface.
        self._total_reward = 0.0
        self._total_steps  = 0
        self._actions: list = []

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def reset(self):
        self._lib.reset(self._ptr)
        self._total_reward = 0.0
        self._total_steps  = 0
        self._actions.clear()
        self._lib.getState(self._ptr, self._buf)
        return self._buf_to_hwc()

    def step(self, action):
        self._lib.step(self._ptr, int(action),
                       byref(self._reward), byref(self._done), self._buf)
        state  = self._buf_to_hwc()
        reward = float(self._reward.value)
        done   = bool(self._done.value)
        self._total_reward += reward
        self._total_steps  += 1
        self._actions.append(action)
        return state, reward, done

    def getState(self):
        self._lib.getState(self._ptr, self._buf)
        return self._buf_to_hwc()

    # ------------------------------------------------------------------
    # Environment metadata
    # ------------------------------------------------------------------

    def getActionCount(self):
        # C++ getActionCount() returns action *history* size, not available actions.
        # The environment supports exactly 9 actions (0-7: move corners, 8: new hero).
        return 9

    def getNumberOfChannels(self):
        return self._nChannels

    def getSizeX(self):
        return self._size

    def getSizeY(self):
        return self._size

    def getMaxNumberOfHeros(self):
        # data arg exists in C++ signature but is unused; pass NULL.
        return int(self._lib.getMaxNumberOfHeros(self._ptr, None))

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def printStats(self):
        print(f'Steps: {self._total_steps}  Reward: {self._total_reward:.4f}  '
              f'Actions: {self._actions[-10:]}')

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _buf_to_hwc(self):
        """Convert the C++ CHW flat buffer to a numpy HWC array."""
        arr = np.frombuffer(self._buf, dtype=np.float32).copy()
        arr = arr.reshape(self._nChannels, self._size, self._size)
        return arr.transpose(1, 2, 0)   # [C, X, Y] → [X, Y, C]

    def __del__(self):
        if getattr(self, '_lib', None) and getattr(self, '_ptr', None):
            self._lib.deleteEnvironment(self._ptr)
            self._ptr = None
