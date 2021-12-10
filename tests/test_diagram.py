import unittest
import pytest
import numpy as np
from numpy import pi
tau = pi*2
from numpy import array as ary
from venn.diagram import _rotate_and_scale

class TestPolygonDiagram(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def _pass_fixtures(self, capsys):
        self.capsys = capsys

    def test_rotate(self):
        rotate_11_to_negative11 = _rotate_and_scale([1,1], tau/4, 1)
        np.testing.assert_array_almost_equal(rotate_11_to_negative11, [-1, 1])
        # self.assertListEqual(rotate_1_1_to_1negative1.tolist(), [-1, 1])

    def test_scale_rotate(self):
        negative22 = _rotate_and_scale([1,1], tau/4, 2)
        np.testing.assert_array_almost_equal(negative22, [-2, 2])

    def test_rotate_list(self):
        diag_line = ary([[1,1], [2,2], [3,3]])
        rotated_line = _rotate_and_scale(diag_line, pi, 1)
        np.testing.assert_array_almost_equal(rotated_line, -diag_line)

    def _test_fill_even(self):
        self.assertTrue()
        self.assertEqual((A_count+B_count), num_iter*4, "expecting each model to be fully filled")

    def _test_region_labeling(self):
        with self.capsys.disabled():
            print(model.grid)
            print(label(model.grid))

        self.assertEqual(model.num_regions(), 2)
        self.assertEqual(model.num_regions(connectivity=1), 4)

if __name__=="__main__":
    unittest.main()