import argparse
import csv
import json
import logging
import numpy as np
import os
import random
import time
from datetime import datetime

import torch
import torch.nn.functional as F

# ---------------------------------------------------------------------------
# GIF helpers (used at end of training to save best-episode replays)
# ---------------------------------------------------------------------------
_TOP_N = 3   # number of best episodes to save as GIFs


_ACTION_NAMES = ['apex→x+', 'apex→x-', 'apex→y+', 'apex→y-',
                 'apex→x+y+', 'apex→x-y+', 'apex→x+y-', 'apex→x-y-', 'PLACE ▶']


def _state_to_rgb(state_hwc, scale):
    """Render a [H, W, 2] HWC state as a crisp upscaled RGB image.

    White background; placed triangles/walls in blue; active triangle in orange.
    Normalises for both Python (0/0.5/0.75/1.0) and C++ (0/1/2) env state values.
    """
    c_active = state_hwc[:, :, 0].astype(np.float32)
    c_placed = state_hwc[:, :, 1].astype(np.float32)
    peak = max(c_active.max(), c_placed.max(), 1.0)
    c_active = c_active / peak
    c_placed = c_placed / peak

    def _corner(c): return c >= 0.85
    def _body(c):   return (c > 0.05) & (c < 0.85)

    r = np.ones_like(c_active)
    g = np.ones_like(c_active)
    b = np.ones_like(c_active)

    r[_body(c_placed)]   = 0.55;  g[_body(c_placed)]   = 0.78;  b[_body(c_placed)]   = 1.00
    r[_corner(c_placed)] = 0.00;  g[_corner(c_placed)] = 0.15;  b[_corner(c_placed)] = 0.65
    r[_body(c_active)]   = 1.00;  g[_body(c_active)]   = 0.55;  b[_body(c_active)]   = 0.05
    r[_corner(c_active)] = 0.65;  g[_corner(c_active)] = 0.00;  b[_corner(c_active)] = 0.00

    rgb = np.stack([r, g, b], axis=-1)
    return np.repeat(np.repeat(rgb, scale, axis=0), scale, axis=1)


def _save_top_picture(top_episodes, path, scale=8):
    """Save a side-by-side PNG of the final placed mesh for each top episode.

    Renders only the placed-triangles channel (channel 1) so the picture shows
    the clean completed mesh without the in-progress active triangle.
    Episodes are ordered best-first (left to right).
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        log.warning('matplotlib not installed — skipping picture save.')
        return

    episodes = list(reversed(top_episodes))   # best first
    n = len(episodes)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axes = [axes]

    for ax, (ep_r, ep_st, ep_rw, ep_ac) in zip(axes, episodes):
        # Use the last frame — all placed triangles + boundary walls are in channel 1.
        c = ep_st[-1][:, :, 1].astype(np.float32)
        peak = max(c.max(), 1.0)
        c = c / peak

        r = np.ones_like(c); g = np.ones_like(c); b = np.ones_like(c)
        body   = (c > 0.05) & (c < 0.85)
        corner = c >= 0.85
        r[body]   = 0.55;  g[body]   = 0.78;  b[body]   = 1.00
        r[corner] = 0.00;  g[corner] = 0.15;  b[corner] = 0.65

        rgb = np.repeat(np.repeat(np.stack([r, g, b], axis=-1), scale, axis=0), scale, axis=1)
        ax.imshow(rgb, interpolation='nearest', vmin=0, vmax=1)
        ax.axis('off')
        ax.set_title(f'r={ep_r:+.3f}  steps={len(ep_st) - 1}', fontsize=9)

    fig.suptitle(f'Top {n} episodes — final mesh', fontsize=11)
    fig.tight_layout(pad=0.8)
    fig.savefig(path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def _save_episode_gif(states, rewards, actions, path, fps=6, scale=8):
    """Save an animated GIF from HWC states, cumulative rewards, and actions taken."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation
    except ImportError:
        log.warning('matplotlib not installed — skipping GIF save.')
        return

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.axis('off')
    im    = ax.imshow(_state_to_rgb(states[0], scale), interpolation='nearest', vmin=0, vmax=1)
    title = ax.set_title('start', fontsize=9)
    fig.tight_layout(pad=0.5)

    def _label(i):
        if i == 0:
            return 'start'
        a_name = _ACTION_NAMES[actions[i - 1]] if actions else f'a={actions[i-1]}'
        return f'step {i}  {a_name}   r={rewards[i]:+.3f}'

    def _update(i):
        im.set_data(_state_to_rgb(states[i], scale))
        title.set_text(_label(i))
        return [im, title]

    ani = animation.FuncAnimation(
        fig, _update, frames=len(states), interval=1000 // fps, blit=True,
    )
    ani.save(path, writer=animation.PillowWriter(fps=fps))
    plt.close(fig)

