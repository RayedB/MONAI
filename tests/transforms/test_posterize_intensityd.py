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

from monai.transforms import PosterizeIntensity, PosterizeIntensityd
from tests.test_utils import TEST_NDARRAYS, assert_allclose


class TestPosterizeIntensityd(unittest.TestCase):
    def test_array_dict_parity(self):
        img = np.array([[0.0, 1.0], [2.0, 3.0]], dtype=np.float32)
        posterizer = PosterizeIntensity(levels=3)
        posterizerd = PosterizeIntensityd(keys="img", levels=3)
        for p in TEST_NDARRAYS:
            array_result = posterizer(p(img))
            dict_result = posterizerd({"img": p(img)})["img"]
            assert_allclose(dict_result, array_result, type_test="tensor", rtol=1e-7, atol=0)

    def test_two_keys(self):
        img = np.array([[0.0, 1.0], [2.0, 3.0]], dtype=np.float32)
        label = np.array([[5.0, 6.0], [7.0, 8.0]], dtype=np.float32)
        expected_img = np.array([[0.0, 1.5], [1.5, 3.0]], dtype=np.float32)
        expected_label = np.array([[5.0, 6.5], [6.5, 8.0]], dtype=np.float32)
        posterizerd = PosterizeIntensityd(keys=["img", "label"], levels=3)
        for p in TEST_NDARRAYS:
            result = posterizerd({"img": p(img), "label": p(label), "meta": 1})
            assert_allclose(result["img"], p(expected_img), type_test="tensor", rtol=1e-7, atol=0)
            assert_allclose(result["label"], p(expected_label), type_test="tensor", rtol=1e-7, atol=0)
            self.assertEqual(result["meta"], 1)

    def test_allow_missing_keys(self):
        img = np.array([[0.0, 1.0], [2.0, 3.0]], dtype=np.float32)
        expected = np.array([[0.0, 1.5], [1.5, 3.0]], dtype=np.float32)
        posterizerd = PosterizeIntensityd(keys=["img", "label"], levels=3, allow_missing_keys=True)
        for p in TEST_NDARRAYS:
            result = posterizerd({"img": p(img)})
            assert_allclose(result["img"], p(expected), type_test="tensor", rtol=1e-7, atol=0)
            self.assertNotIn("label", result)


if __name__ == "__main__":
    unittest.main()
