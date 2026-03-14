"""
Benchmark: Python environment vs C++ environment (via ctypes).

Measures env.step() throughput for both implementations across three
grid sizes.  The C++ timings are split into two cases:
  - raw:      just the ctypes step call (C++ computation only)
  - +extract: step call + copying the state float buffer into a numpy array
              (what a training loop actually does)

Run from ReLeMeshv2/src/:
    python3 benchmark.py
"""
import os
import sys
import time
import numpy as np
from ctypes import CDLL, c_int, c_float, c_bool, c_void_p, POINTER, byref

sys.path.insert(0, os.path.dirname(__file__))
from environments.triMesherEnv import triMesherEnv
from worldGenerators.simpleMeshWorldGenerator import simpleMeshWorldGenerator

LIB_PATH = os.path.join(
    os.path.dirname(__file__),
    '../../ReLeMeshCppv2/bin/ReLeMeshInterface.so'
)
N_STEPS   = 2000
WARMUP    = 50
SIZES     = [17, 25, 35]


# ---------------------------------------------------------------------------
# Load C++ library once
# ---------------------------------------------------------------------------
def load_lib():
    lib = CDLL(LIB_PATH)
    lib.createTriMeshEnvironment.restype  = c_void_p
    lib.createTriMeshEnvironment.argtypes = [c_int, c_int]
    lib.reset.restype  = None
    lib.reset.argtypes = [c_void_p]
    lib.step.restype   = None
    lib.step.argtypes  = [c_void_p, c_int, POINTER(c_float), POINTER(c_bool), POINTER(c_float)]
    lib.deleteEnvironment.restype  = None
    lib.deleteEnvironment.argtypes = [c_void_p]
    lib.getChannelCount.restype    = c_int
    lib.getChannelCount.argtypes   = [c_void_p]
    return lib


# ---------------------------------------------------------------------------
# Python benchmark
# ---------------------------------------------------------------------------
def bench_python(size, n_steps, warmup):
    env = triMesherEnv(size=size, seedValue=1, nLinesX=4, nLinesY=4)
    env.reset()

    for _ in range(warmup):
        _, _, done = env.step(0)
        if done:
            env.reset()

    env.reset()
    resets = 0
    t0 = time.perf_counter()
    for i in range(n_steps):
        _, _, done = env.step(i % 9)
        if done:
            env.reset()
            resets += 1
    elapsed = time.perf_counter() - t0
    return elapsed, resets


# ---------------------------------------------------------------------------
# C++ benchmark
# ---------------------------------------------------------------------------
def bench_cpp(lib, size, n_steps, warmup):
    ptr       = lib.createTriMeshEnvironment(size, size)
    n_ch      = lib.getChannelCount(ptr)
    buf       = (c_float * (size * size * n_ch))()
    reward    = c_float(0.0)
    done      = c_bool(False)

    for _ in range(warmup):
        lib.step(ptr, 0, byref(reward), byref(done), buf)
        if done.value:
            lib.reset(ptr)

    # --- raw: step call only ---
    lib.reset(ptr)
    resets = 0
    t0 = time.perf_counter()
    for i in range(n_steps):
        lib.step(ptr, i % 9, byref(reward), byref(done), buf)
        if done.value:
            lib.reset(ptr)
            resets += 1
    elapsed_raw = time.perf_counter() - t0

    # --- with numpy state extraction ---
    lib.reset(ptr)
    t0 = time.perf_counter()
    for i in range(n_steps):
        lib.step(ptr, i % 9, byref(reward), byref(done), buf)
        # Equivalent to what a training loop needs: state as float32 numpy array.
        _ = np.frombuffer(buf, dtype=np.float32).copy()
        if done.value:
            lib.reset(ptr)
    elapsed_extract = time.perf_counter() - t0

    lib.deleteEnvironment(ptr)
    return elapsed_raw, elapsed_extract, resets


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not os.path.exists(LIB_PATH):
        print(f'C++ library not found at:\n  {LIB_PATH}')
        print('Build it with:  cd ReLeMeshCppv2 && make bin/ReLeMeshInterface.so')
        sys.exit(1)

    lib = load_lib()

    header = f"{'Size':>6}  {'Python':>12}  {'C++ raw':>12}  {'C++ +extract':>14}  {'Speedup raw':>12}  {'Speedup +ext':>13}"
    sep    = '-' * len(header)
    print(f'\nBenchmark: {N_STEPS} steps per run  (warmup: {WARMUP} steps)\n')
    print(header)
    print(sep)

    for size in SIZES:
        py_t,  py_resets               = bench_python(size,      N_STEPS, WARMUP)
        cpp_raw, cpp_ext, cpp_resets   = bench_cpp(lib, size,    N_STEPS, WARMUP)

        py_sps   = N_STEPS / py_t
        raw_sps  = N_STEPS / cpp_raw
        ext_sps  = N_STEPS / cpp_ext

        print(
            f'{size:>4}x{size:<2}'
            f'  {py_sps:>9.0f}/s'
            f'  {raw_sps:>9.0f}/s'
            f'  {ext_sps:>11.0f}/s'
            f'  {py_t/cpp_raw:>10.1f}x'
            f'  {py_t/cpp_ext:>11.1f}x'
        )

    print(sep)
    print('\nColumns:')
    print('  Python       — triMesherEnv.step() including geometry, rendering, reward')
    print('  C++ raw      — ctypes step call (C++ computation only, no state copy)')
    print('  C++ +extract — ctypes step + np.frombuffer state copy (training-realistic)')


if __name__ == '__main__':
    main()