from environments.triMesherEnv import triMesherEnv
from worldGenerators.ObjectInTheMiddleWorldGenerator import *
from environments.PartialViewEnv import PartialViewEnv
from Networks.BasicQNetwork import Qnetwork, experience_buffer, processState, updateTarget

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Train a Double DQN agent to generate 2D meshes.')
parser.add_argument('--episodes',        type=int,   default=5000,   help='Number of training episodes.')
parser.add_argument('--batch-size',      type=int,   default=160,    help='Replay batch size.')
parser.add_argument('--update-freq',     type=int,   default=20,     help='Steps between gradient updates.')
parser.add_argument('--gamma',           type=float, default=0.92,   help='Discount factor.')
parser.add_argument('--start-epsilon',   type=float, default=0.6,    help='Initial exploration rate.')
parser.add_argument('--end-epsilon',     type=float, default=0.01,   help='Final exploration rate.')
parser.add_argument('--annealing-steps', type=int,   default=600000, help='Steps to anneal epsilon.')
parser.add_argument('--pre-train-steps', type=int,   default=100000, help='Random steps before training.')
parser.add_argument('--buffer-size',     type=int,   default=100000, help='Replay buffer capacity.')
parser.add_argument('--tau',             type=float, default=0.001,  help='Target network update rate.')
parser.add_argument('--lr',              type=float, default=1e-4,   help='Adam learning rate.')
parser.add_argument('--h-size',          type=int,   default=512,    help='Final conv layer channels.')
parser.add_argument('--max-ep-length',   type=int,   default=175,    help='Max steps per episode.')
parser.add_argument('--seed',            type=int,   default=None,   help='Random seed for reproducibility.')
parser.add_argument('--device',          type=str,   default=None,   help='Device override: "cpu" or "cuda". Auto-detects if unset.')
parser.add_argument('--load-model',      action='store_true',        help='Resume from checkpoint.')
parser.add_argument('--path',            type=str,   default='./dqn',help='Checkpoint directory.')
parser.add_argument('--log-csv',         type=str,   default='training_log.csv', help='CSV log file path.')
parser.add_argument('--use-cpp',         action='store_true',        help='Use C++ environment backend (faster, no PartialViewEnv).')
parser.add_argument('--cpp-lib',         type=str,   default=None,   help='Path to ReLeMeshInterface.so (auto-detected if unset).')
parser.add_argument('--env-size',        type=int,   default=15,     help='Grid size. Try 9 for quick experiments (default 15).')
parser.add_argument('--lines',           type=int,   default=4,      help='Boundary lines per side for Python env (default 4; fewer = simpler). Ignored by C++ env.')

# Allow import without sys.argv conflicts (e.g. from unit tests).
if __name__ == '__main__':
    args = parser.parse_args()
else:
    args = parser.parse_args([])

# ---------------------------------------------------------------------------
# Seeding (P15)
# ---------------------------------------------------------------------------
if args.seed is not None:
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

# ---------------------------------------------------------------------------
# Logging (P6)
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger('ReLeMesh')

# ---------------------------------------------------------------------------
# Restore structural config when resuming
# env_size and h_size determine network weight shapes, so they MUST match the
# checkpoint.  Read them from config.json; CLI args are used as fallback for
# runs that pre-date config.json saving.
# ---------------------------------------------------------------------------
_resume_cfg = {}
if args.load_model:
    _cfg_path = os.path.join(args.path, 'config.json')
    if os.path.exists(_cfg_path):
        with open(_cfg_path) as f:
            _resume_cfg = json.load(f)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
sizeEnv   = _resume_cfg.get('env_size', args.env_size)
xLines    = _resume_cfg.get('lines',    args.lines)
yLines    = xLines
nChannels = 2
if args.use_cpp:
    from environments.triMesherEnvCpp import triMesherEnvCpp
    kwargs = {'lib_path': args.cpp_lib} if args.cpp_lib else {}
    env = triMesherEnvCpp(size=sizeEnv, nLinesX=xLines, nLinesY=yLines, **kwargs)
    env.reset()
    log.info('Using C++ environment backend.')
else:
    full_env_size = max(25, sizeEnv + 10)
    fullEnv = triMesherEnv(size=full_env_size, seedValue=2, nLinesX=xLines, nLinesY=yLines)
    fullEnv.setWorldGenerator(simpleMeshWorldGenerator(xLines, yLines, 0, 0))
    env = PartialViewEnv(fullEnv, sizeEnv)

# ---------------------------------------------------------------------------
# Hyperparameters (from CLI)
# ---------------------------------------------------------------------------
num_episodes    = args.episodes
batch_size      = args.batch_size
update_freq     = args.update_freq
gamma           = args.gamma
startE          = args.start_epsilon
endE            = args.end_epsilon
annealing_steps = args.annealing_steps
pre_train_steps = args.pre_train_steps
bufferSize      = args.buffer_size
tau             = args.tau
h_size          = _resume_cfg.get('h_size', args.h_size)
max_epLength    = args.max_ep_length

