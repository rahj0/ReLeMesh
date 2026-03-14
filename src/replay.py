"""Replay a trained ReLeMesh agent and save a GIF.

Loads config.json + checkpoint.pt from a run directory, recreates the
environment, runs the agent greedily, and saves an animated GIF so you
can see the mesh being built step by step.

Usage:
    python3 replay.py --path ./dqn/20260302_091230
    python3 replay.py --path ./dqn/20260302_091230 --episodes 3 --fps 4
    python3 replay.py --path ./dqn/20260302_091230 --out my_replay.gif
"""
import argparse
import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import torch

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Replay a trained ReLeMesh agent.')
parser.add_argument('--path',       type=str, required=True,   help='Run directory containing checkpoint.pt and config.json.')
parser.add_argument('--episodes',   type=int, default=1,       help='Number of episodes to replay (default 1).')
parser.add_argument('--max-steps',  type=int, default=None,    help='Max steps per episode (default: value from config.json).')
parser.add_argument('--fps',        type=int, default=6,       help='GIF frames per second (default 6).')
parser.add_argument('--out',        type=str, default=None,    help='Output GIF path (default: <path>/replay.gif).')
parser.add_argument('--device',     type=str, default=None,    help='Device override: "cpu" or "cuda".')
parser.add_argument('--scale',      type=int, default=12,      help='Pixel upscale factor for display (default 12).')
args = parser.parse_args()

sys.path.insert(0, os.path.dirname(__file__))

# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------
config_path = os.path.join(args.path, 'config.json')
if not os.path.exists(config_path):
    raise FileNotFoundError(
        f'No config.json in {args.path}.\n'
        f'If this is an older run, use --env-size / --h-size etc. overrides.'
    )
with open(config_path) as f:
    cfg = json.load(f)

sizeEnv   = cfg['env_size']
h_size    = cfg['h_size']
use_cpp   = cfg['use_cpp']
xLines    = cfg.get('lines', 4)
nChannels = 2
max_steps = args.max_steps or cfg.get('max_ep_length', 175)

print(f'Config: env_size={sizeEnv}, h_size={h_size}, use_cpp={use_cpp}')

# ---------------------------------------------------------------------------
# Device
# ---------------------------------------------------------------------------
if args.device:
    device = torch.device(args.device)
else:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Device: {device}')

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
# Network
# ---------------------------------------------------------------------------
from Networks.BasicQNetwork import Qnetwork, processState

ckpt_path = os.path.join(args.path, 'checkpoint.pt')
if not os.path.exists(ckpt_path):
    raise FileNotFoundError(f'No checkpoint.pt in {args.path}')

mainQN = Qnetwork(h_size, env.getActionCount(), sizeEnv, nChannels).to(device)
ckpt   = torch.load(ckpt_path, map_location=device)
mainQN.load_state_dict(ckpt['model_state'])
mainQN.eval()
total_steps_trained = ckpt.get('total_steps', '?')
print(f'Loaded checkpoint (total_steps_trained={total_steps_trained})')

# ---------------------------------------------------------------------------
# Rendering helper
# ---------------------------------------------------------------------------
ACTION_NAMES = ['apex→x+', 'apex→x-', 'apex→y+', 'apex→y-',
                'apex→x+y+', 'apex→x-y+', 'apex→x+y-', 'apex→x-y-', 'PLACE ▶']


def state_to_rgb(state_hwc, scale):
    """Convert a [H, W, 2] state to a crisp upscaled RGB image.

    White background; placed triangles/walls in blue; active triangle in orange.
    Corners (highest-intensity pixels) are shown as dark anchor dots.

    Handles both renderers:
      Python env — values: 0 (empty), 0.5 (fill), 0.75 (edge), 1.0 (corner)
      C++ env    — values: 0 (empty), 1.0 (edge),              2.0 (corner)
    """
    c_active = state_hwc[:, :, 0].astype(np.float32)
    c_placed = state_hwc[:, :, 1].astype(np.float32)

    # Normalise so that the peak intensity maps to 1.0 in both env types.
    peak = max(c_active.max(), c_placed.max(), 1.0)
    c_active = c_active / peak
    c_placed = c_placed / peak

    # Classify each pixel: corner node (≥0.85) vs body (>0.05).
    def _corner(c): return c >= 0.85
    def _body(c):   return (c > 0.05) & (c < 0.85)

    r = np.ones_like(c_active)   # start with white background
    g = np.ones_like(c_active)
    b = np.ones_like(c_active)

    # Placed triangles + boundary walls — blue palette
    r[_body(c_placed)]   = 0.55;  g[_body(c_placed)]   = 0.78;  b[_body(c_placed)]   = 1.00
    r[_corner(c_placed)] = 0.00;  g[_corner(c_placed)] = 0.15;  b[_corner(c_placed)] = 0.65

    # Active triangle (drawn on top) — orange / red palette
    r[_body(c_active)]   = 1.00;  g[_body(c_active)]   = 0.55;  b[_body(c_active)]   = 0.05
    r[_corner(c_active)] = 0.65;  g[_corner(c_active)] = 0.00;  b[_corner(c_active)] = 0.00

    rgb = np.stack([r, g, b], axis=-1)
    return np.repeat(np.repeat(rgb, scale, axis=0), scale, axis=1)

