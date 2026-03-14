"""
Evaluate a trained ReLeMesh agent with a greedy policy (epsilon=0).
Loads config.json + checkpoint.pt from --path and runs --episodes episodes,
reporting mean, std, min and max reward.

Usage:
    python3 evaluate.py --episodes 100 --path ./dqn/20260302_143021
    python3 evaluate.py --episodes 100 --path ./dqn/20260302_143021 --seed 42
"""
import argparse
import json
import logging
import numpy as np
import os
import torch

from Networks.BasicQNetwork import Qnetwork, processState

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger('evaluate')

parser = argparse.ArgumentParser(description='Evaluate a trained ReLeMesh agent.')
parser.add_argument('--episodes',      type=int,   default=100,    help='Number of evaluation episodes.')
parser.add_argument('--max-ep-length', type=int,   default=300,    help='Max steps per episode.')
parser.add_argument('--path',          type=str,   default='./dqn',help='Run directory (contains checkpoint.pt and config.json).')
parser.add_argument('--seed',          type=int,   default=None,   help='Random seed.')
parser.add_argument('--device',        type=str,   default=None,   help='Device override: "cpu" or "cuda".')
args = parser.parse_args()

if args.seed is not None:
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

CHECKPOINT = os.path.join(args.path, 'checkpoint.pt')
if not os.path.exists(CHECKPOINT):
    log.error(f'No checkpoint found at {CHECKPOINT}. Train first with gameTrainingMain.py.')
    exit(1)

# Load config so env/network are built with the correct shapes.
cfg = {}
cfg_path = os.path.join(args.path, 'config.json')
if os.path.exists(cfg_path):
    with open(cfg_path) as f:
        cfg = json.load(f)
else:
    log.warning('No config.json found — falling back to defaults (env_size=15, h_size=512, Python env).')

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
    env = triMesherEnvCpp(size=sizeEnv, **kwargs)
else:
    from environments.triMesherEnv import triMesherEnv
    from environments.PartialViewEnv import PartialViewEnv
    from worldGenerators.simpleMeshWorldGenerator import simpleMeshWorldGenerator
    full_size = max(25, sizeEnv + 10)
    fullEnv   = triMesherEnv(size=full_size, seedValue=2, nLinesX=xLines, nLinesY=xLines)
    fullEnv.setWorldGenerator(simpleMeshWorldGenerator(xLines, xLines, 0, 0))
    env = PartialViewEnv(fullEnv, sizeEnv)

if args.device:
    device = torch.device(args.device)
else:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
log.info(f'Using device: {device}  |  env_size={sizeEnv}  h_size={h_size}  use_cpp={use_cpp}')

model = Qnetwork(h_size, env.getActionCount(), sizeEnv, nChannels).to(device)
ckpt  = torch.load(CHECKPOINT, map_location=device)
model.load_state_dict(ckpt['model_state'])
model.eval()
log.info(f"Loaded checkpoint (trained for {ckpt.get('total_steps','?')} steps, e={ckpt.get('e', '?')})")

rewards = []
for ep in range(args.episodes):
    s    = processState(env.reset(), sizeEnv, nChannels)
    rAll = 0.0

    for _ in range(args.max_ep_length):
        with torch.no_grad():
            s_t = torch.from_numpy(s).unsqueeze(0).to(device)
            a   = model.predict_action(s_t).item()
        s1, r, done = env.step(a)
        s    = processState(s1, sizeEnv, nChannels)
        rAll += r
        if rAll < -5.0 or done:
            break

    rewards.append(rAll)
    if (ep + 1) % 10 == 0:
        log.info(f'Episode {ep + 1}/{args.episodes}  reward={rAll:.4f}')

rewards = np.array(rewards)
log.info('--- Evaluation Results ---')
log.info(f'Episodes : {args.episodes}')
log.info(f'Mean     : {rewards.mean():.4f}')
log.info(f'Std      : {rewards.std():.4f}')
log.info(f'Min      : {rewards.min():.4f}')
log.info(f'Max      : {rewards.max():.4f}')
