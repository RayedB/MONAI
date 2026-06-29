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

from monai.transforms import FlipBrightness, FlipBrightnessd
from tests.test_utils import TEST_NDARRAYS, assert_allclose


class TestFlipBrightnessd(unittest.TestCase):
    def test_array_dict_parity(self):
        img = np.array([[0, 128], [255, 64]], dtype=np.uint8)
        flipper = FlipBrightness()
        flipperd = FlipBrightnessd(keys="img")
        for p in TEST_NDARRAYS:
            array_result = flipper(p(img))
            dict_result = flipperd({"img": p(img)})["img"]
            assert_allclose(dict_result, array_result, type_test="tensor")

    def test_two_keys(self):
        img = np.array([[0, 255]], dtype=np.uint8)
        label = np.array([[128, 64]], dtype=np.uint8)
        expected_img = np.array([[255, 0]], dtype=np.uint8)
        expected_label = np.array([[64, 128]], dtype=np.uint8)
        flipperd = FlipBrightnessd(keys=["img", "label"])
        for p in TEST_NDARRAYS:
            data = {"img": p(img), "label": p(label), "meta": 1}
            result = flipperd(data)
            assert_allclose(result["img"], p(expected_img), type_test="tensor")
            assert_allclose(result["label"], p(expected_label), type_test="tensor")
            self.assertEqual(result["meta"], 1)

    def test_allow_missing_keys(self):
        img = np.array([[0, 255]], dtype=np.uint8)
        expected = np.array([[255, 0]], dtype=np.uint8)
        flipperd = FlipBrightnessd(keys=["img", "label"], allow_missing_keys=True)
        for p in TEST_NDARRAYS:
            result = flipperd({"img": p(img)})
            assert_allclose(result["img"], p(expected), type_test="tensor")
            self.assertNotIn("label", result)


if __name__ == "__main__":
    unittest.main()