# ---------------------------------------------------------------------------
# ASCII state printer
# ---------------------------------------------------------------------------
_CHAR = ['.', '+', '#', '@']   # empty / fill / edge / corner

def _pixel_char(norm_val):
    """Map a normalised [0,1] intensity to an ASCII character."""
    if norm_val >= 0.85: return '@'   # corner node
    if norm_val >= 0.60: return '#'   # edge
    if norm_val >= 0.05: return '+'   # interior fill
    return '.'

def print_state(state_hwc, q_vals, action):
    """Print both input channels as ASCII grids, numerical grids, and Q-values.

    state_hwc : [W, H, 2] numpy array (HWC, as returned by env)
    q_vals    : [n_actions] numpy array of raw Q-values
    action    : integer index of the chosen action
    """
    W, H = state_hwc.shape[0], state_hwc.shape[1]
    c0 = state_hwc[:, :, 0].astype(np.float32)
    c1 = state_hwc[:, :, 1].astype(np.float32)
    peak = max(c0.max(), c1.max(), 1.0)
    c0n = c0 / peak
    c1n = c1 / peak

    # --- ASCII grid (quick visual overview) ---
    print(f'  {"active (ch0)":^{W}}   {"placed (ch1)":^{W}}')
    for y in range(H - 1, -1, -1):
        row0 = ''.join(_pixel_char(c0n[x, y]) for x in range(W))
        row1 = ''.join(_pixel_char(c1n[x, y]) for x in range(W))
        print(f'  {row0}   {row1}')

    # --- Numerical grid (exact values the model receives) ---
    # Each cell is 3 chars wide ("0.0", "0.5", "1.0", "2.0", etc.)
    print()
    num_row_w = W * 4 - 1   # "x.x " * W, minus trailing space
    print(f'  {"active ch0":^{num_row_w}}   {"placed ch1":^{num_row_w}}')
    for y in range(H - 1, -1, -1):
        row0 = ' '.join(f'{c0[x, y]:.1f}' for x in range(W))
        row1 = ' '.join(f'{c1[x, y]:.1f}' for x in range(W))
        print(f'  {row0}   {row1}')

    # Q-value row — highlight the chosen action with brackets
    q_min, q_max = q_vals.min(), q_vals.max()
    q_range = q_max - q_min if q_max != q_min else 1.0
    parts = []
    for i, (name, q) in enumerate(zip(ACTION_NAMES, q_vals)):
        bar_len = int(8 * (q - q_min) / q_range)
        bar = '█' * bar_len + '░' * (8 - bar_len)
        marker = '◀' if i == action else ' '
        parts.append(f'  {name:<10} {bar} {q:+6.2f}{marker}')
    print()
    print('  Q-values:')
    # Print in two columns
    mid = (len(parts) + 1) // 2
    for a_row, b_row in zip(parts[:mid], parts[mid:] + ['']):
        print(f'{a_row}    {b_row}')
    print()


# ---------------------------------------------------------------------------
# Run episodes and collect frames
# ---------------------------------------------------------------------------
all_frames   = []   # list of (rgb_image, title_str)
episode_info = []   # (n_steps, total_reward) per episode

for ep in range(args.episodes):
    s = env.reset()
    total_r = 0.0
    step    = 0
    done    = False

    print(f'\n{"="*60}')
    print(f'Episode {ep + 1} / {args.episodes}   start')
    print(f'{"="*60}')

    # Initial frame — show the starting state before any action.
    all_frames.append((
        state_to_rgb(s, args.scale),
        f'Ep {ep + 1} / {args.episodes}   start',
    ))

    while not done and step < max_steps:
        s_proc = processState(s, sizeEnv, nChannels)
        with torch.no_grad():
            s_t   = torch.from_numpy(s_proc).unsqueeze(0).to(device)
            q_out = mainQN(s_t).squeeze(0).cpu().numpy()
            a     = int(q_out.argmax())

        print(f'--- step {step + 1}  →  {ACTION_NAMES[a]}   cumulative r={total_r:+.3f}')
        print_state(s, q_out, a)

        s, r, done = env.step(a)
        total_r += r
        step    += 1
        if total_r < -5.0:
            done = True

        # Each frame is annotated with the action that produced it.
        suffix = '  ✓ done' if done else ''
        all_frames.append((
            state_to_rgb(s, args.scale),
            f'Ep {ep + 1}  step {step:3d}  {ACTION_NAMES[a]}   r={total_r:+.3f}{suffix}',
        ))

    episode_info.append((step, total_r))
    print(f'  ep {ep + 1}: steps={step}, reward={total_r:.4f}')

# ---------------------------------------------------------------------------
# Build and save GIF
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(5, 5))
ax.axis('off')
im   = ax.imshow(all_frames[0][0], interpolation='nearest', vmin=0, vmax=1)
title = ax.set_title(all_frames[0][1], fontsize=10)
fig.tight_layout(pad=0.5)

def update(i):
    img, txt = all_frames[i]
    im.set_data(img)
    title.set_text(txt)
    return [im, title]

ani = animation.FuncAnimation(
    fig, update, frames=len(all_frames),
    interval=1000 // args.fps, blit=True,
)

out = args.out or os.path.join(args.path, 'replay.gif')
ani.save(out, writer=animation.PillowWriter(fps=args.fps))
plt.close(fig)
print(f'Saved → {out}')
