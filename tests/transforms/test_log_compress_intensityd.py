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

from monai.transforms import LogCompressIntensity, LogCompressIntensityd
from tests.test_utils import TEST_NDARRAYS, assert_allclose


class TestLogCompressIntensityd(unittest.TestCase):
    def test_array_dict_parity(self):
        img = np.array([[0.0, 1.0], [2.0, 10.0]], dtype=np.float32)
        transform = LogCompressIntensity()
        transformd = LogCompressIntensityd(keys="img")
        for p in TEST_NDARRAYS:
            array_result = transform(p(img))
            dict_result = transformd({"img": p(img)})["img"]
            assert_allclose(dict_result, array_result, type_test="tensor", rtol=1e-7, atol=0)

    def test_two_keys(self):
        img = np.array([[0.0, 1.0]], dtype=np.float32)
        label = np.array([[2.0, 10.0]], dtype=np.float32)
        expected_img = np.log1p(img)
        expected_label = np.log1p(label)
        transformd = LogCompressIntensityd(keys=["img", "label"])
        for p in TEST_NDARRAYS:
            data = {"img": p(img), "label": p(label), "meta": 1}
            result = transformd(data)
            assert_allclose(result["img"], p(expected_img), type_test="tensor", rtol=1e-7, atol=0)
            assert_allclose(result["label"], p(expected_label), type_test="tensor", rtol=1e-7, atol=0)
            self.assertEqual(result["meta"], 1)

    def test_allow_missing_keys(self):
        img = np.array([[0.0, 100.0]], dtype=np.float32)
        expected = np.log1p(img)
        transformd = LogCompressIntensityd(keys=["img", "label"], allow_missing_keys=True)
        for p in TEST_NDARRAYS:
            result = transformd({"img": p(img)})
            assert_allclose(result["img"], p(expected), type_test="tensor", rtol=1e-7, atol=0)
            self.assertNotIn("label", result)


if __name__ == "__main__":
    unittest.main()
