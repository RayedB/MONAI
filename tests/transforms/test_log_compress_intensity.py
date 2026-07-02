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
import torch

from monai.transforms import LogCompressIntensity
from tests.test_utils import TEST_NDARRAYS, assert_allclose


class TestLogCompressIntensity(unittest.TestCase):
    def test_known_values(self):
        img = np.array([0.0, 1.0, 2.0, 10.0, 100.0], dtype=np.float32)
        expected = np.log1p(img)
        transform = LogCompressIntensity()
        for p in TEST_NDARRAYS:
            result = transform(p(img))
            assert_allclose(result, p(expected), type_test="tensor", rtol=1e-7, atol=0)

    def test_long_tail_compression(self):
        a, b = 1.0, 1000.0
        self.assertLess(np.log1p(a), np.log1p(b))
        linear_ratio = b / a
        log_ratio = np.log1p(b) / np.log1p(a)
        self.assertLess(log_ratio, linear_ratio)

        img = np.array([a, b], dtype=np.float32)
        expected = np.log1p(img)
        transform = LogCompressIntensity()
        for p in TEST_NDARRAYS:
            result = transform(p(img))
            assert_allclose(result, p(expected), type_test="tensor", rtol=1e-7, atol=0)

    def test_zero_and_near_zero(self):
        img = np.array([0.0, 1e-8, 1e-4], dtype=np.float64)
        expected = np.log1p(img)
        transform = LogCompressIntensity()
        for p in TEST_NDARRAYS:
            result = transform(p(img))
            assert_allclose(result, p(expected), type_test="tensor", rtol=1e-7, atol=0)

    def test_negative_above_threshold(self):
        img = np.array([-0.5, 0.0, 1.0], dtype=np.float32)
        expected = np.log1p(img)
        transform = LogCompressIntensity()
        for p in TEST_NDARRAYS:
            result = transform(p(img))
            assert_allclose(result, p(expected), type_test="tensor", rtol=1e-7, atol=0)

    def test_negative_at_and_below_threshold(self):
        img = np.array([-1.0, -1.1], dtype=np.float32)
        expected = np.log1p(img)
        transform = LogCompressIntensity()
        for p in TEST_NDARRAYS:
            result = transform(p(img))
            assert_allclose(result, p(expected), type_test="tensor", rtol=1e-7, atol=0, equal_nan=True)

    def test_integer_dtypes_promote_to_float32(self):
        for dtype in (np.uint8, np.int16):
            img = np.array([[0, 1], [2, 10]], dtype=dtype)
            expected = np.log1p(img.astype(np.float32))
            transform = LogCompressIntensity()
            for p in TEST_NDARRAYS:
                result = transform(p(img))
                assert_allclose(result, p(expected), type_test="tensor", rtol=1e-7, atol=0)
                self.assertEqual(result.dtype, torch.float32)

    def test_2d_and_3d_shapes(self):
        transform = LogCompressIntensity()
        for shape in ((4, 5), (2, 4, 5)):
            img = np.arange(np.prod(shape), dtype=np.float32).reshape(shape)
            expected = np.log1p(img)
            for p in TEST_NDARRAYS:
                result = transform(p(img))
                assert_allclose(result, p(expected), type_test="tensor", rtol=1e-7, atol=0)
                self.assertEqual(result.shape, img.shape)

    def test_multichannel(self):
        img = np.stack(
            [
                np.array([[0.0, 1.0], [2.0, 10.0]], dtype=np.float32),
                np.array([[100.0, 50.0], [25.0, 5.0]], dtype=np.float32),
            ]
        )
        expected = np.log1p(img)
        transform = LogCompressIntensity()
        for p in TEST_NDARRAYS:
            result = transform(p(img))
            assert_allclose(result, p(expected), type_test="tensor", rtol=1e-7, atol=0)
            self.assertEqual(result.shape, img.shape)


if __name__ == "__main__":
    unittest.main()
