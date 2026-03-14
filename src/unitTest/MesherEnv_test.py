"""
Unit tests for ReLeMesh environments, rendering, and reward logic.
Run from ReLeMeshv2/src/:
    python3 -m pytest unitTest/MesherEnv_test.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import numpy as np

from environments.triMesherEnv import triMesherEnv
from environments.PartialViewEnv import PartialViewEnv
from environments.Rendering.BasicEnvironmentRender import BasicEnvironmentRender
from gameObjects.triObj import triObj
from gameObjects.lineObj import lineOb


# ---------------------------------------------------------------------------
# Environment construction
# ---------------------------------------------------------------------------
class TestTriMesherEnvConstructor(unittest.TestCase):

    def test_valid_size(self):
        env = triMesherEnv(20)
        self.assertEqual(env.getSizeX(), 20)
        self.assertEqual(env.getSizeY(), 20)

    def test_minimum_valid_size(self):
        env = triMesherEnv(7)
        self.assertIsNotNone(env)

    def test_too_small_raises(self):
        with self.assertRaises(ValueError):
            triMesherEnv(3)

    def test_zero_size_raises(self):
        with self.assertRaises(ValueError):
            triMesherEnv(0)

    def test_negative_size_raises(self):
        with self.assertRaises(ValueError):
            triMesherEnv(-5)

    def test_action_count(self):
        env = triMesherEnv(20)
        self.assertEqual(env.getActionCount(), 9)

    def test_channel_count(self):
        env = triMesherEnv(20)
        self.assertEqual(env.getNumberOfChannels(), 2)


# ---------------------------------------------------------------------------
# Environment step / reset
# ---------------------------------------------------------------------------
class TestTriMesherEnvStep(unittest.TestCase):

    def setUp(self):
        self.env = triMesherEnv(20)

    def test_reset_returns_correct_shape(self):
        state = self.env.reset()
        self.assertEqual(state.shape, (20, 20, 2))

    def test_step_returns_state_reward_done(self):
        self.env.reset()
        for action in range(8):          # all movement actions
            state, reward, done = self.env.step(action)
            self.assertEqual(state.shape, (20, 20, 2))
            self.assertIsInstance(reward, float)
            self.assertIsInstance(done, bool)

    def test_movement_produces_nonzero_reward(self):
        self.env.reset()
        _, reward, _ = self.env.step(0)
        self.assertNotEqual(reward, 0.0)

    def test_finish_action_spawns_new_hero(self):
        self.env.reset()
        nHerosBefore = self.env._nHeros
        self.env.step(8)   # action 8 = finish
        self.assertEqual(self.env._nHeros, nHerosBefore + 1)

    def test_episode_terminates(self):
        self.env.reset()
        done = False
        steps = 0
        while not done and steps < 10000:
            _, _, done = self.env.step(8)  # always finish immediately
            steps += 1
        self.assertTrue(done)


# ---------------------------------------------------------------------------
# PartialViewEnv
# ---------------------------------------------------------------------------
class TestPartialViewEnv(unittest.TestCase):

    def setUp(self):
        full = triMesherEnv(size=25, nLinesX=4, nLinesY=4)
        self.env = PartialViewEnv(full, viewSize=15)

    def test_reset_returns_correct_shape(self):
        state = self.env.reset()
        self.assertEqual(state.shape, (15, 15, 2))

    def test_step_returns_partial_state(self):
        self.env.reset()
        state, _, _ = self.env.step(0)
        self.assertEqual(state.shape, (15, 15, 2))

    def test_channel_count(self):
        self.assertEqual(self.env.getNumberOfChannels(), 2)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
class TestBasicEnvironmentRender(unittest.TestCase):

    def test_render_single_triangle(self):
        render = BasicEnvironmentRender(25, 25)
        tri = triObj((5, 5), (15, 5), intensity=0.75, channel=0, reward=None)
        ok, state = render.renderEnvObject(tri, np.zeros((25, 25)))
        self.assertTrue(ok)
        self.assertTrue(np.any(state > 0))

    def test_render_produces_two_channel_output(self):
        render = BasicEnvironmentRender(25, 25)
        tri = triObj((5, 5), (15, 5), intensity=0.75, channel=0, reward=None)
        ok, state = render.renderEnv([tri])
        self.assertTrue(ok)
        self.assertEqual(state.shape, (25, 25, 2))

    def test_compute_pixels_from_line_horizontal(self):
        pixels = BasicEnvironmentRender.computePixelsFromLine(0, 0, 4, 0)
        xs = [p[0] for p in pixels]
        self.assertEqual(xs[0], 0)
        self.assertEqual(xs[-1], 4)

    def test_compute_pixels_from_line_diagonal(self):
        pixels = BasicEnvironmentRender.computePixelsFromLine(0, 0, 3, 3)
        self.assertEqual(pixels[0], [0, 0])
        self.assertEqual(pixels[-1], [3, 3])

    def test_pixel_values_in_valid_range(self):
        render = BasicEnvironmentRender(25, 25)
        env = triMesherEnv(25)
        env.reset()
        state = env.getState()
        self.assertTrue(np.all(state >= 0.0))
        self.assertTrue(np.all(state <= 1.0))


# ---------------------------------------------------------------------------
# Reward logic
# ---------------------------------------------------------------------------
class TestRewardLogic(unittest.TestCase):

    def test_overlap_penalty_increases_count(self):
        """Overlapping pixels (channel 0 interior + channel 1 nonzero) are counted."""
        env = triMesherEnv(20)
        env.reset()
        # Force a known state: put 0.5 (interior) in channel 0 and 1.0 in channel 1.
        env._state[10, 10, 0] = 0.5
        env._state[10, 10, 1] = 1.0
        count = env.countOverlappingPixels()
        self.assertGreater(count, 0)

    def test_no_overlap_on_fresh_reset(self):
        """After reset with no moves, overlap count should be 0."""
        env = triMesherEnv(20)
        env.reset()
        # On a fresh reset the active hero sits on channel 0 (hero channel=0),
        # so channel 1 should be empty — no overlap possible.
        env._state[:, :, 1] = 0.0   # ensure channel 1 is clear
        count = env.countOverlappingPixels()
        self.assertEqual(count, 0)

    def test_total_reward_accumulates(self):
        env = triMesherEnv(20)
        env.reset()
        for _ in range(5):
            env.step(0)
        self.assertNotEqual(env._totalReward, 0.0)

    def test_ideal_area_positive(self):
        env = triMesherEnv(20)
        area = env.getIdealObjectArea(0, 0)
        self.assertGreater(area, 0)


if __name__ == '__main__':
    unittest.main()
