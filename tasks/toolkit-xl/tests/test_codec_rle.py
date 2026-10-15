import pytest

from toolkit.codec.rle import (
    RLEError,
    rle_decode,
    rle_decode_bytes,
    rle_encode,
    rle_encode_bytes,
    rle_runs,
)


# --- rle_runs -----------------------------------------------------------


def test_rle_runs_of_a_string():
    assert rle_runs("aaabcc") == [("a", 3), ("b", 1), ("c", 2)]


def test_rle_runs_of_a_list():
    assert rle_runs([1, 1, 2, 1]) == [(1, 2), (2, 1), (1, 1)]


def test_rle_runs_result_is_a_list_of_tuples():
    result = rle_runs("ab")
    assert type(result) is list and [type(run) for run in result] == [tuple, tuple]


# --- rle_encode ---------------------------------------------------------


def test_rle_encode_empty_string():
    assert rle_encode("") == ""


def test_rle_encode_run_of_spaces():
    assert rle_encode("a  b") == "a2 b"


def test_rle_encode_runs_of_digits_are_escaped():
    assert rle_encode("a1122") == "a2\\12\\2"


def test_rle_encode_run_of_backslashes():
    assert rle_encode("\\\\\\") == "3\\\\"


def test_rle_encode_non_ascii_letters():
    assert rle_encode("\u00e9\u00e9a") == "2\u00e9a"


# --- rle_decode ---------------------------------------------------------


def test_rle_decode_runs_and_single_characters():
    assert rle_decode("3ab2c") == "aaabcc"


def test_rle_decode_length_with_two_digits():
    assert rle_decode("12x") == "x" * 12


def test_rle_decode_single_escaped_digit():
    assert rle_decode("\\7") == "7"


def test_rle_decode_run_of_spaces():
    assert rle_decode("a2 b") == "a  b"


def test_rle_decode_length_at_the_end_raises_rle_error():
    with pytest.raises(RLEError):
        rle_decode("3")


def test_rle_decode_length_and_backslash_at_the_end_raise_rle_error():
    with pytest.raises(RLEError):
        rle_decode("3\\")


def test_rle_decode_length_one_raises_rle_error():
    with pytest.raises(RLEError):
        rle_decode("1a")


def test_rle_decode_two_runs_of_the_same_character_raise_rle_error():
    with pytest.raises(RLEError):
        rle_decode("2a3a")


def test_rle_decode_error_is_a_value_error():
    with pytest.raises(ValueError):
        rle_decode("5")


# --- rle_encode_bytes ---------------------------------------------------


def test_rle_encode_bytes_without_runs():
    assert rle_encode_bytes(b"abc") == "61 62 63"


def test_rle_encode_bytes_hex_digits_are_lower_case():
    assert rle_encode_bytes(b"\xab\xab\xcd") == "ab*2 cd"


# --- rle_decode_bytes ---------------------------------------------------


def test_rle_decode_bytes_empty_text():
    assert rle_decode_bytes("") == b""


def test_rle_decode_bytes_is_the_inverse_of_encode_bytes():
    data = bytes(range(256)) + b"\x00\x00\xff\xff\xff\x10"
    assert rle_decode_bytes(rle_encode_bytes(data)) == data


def test_rle_decode_bytes_trailing_space_raises_rle_error():
    with pytest.raises(RLEError):
        rle_decode_bytes("00 ")


def test_rle_decode_bytes_length_zero_raises_rle_error():
    with pytest.raises(RLEError):
        rle_decode_bytes("00*0")


def test_rle_decode_bytes_same_byte_in_two_runs_raises_rle_error():
    with pytest.raises(RLEError):
        rle_decode_bytes("00*2 00")


def test_rle_decode_bytes_invalid_hex_digit_raises_rle_error():
    with pytest.raises(RLEError):
        rle_decode_bytes("0g")


def test_rle_decode_bytes_newline_as_separator_raises_rle_error():
    with pytest.raises(RLEError):
        rle_decode_bytes("00\nff")
