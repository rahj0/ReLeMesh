# -*- coding: utf-8 -*-
"""Interactive manual-control viewer for ReLeMesh.

Loads the environment from a training run directory (config.json + optional
checkpoint.pt) so you are always looking at the same problem the agent trained on.

Usage:
    python3 MeshEnvViewerGame.py                          # auto-detect latest run
    python3 MeshEnvViewerGame.py --path ./dqn/20260302_091230
    python3 MeshEnvViewerGame.py --path ./dqn/20260302_091230 --device cpu

Controls:
    Arrow keys   Move triangle apex
    Enter        Place current triangle (commit)
    Space        Toggle left/right corner selection
    q            Let the AI take one step (if checkpoint loaded)
"""
import argparse
import glob
import json
import os
import sys
from tkinter import *

parser = argparse.ArgumentParser(description='Interactive ReLeMesh viewer.')
parser.add_argument('--path',   type=str, default='./dqn', help='Run directory with config.json (auto-detects latest run if a parent dir is given).')
parser.add_argument('--device', type=str, default=None,    help='Device override: "cpu" or "cuda".')
args = parser.parse_args()

sys.path.insert(0, os.path.dirname(__file__))

# ---------------------------------------------------------------------------
# Auto-detect latest timestamped run if a parent directory is given.
# ---------------------------------------------------------------------------
def _latest_run(base):
    runs = sorted(glob.glob(os.path.join(base, '2*')))
    return runs[-1] if runs else base

run_dir = args.path
if not os.path.exists(os.path.join(run_dir, 'config.json')):
    run_dir = _latest_run(run_dir)

# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------
cfg = {}
cfg_path = os.path.join(run_dir, 'config.json')
if os.path.exists(cfg_path):
    with open(cfg_path) as f:
        cfg = json.load(f)
    print(f'Config loaded from: {cfg_path}')
else:
    print('Warning: no config.json found — using defaults.')

sizeEnv   = cfg.get('env_size', 15)
h_size    = cfg.get('h_size',   512)
xLines    = cfg.get('lines',    4)
use_cpp   = cfg.get('use_cpp',  False)
nChannels = 2

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
if use_cpp:
    from environments.triMesherEnvCpp import triMesherEnvCpp
    cpp_lib = cfg.get('cpp_lib')
    kwargs  = {'lib_path': cpp_lib} if cpp_lib else {}
    env = triMesherEnvCpp(size=sizeEnv, **kwargs)
else:
    from environments.triMesherEnv import triMesherEnv
    from environments.PartialViewEnv import PartialViewEnv
    from worldGenerators.simpleMeshWorldGenerator import simpleMeshWorldGenerator
    full_size = max(25, sizeEnv + 10)
    fullEnv   = triMesherEnv(size=full_size, seedValue=2, nLinesX=xLines, nLinesY=xLines)
    fullEnv.setWorldGenerator(simpleMeshWorldGenerator(xLines, xLines, 0, 0))
    env = PartialViewEnv(fullEnv, sizeEnv)

# ---------------------------------------------------------------------------
# Optionally load network (enables 'q' key for AI step)
# ---------------------------------------------------------------------------
mainQN = None
ckpt_path = os.path.join(run_dir, 'checkpoint.pt')
if os.path.exists(ckpt_path):
    import torch
    from Networks.BasicQNetwork import Qnetwork
    device = torch.device(args.device) if args.device else \
             torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    mainQN = Qnetwork(h_size, env.getActionCount(), sizeEnv, nChannels).to(device)
    ckpt   = torch.load(ckpt_path, map_location=device)
    mainQN.load_state_dict(ckpt['model_state'])
    mainQN.eval()
    print(f'Network loaded (total_steps={ckpt.get("total_steps","?")})  — press q for AI step')
else:
    print('No checkpoint found — manual play only.')

# ---------------------------------------------------------------------------
# Launch viewer
# ---------------------------------------------------------------------------
from MeshEnvViewer import meshEnvViewer

master = Tk()
master.wm_title(f'ReLeMesh — {os.path.basename(run_dir)}')
viewer = meshEnvViewer(master, env, lineDistance=20, qNetwork=mainQN)
mainloop()
