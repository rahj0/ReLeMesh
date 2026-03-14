import numpy as np
import torch
import torch.nn as nn


def _conv_params(sizeEnv):
    """Pick conv kernel/stride sizes that fit sizeEnv without zero-size feature maps.

    The original (k=4,s=2) x2 then (k=2,s=1) is preserved for sizeEnv>=15.
    Smaller grids fall back to smaller kernels so the architecture stays valid.
    """
    k1, s1 = min(4, sizeEnv), 2
    sz1    = max(1, (sizeEnv - k1) // s1 + 1)
    k2, s2 = min(4, sz1), (2 if sz1 >= 4 else 1)
    sz2    = max(1, (sz1 - k2) // s2 + 1)
    k3     = min(2, sz2)
    return k1, s1, k2, s2, k3


class Qnetwork(nn.Module):
    def __init__(self, h_size, envActions, sizeEnv, nChannels):
        super().__init__()
        self.sizeEnv = sizeEnv
        self.nChannels = nChannels
        self.envActions = envActions

        k1, s1, k2, s2, k3 = _conv_params(sizeEnv)
        self.conv1 = nn.Conv2d(nChannels, 64,     kernel_size=k1, stride=s1, padding=0, bias=False)
        self.conv2 = nn.Conv2d(64,        128,    kernel_size=k2, stride=s2, padding=0, bias=False)
        self.conv3 = nn.Conv2d(128,       h_size, kernel_size=k3, stride=1,  padding=0, bias=False)

        # Compute flattened size of each dueling stream from a dummy forward pass.
        with torch.no_grad():
            dummy = torch.zeros(1, nChannels, sizeEnv, sizeEnv)
            conv_out = self.conv3(self.conv2(self.conv1(dummy)))
            stream_size = (conv_out.shape[1] // 2) * conv_out.shape[2] * conv_out.shape[3]

        self.flat = nn.Flatten()
        self.advantage = nn.Linear(stream_size, envActions, bias=False)
        self.value     = nn.Linear(stream_size, 1,          bias=False)

        nn.init.xavier_uniform_(self.advantage.weight)
        nn.init.xavier_uniform_(self.value.weight)

    def forward(self, x):
        if not isinstance(x, torch.Tensor):
            x = torch.tensor(x, dtype=torch.float32)
        # Input is flat [N, C*H*W] in CHW order — view directly as NCHW for convolutions.
        x = x.view(-1, self.nChannels, self.sizeEnv, self.sizeEnv)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        # Split channel dim into advantage and value streams.
        streamA, streamV = torch.chunk(x, 2, dim=1)
        advantage = self.advantage(self.flat(streamA))
        value     = self.value(self.flat(streamV))
        return value + (advantage - advantage.mean(dim=1, keepdim=True))

    @torch.no_grad()
    def predict_action(self, x):
        return torch.argmax(self(x), dim=1)


class experience_buffer:
    """Pre-allocated numpy circular replay buffer.

    Stores each field in a separate typed array, eliminating dtype=object
    overhead and O(n) list eviction.  Sampling uses numpy fancy indexing
    and returns contiguous typed arrays ready for torch.from_numpy().
    """

    def __init__(self, buffer_size=10000, state_size=450):
        self._buf_size = buffer_size
        self._s    = np.zeros((buffer_size, state_size), dtype=np.float32)
        self._a    = np.zeros(buffer_size,               dtype=np.int64)
        self._r    = np.zeros(buffer_size,               dtype=np.float32)
        self._s1   = np.zeros((buffer_size, state_size), dtype=np.float32)
        self._done = np.zeros(buffer_size,               dtype=np.float32)
        self._ptr   = 0
        self._count = 0

    def add(self, s, a, r, s1, done):
        i = self._ptr % self._buf_size
        self._s[i]    = s
        self._a[i]    = int(a)
        self._r[i]    = float(r)
        self._s1[i]   = s1
        self._done[i] = float(done)
        self._ptr   += 1
        self._count  = min(self._ptr, self._buf_size)

    def sample(self, size):
        idxs = np.random.randint(0, self._count, size=size)
        return (
            self._s[idxs],
            self._a[idxs],
            self._r[idxs],
            self._s1[idxs],
            self._done[idxs],
        )

    @property
    def size(self):
        return self._count


def processState(states, sizeEnv, nChannels):
    """Flatten an HWC numpy state to a float32 CHW 1-D array.

    Converting HWC → CHW here means forward() can view the flat buffer
    directly as NCHW without a permute+contiguous copy on every forward pass.
    astype(copy=False) is a no-op when the array is already float32 (C++ env)
    and a cheap cast when it is float64 (Python env).
    """
    return states.transpose(2, 0, 1).ravel().astype(np.float32, copy=False)


def updateTarget(mainQN, targetQN, tau):
    with torch.no_grad():
        for main_p, target_p in zip(mainQN.parameters(), targetQN.parameters()):
            target_p.data.lerp_(main_p.data, tau)
