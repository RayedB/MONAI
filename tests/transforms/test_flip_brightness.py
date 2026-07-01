# Copyright (c) MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import unittest

import numpy as np

from monai.transforms import FlipBrightness
from tests.test_utils import TEST_NDARRAYS, assert_allclose


class TestFlipBrightness(unittest.TestCase):
    def test_correctness_uint8(self):
        img = np.array([[0, 128], [255, 64]], dtype=np.uint8)
        expected = np.array([[255, 127], [0, 191]], dtype=np.uint8)
        flipper = FlipBrightness()
        for p in TEST_NDARRAYS:
            result = flipper(p(img))
            assert_allclose(result, p(expected), type_test="tensor")

    def test_correctness_float(self):
        img = np.array([[0.0, 0.25], [1.0, 0.5]], dtype=np.float32)
        expected = np.array([[1.0, 0.75], [0.0, 0.5]], dtype=np.float32)
        flipper = FlipBrightness()
        for p in TEST_NDARRAYS:
            result = flipper(p(img))
            assert_allclose(result, p(expected), type_test="tensor", rtol=1e-7, atol=0)

    def test_double_inversion(self):
        img = np.array([[10, 20], [30, 40]], dtype=np.float32)
        flipper = FlipBrightness()
        for p in TEST_NDARRAYS:
            result = flipper(flipper(p(img)))
            assert_allclose(result, p(img), type_test="tensor", rtol=1e-7, atol=0)

    def test_uint8_boundaries(self):
        img = np.array([[0, 255]], dtype=np.uint8)
        expected = np.array([[255, 0]], dtype=np.uint8)
        flipper = FlipBrightness()
        for p in TEST_NDARRAYS:
            result = flipper(p(img))
            assert_allclose(result, p(expected), type_test="tensor")

    def test_int16(self):
        """integers should preserve dtype after inversion."""
        img = np.array([[0, 100], [200, 50]], dtype=np.int16)
        expected = np.array([[200, 100], [0, 150]], dtype=np.int16)
        flipper = FlipBrightness()
        for p in TEST_NDARRAYS:
            result = flipper(p(img))
            assert_allclose(result, p(expected), type_test="tensor")

    def test_negative_values(self):
        img = np.array([[-1.0, 0.0, 1.0]], dtype=np.float32)
        expected = np.array([[1.0, 0.0, -1.0]], dtype=np.float32)
        flipper = FlipBrightness()
        for p in TEST_NDARRAYS:
            result = flipper(p(img))
            assert_allclose(result, p(expected), type_test="tensor", rtol=1e-7, atol=0)

    def test_constant_image(self):
        img = np.full((2, 2), 42, dtype=np.float32)
        flipper = FlipBrightness()
        for p in TEST_NDARRAYS:
            result = flipper(p(img))
            assert_allclose(result, p(img), type_test="tensor", rtol=1e-7, atol=0)

    def test_3d_volume(self):
        img = np.array([[[0, 255], [128, 64]]], dtype=np.uint8)
        expected = np.array([[[255, 0], [127, 191]]], dtype=np.uint8)
        flipper = FlipBrightness()
        for p in TEST_NDARRAYS:
            result = flipper(p(img))
            assert_allclose(result, p(expected), type_test="tensor")
            self.assertEqual(result.shape, img.shape)

    def test_multichannel_global_minmax(self):
        ch0 = np.array([[0, 255]], dtype=np.float32)
        ch1 = np.array([[128, 64]], dtype=np.float32)
        img = np.stack([ch0, ch1])
        expected = np.array([[[255.0, 0.0]], [[127.0, 191.0]]], dtype=np.float32)
        flipper = FlipBrightness()
        for p in TEST_NDARRAYS:
            result = flipper(p(img))
            assert_allclose(result, p(expected), type_test="tensor", rtol=1e-7, atol=0)


if __name__ == "__main__":
    unittest.main()