# New runs get a timestamped subdirectory so multiple runs never collide.
# To resume: pass the exact timestamped path with --load-model.
if args.load_model:
    run_dir = args.path          # resume: use the path as-is
else:
    run_dir = os.path.join(args.path, datetime.now().strftime('%Y%m%d_%H%M%S'))
CHECKPOINT = os.path.join(run_dir, 'checkpoint.pt')

log.info(f'Annealing steps: {annealing_steps}')

# ---------------------------------------------------------------------------
# Networks & optimiser
# ---------------------------------------------------------------------------
if args.device:
    device = torch.device(args.device)
else:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
log.info(f'Using device: {device}')
if _resume_cfg:
    log.info(f'Resumed config: env_size={sizeEnv}, h_size={h_size}, lines={xLines}')
mainQN   = Qnetwork(h_size, env.getActionCount(), sizeEnv, env.getNumberOfChannels()).to(device)
targetQN = Qnetwork(h_size, env.getActionCount(), sizeEnv, env.getNumberOfChannels()).to(device)
targetQN.load_state_dict(mainQN.state_dict())
targetQN.eval()

optimizer = torch.optim.Adam(mainQN.parameters(), lr=args.lr)
myBuffer  = experience_buffer(buffer_size=bufferSize,
                              state_size=sizeEnv * sizeEnv * nChannels)

# ---------------------------------------------------------------------------
# Training state
# ---------------------------------------------------------------------------
e           = startE
stepDrop    = (startE - endE) / annealing_steps
total_steps = 0
jList       = []
rList       = []

os.makedirs(run_dir, exist_ok=True)

# Save config so replay/plot tools can reconstruct the run without extra flags.
if not args.load_model:
    config_dict = {
        'env_size': sizeEnv, 'lines': xLines, 'h_size': h_size,
        'use_cpp': args.use_cpp, 'gamma': gamma, 'lr': args.lr,
        'batch_size': batch_size, 'update_freq': update_freq,
        'pre_train_steps': pre_train_steps, 'annealing_steps': annealing_steps,
        'start_epsilon': startE, 'end_epsilon': endE,
        'buffer_size': bufferSize, 'tau': tau, 'max_ep_length': max_epLength,
        'seed': args.seed, 'cpp_lib': args.cpp_lib,
    }
    with open(os.path.join(run_dir, 'config.json'), 'w') as f:
        json.dump(config_dict, f, indent=2)
    log.info(f'Run dir: {run_dir}')

if args.load_model:
    if os.path.exists(CHECKPOINT):
        ckpt = torch.load(CHECKPOINT, map_location=device)
        mainQN.load_state_dict(ckpt['model_state'])
        targetQN.load_state_dict(ckpt['target_state'])
        optimizer.load_state_dict(ckpt['optimizer_state'])
        total_steps = ckpt['total_steps']
        e           = max(endE, ckpt['e'])
        log.info(f'Resumed from checkpoint: total_steps={total_steps}, e={e:.4f}')
    else:
        log.warning(f'--load-model set but no checkpoint found at {CHECKPOINT}. Starting fresh.')

# ---------------------------------------------------------------------------
# CSV log (P9)
# ---------------------------------------------------------------------------
csv_path    = os.path.join(run_dir, args.log_csv)
csv_is_new  = not os.path.exists(csv_path)
csv_file    = open(csv_path, 'a', newline='')
csv_writer  = csv.writer(csv_file)
if csv_is_new:
    csv_writer.writerow(['episode', 'total_steps', 'reward', 'steps', 'epsilon'])

# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------
maxScore      = 0
last_avg      = 0
envResetTime  = 0.0
envRenderTime = 0.0
networkTime   = 0.0
startComplete = time.time()
_top_episodes = []   # list of (reward, states, cumulative_rewards) — top _TOP_N by reward

