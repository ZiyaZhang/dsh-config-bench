# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/variable-length-quantity/canonical-data.json
# File last updated on 2023-07-19

import unittest

from variable_length_quantity import (
    decode,
    encode,
)


class VariableLengthQuantityTest(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(encode([0x0]), [0x0])

    def test_smallest_double_byte(self):
        self.assertEqual(encode([0x80]), [0x81, 0x0])

    def test_smallest_triple_byte(self):
        self.assertEqual(encode([0x4000]), [0x81, 0x80, 0x0])

    def test_smallest_quadruple_byte(self):
        self.assertEqual(encode([0x200000]), [0x81, 0x80, 0x80, 0x0])

    def test_smallest_quintuple_byte(self):
        self.assertEqual(encode([0x10000000]), [0x81, 0x80, 0x80, 0x80, 0x0])

    def test_two_single_byte_values(self):
        self.assertEqual(encode([0x40, 0x7F]), [0x40, 0x7F])

    def test_one_byte(self):
        self.assertEqual(decode([0x7F]), [0x7F])

    def test_four_bytes(self):
        self.assertEqual(decode([0x81, 0x80, 0x80, 0x0]), [0x200000])

    def test_incomplete_sequence_causes_error_even_if_value_is_zero(self):
        with self.assertRaises(ValueError) as err:
            decode([0x80])
        self.assertEqual(type(err.exception), ValueError)
        self.assertEqual(err.exception.args[0], "incomplete sequence")
