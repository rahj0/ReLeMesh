"""Plot training curves from a ReLeMesh run directory.

Usage:
    python3 plot_training.py --path ./dqn/20260302_091230
    python3 plot_training.py --path ./dqn/20260302_091230 --window 200
"""
import argparse
import csv
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Plot ReLeMesh training curves.')
parser.add_argument('--path',   type=str, required=True, help='Run directory containing training_log.csv.')
parser.add_argument('--window', type=int, default=100,   help='Rolling average window (default 100).')
parser.add_argument('--out',    type=str, default=None,  help='Output PNG path (default: <path>/training_curves.png).')
args = parser.parse_args()

csv_path = os.path.join(args.path, 'training_log.csv')
if not os.path.exists(csv_path):
    raise FileNotFoundError(f'No training_log.csv found in {args.path}')

episodes, total_steps, rewards, steps, epsilons = [], [], [], [], []
with open(csv_path) as f:
    for row in csv.DictReader(f):
        episodes.append(int(row['episode']))
        total_steps.append(int(row['total_steps']))
        rewards.append(float(row['reward']))
        steps.append(int(row['steps']))
        epsilons.append(float(row['epsilon']))

episodes = np.array(episodes)
rewards  = np.array(rewards)
steps    = np.array(steps)
epsilons = np.array(epsilons)

def rolling(arr, w):
    if len(arr) < w:
        return arr
    return np.convolve(arr, np.ones(w) / w, mode='valid')

w = min(args.window, len(rewards))
roll_ep = episodes[w - 1:]

fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=False)
fig.suptitle(f'Training — {os.path.basename(args.path)}', fontsize=13)

# — Reward —
ax = axes[0]
ax.plot(episodes, rewards, alpha=0.25, color='steelblue', linewidth=0.7, label='raw')
ax.plot(roll_ep, rolling(rewards, w), color='steelblue', linewidth=1.5, label=f'mean{w}')
ax.set_ylabel('Episode reward')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# — Episode length —
ax = axes[1]
ax.plot(episodes, steps, alpha=0.25, color='darkorange', linewidth=0.7)
ax.plot(roll_ep, rolling(steps, w), color='darkorange', linewidth=1.5)
ax.set_ylabel('Episode length (steps)')
ax.grid(True, alpha=0.3)

# — Epsilon —
ax = axes[2]
ax.plot(episodes, epsilons, color='seagreen', linewidth=1.2)
ax.set_ylabel('Epsilon')
ax.set_xlabel('Episode')
ax.set_ylim(0, None)
ax.grid(True, alpha=0.3)

plt.tight_layout()
out = args.out or os.path.join(args.path, 'training_curves.png')
plt.savefig(out, dpi=150)
print(f'Saved → {out}')