for i in range(num_episodes):
    start = time.time()
    s_raw = env.reset()
    envResetTime += time.time() - start
    ep_states  = [s_raw.copy()]   # raw HWC frames for potential GIF
    ep_rewards = [0.0]            # cumulative reward at each frame
    ep_actions = []               # action taken at each step
    s = processState(s_raw, sizeEnv, env.getNumberOfChannels())

    d    = False
    rAll = 0.0
    j    = 0

    while j < max_epLength:
        j += 1

        if np.random.rand() < e or total_steps < pre_train_steps:
            a = np.random.randint(0, env.getActionCount())
        else:
            start0 = time.time()
            s_t = torch.from_numpy(s).unsqueeze(0).to(device)
            a   = mainQN.predict_action(s_t).item()
            networkTime += time.time() - start0

        start = time.time()
        s1_raw, r, d = env.step(a)
        envRenderTime += time.time() - start

        ep_states.append(s1_raw.copy())
        ep_actions.append(a)
        s1 = processState(s1_raw, sizeEnv, env.getNumberOfChannels())
        total_steps += 1
        myBuffer.add(s, a, r, s1, d)

        if total_steps > pre_train_steps:
            if e > endE:
                e -= stepDrop

            if total_steps % update_freq == 0:
                start0 = time.time()
                s_cur, acts, rews, s_next, dones = myBuffer.sample(batch_size)

                states_cur  = torch.from_numpy(s_cur).to(device)
                states_next = torch.from_numpy(s_next).to(device)
                actions     = torch.from_numpy(acts).to(device)
                rewards_t   = torch.from_numpy(rews).to(device)
                dones_t     = torch.from_numpy(dones).to(device)

                # Double-DQN target Q-values.
                with torch.no_grad():
                    Q1      = mainQN(states_next).argmax(dim=1)
                    Q2      = targetQN(states_next)
                    doubleQ = Q2[range(batch_size), Q1]
                    targetQ = rewards_t + gamma * doubleQ * (1.0 - dones_t)

                # Gradient update.
                mainQN.train()
                Qout    = mainQN(states_cur)
                Q_taken = Qout.gather(1, actions.unsqueeze(1)).squeeze(1)
                loss    = F.mse_loss(Q_taken, targetQ)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                mainQN.eval()

                updateTarget(mainQN, targetQN, tau)
                networkTime += time.time() - start0

        rAll += r
        ep_rewards.append(rAll)
        if rAll < -5.0:
            d = True
        s = s1
        if d:
            break

    # Update top-N episode list for end-of-training GIFs.
    if len(_top_episodes) < _TOP_N or rAll > _top_episodes[0][0]:
        _top_episodes.append((rAll, ep_states, ep_rewards, ep_actions))
        _top_episodes.sort(key=lambda x: x[0])
        if len(_top_episodes) > _TOP_N:
            _top_episodes.pop(0)  # drop lowest

    if rAll > maxScore:
        env.printStats()
        maxScore = rAll

    jList.append(j)
    rList.append(rAll)

    # CSV log every episode.
    csv_writer.writerow([i, total_steps, f'{rAll:.4f}', j, f'{e:.4f}'])
    csv_file.flush()

    # Checkpoint every 1000 episodes.
    if i % 1000 == 0:
        torch.save({
            'model_state':     mainQN.state_dict(),
            'target_state':    targetQN.state_dict(),
            'optimizer_state': optimizer.state_dict(),
            'total_steps':     total_steps,
            'e':               e,
        }, CHECKPOINT)
        log.info(f'Checkpoint saved | episode={i} | e={e:.4f} | total_steps={total_steps}'
                 f' | env_time={envRenderTime:.1f}s | net_time={networkTime:.1f}s')

    if len(rList) % 100 == 0:
        mean500 = np.mean(rList[-500:])
        log.info(f'Avg reward (last 500, ep {i}): {mean500:.4f}  Δ{mean500 - last_avg:+.4f}')
        last_avg = mean500

# Final save.
torch.save({
    'model_state':     mainQN.state_dict(),
    'target_state':    targetQN.state_dict(),
    'optimizer_state': optimizer.state_dict(),
    'total_steps':     total_steps,
    'e':               e,
}, CHECKPOINT)
csv_file.close()

log.info(f'Training complete.')
log.info(f'Mean reward: {sum(rList) / num_episodes:.4f}')
log.info(f'Best score:  {maxScore:.4f}')
log.info(f'Total steps: {total_steps}')
log.info(f'Env time:    {envRenderTime:.1f}s')
log.info(f'Net time:    {networkTime:.1f}s')
log.info(f'Total time:  {time.time() - startComplete:.1f}s')

# ---------------------------------------------------------------------------
# Save GIFs for the top-N episodes.
# ---------------------------------------------------------------------------
log.info(f'Saving best-episode GIFs (top {_TOP_N})...')
for rank, (ep_r, ep_st, ep_rw, ep_ac) in enumerate(reversed(_top_episodes)):
    gif_path = os.path.join(run_dir, f'best_{rank + 1:02d}_r{ep_r:.4f}.gif')
    _save_episode_gif(ep_st, ep_rw, ep_ac, gif_path)
    log.info(f'  #{rank + 1}: reward={ep_r:.4f}  steps={len(ep_st) - 1}  → {gif_path}')

pic_path = os.path.join(run_dir, 'best_episodes.png')
_save_top_picture(_top_episodes, pic_path)
log.info(f'  Best-episodes picture → {pic_path}')
