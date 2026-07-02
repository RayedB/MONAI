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
from parameterized import parameterized

from monai.transforms import PosterizeIntensity
from tests.test_utils import TEST_NDARRAYS, assert_allclose

TESTS = [
    ["two_levels", np.array([0.0, 1.0, 2.0, 3.0, 4.0], dtype=np.float32), 2, np.array([0.0, 0.0, 4.0, 4.0, 4.0])],
    ["three_levels", np.array([-1.0, 0.0, 1.0, 2.0, 3.0], dtype=np.float32), 3, np.array([-1.0, 1.0, 1.0, 3.0, 3.0])],
]

INVALID_LEVELS = [[0], [-1], [1.5], [True]]


class TestPosterizeIntensity(unittest.TestCase):
    @parameterized.expand(TESTS)
    def test_correctness(self, _, img, levels, expected):
        posterizer = PosterizeIntensity(levels=levels)
        for p in TEST_NDARRAYS:
            result = posterizer(p(img))
            assert_allclose(result, p(expected.astype(img.dtype)), type_test="tensor", rtol=1e-7, atol=0)

    def test_levels_one_uses_global_min(self):
        img = np.array([[2.0, 4.0], [6.0, 8.0]], dtype=np.float32)
        expected = np.full_like(img, 2.0)
        posterizer = PosterizeIntensity(levels=1)
        for p in TEST_NDARRAYS:
            result = posterizer(p(img))
            assert_allclose(result, p(expected), type_test="tensor", rtol=1e-7, atol=0)

    def test_constant_image_is_unchanged(self):
        img = np.full((2, 3), 7.0, dtype=np.float32)
        posterizer = PosterizeIntensity(levels=4)
        for p in TEST_NDARRAYS:
            result = posterizer(p(img))
            assert_allclose(result, p(img), type_test="tensor", rtol=1e-7, atol=0)

    def test_integer_dtype_preserved(self):
        img = np.array([[0, 1, 2, 3, 4]], dtype=np.int16)
        expected = np.array([[0, 2, 2, 4, 4]], dtype=np.int16)
        posterizer = PosterizeIntensity(levels=3)
        for p in TEST_NDARRAYS:
            result = posterizer(p(img))
            assert_allclose(result, p(expected), type_test="tensor")

    def test_deterministic(self):
        img = np.array([[0.0, 1.0], [2.0, 3.0]], dtype=np.float32)
        posterizer = PosterizeIntensity(levels=3)
        for p in TEST_NDARRAYS:
            result = posterizer(p(img))
            repeated = posterizer(p(img))
            assert_allclose(result, repeated, type_test="tensor", rtol=1e-7, atol=0)

    @parameterized.expand(INVALID_LEVELS)
    def test_invalid_levels(self, levels):
        with self.assertRaises(ValueError):
            PosterizeIntensity(levels=levels)


if __name__ == "__main__":
    unittest.main()
