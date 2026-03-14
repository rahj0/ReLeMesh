import argparse
import glob
import json
import os
import torch
from tkinter import *
from MeshEnvViewer import meshEnvViewer
from Networks.BasicQNetwork import Qnetwork
from worldGenerators.simpleMeshWorldGenerator import simpleMeshWorldGenerator

parser = argparse.ArgumentParser(description='View a trained ReLeMesh agent in the interactive viewer.')
parser.add_argument('--path',   type=str, default='./dqn', help='Run directory containing checkpoint.pt and config.json (auto-detects latest run if a parent dir is given).')
parser.add_argument('--device', type=str, default=None,    help='Device override: "cpu" or "cuda".')
args = parser.parse_args()

# Auto-detect latest timestamped run if a parent directory is given.
# Key off config.json (always present in timestamped subdirs) to avoid
# picking up old bare checkpoints that pre-date config.json saving.
run_dir = args.path
if not os.path.exists(os.path.join(run_dir, 'config.json')):
    runs = sorted(glob.glob(os.path.join(run_dir, '2*')))
    if runs:
        run_dir = runs[-1]

CHECKPOINT = os.path.join(run_dir, 'checkpoint.pt')
if not os.path.exists(CHECKPOINT):
    print(f'No checkpoint found in {args.path}')
    print('Train first with: python3 gameTrainingMain.py --episodes 5000')
    exit()
print(f'Loading run: {run_dir}')

# Load config so env/network are built with the correct shapes.
cfg = {}
cfg_path = os.path.join(run_dir, 'config.json')
if os.path.exists(cfg_path):
    with open(cfg_path) as f:
        cfg = json.load(f)
else:
    print('Warning: no config.json found — using defaults (env_size=15, h_size=512, Python env).')

sizeEnv   = cfg.get('env_size', 15)
h_size    = cfg.get('h_size',   512)
xLines    = cfg.get('lines',    4)
use_cpp   = cfg.get('use_cpp',  False)
nChannels = 2

# Build environment.
if use_cpp:
    from environments.triMesherEnvCpp import triMesherEnvCpp
    cpp_lib = cfg.get('cpp_lib')
    kwargs  = {'lib_path': cpp_lib} if cpp_lib else {}
    env      = triMesherEnvCpp(size=sizeEnv, **kwargs)
    fullEnv  = None
else:
    from environments.triMesherEnv import triMesherEnv
    from environments.PartialViewEnv import PartialViewEnv
    full_size = max(25, sizeEnv + 10)
    fullEnv   = triMesherEnv(size=full_size, seedValue=2, nLinesX=xLines, nLinesY=xLines)
    fullEnv.setWorldGenerator(simpleMeshWorldGenerator(xLines, xLines, 0, 0))
    env = PartialViewEnv(fullEnv, sizeEnv)

device = torch.device(args.device) if args.device else \
         torch.device('cuda' if torch.cuda.is_available() else 'cpu')

mainQN = Qnetwork(h_size, env.getActionCount(), sizeEnv, nChannels).to(device)
ckpt   = torch.load(CHECKPOINT, map_location=device)
mainQN.load_state_dict(ckpt['model_state'])
mainQN.eval()
print(f"Model loaded (total_steps={ckpt.get('total_steps','?')}, e={ckpt.get('e','?')})")

master = Tk()
viewer = meshEnvViewer(master, env, 20, qNetwork=mainQN)
mainloop()

# After closing: show the full environment state (Python env only).
if fullEnv is not None:
    master = Tk()
    viewer = meshEnvViewer(master, fullEnv, 20)
    mainloop()
