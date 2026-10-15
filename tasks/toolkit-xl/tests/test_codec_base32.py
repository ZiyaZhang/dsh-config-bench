import pytest

from toolkit.codec.base32 import (
    Base32Error,
    b32_decode,
    b32_decode_int,
    b32_encode,
    b32_encode_int,
    b32_normalize,
)


# --- b32_encode_int -----------------------------------------------------


def test_b32_encode_int_zero():
    assert b32_encode_int(0) == "0"


def test_b32_encode_int_alphabet_has_no_i_l_o_u():
    symbols = "".join(b32_encode_int(value) for value in range(32))
    assert symbols == "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def test_b32_encode_int_power_of_two_beyond_64_bits():
    assert b32_encode_int(2 ** 70) == "1" + "0" * 14


def test_b32_encode_int_check_symbol_of_zero():
    assert b32_encode_int(0, True) == "00"


def test_b32_encode_int_negative_raises_value_error():
    with pytest.raises(ValueError):
        b32_encode_int(-1)


# --- b32_decode_int -----------------------------------------------------


def test_b32_decode_int_three_symbols():
    assert b32_decode_int("16J") == 1234


def test_b32_decode_int_hyphens_at_both_ends_and_doubled():
    assert b32_decode_int("-1--6J-") == 1234


def test_b32_decode_int_leading_zeros_are_allowed():
    assert b32_decode_int("00Z") == 31


def test_b32_decode_int_is_the_inverse_of_encode_int():
    assert b32_decode_int(b32_encode_int(10 ** 18)) == 10 ** 18


def test_b32_decode_int_letter_u_raises_base32_error():
    with pytest.raises(Base32Error):
        b32_decode_int("1U")


def test_b32_decode_int_trailing_newline_raises_base32_error():
    with pytest.raises(Base32Error):
        b32_decode_int("16J\n")


def test_b32_decode_int_non_ascii_digit_raises_base32_error():
    with pytest.raises(Base32Error):
        b32_decode_int("\u0661")


def test_b32_decode_int_check_symbol_u():
    assert b32_decode_int("14U", True) == 36 and b32_decode_int("14u", True) == 36


def test_b32_decode_int_alias_as_check_symbol():
    assert b32_decode_int("1L", check=True) == 1


def test_b32_decode_int_empty_text_with_check_raises_base32_error():
    with pytest.raises(Base32Error):
        b32_decode_int("", check=True)


# --- b32_encode ---------------------------------------------------------


def test_b32_encode_empty_data():
    assert b32_encode(b"") == ""


def test_b32_encode_five_bytes_need_no_padding_bits():
    assert b32_encode(b"fooba") == "CSQPYRK1"


def test_b32_encode_all_bits_set():
    assert b32_encode(b"\xff") == "ZW" and b32_encode(b"\xff\xff") == "ZZZG"


def test_b32_encode_check_symbol_of_empty_data():
    assert b32_encode(b"", check=True) == "0"


# --- b32_decode ---------------------------------------------------------


def test_b32_decode_empty_text():
    assert b32_decode("") == b""


def test_b32_decode_lower_case_and_hyphens():
    assert b32_decode("csqp-yrk1-e8") == b"foobar"


def test_b32_decode_text_lengths_that_hold_whole_bytes():
    texts = ["CR", "CSQG", "CSQPY", "CSQPYRG", "CSQPYRK1"]
    assert [len(b32_decode(text)) for text in texts] == [1, 2, 3, 4, 5]


def test_b32_decode_three_symbols_raise_base32_error():
    with pytest.raises(Base32Error):
        b32_decode("000")


def test_b32_decode_lowest_left_over_bit_set_raises_base32_error():
    with pytest.raises(Base32Error):
        b32_decode("CSQH")


def test_b32_decode_with_check_symbol():
    assert b32_decode("ZW~", check=True) == b"\xff"


def test_b32_decode_wrong_check_symbol_raises_base32_error():
    with pytest.raises(Base32Error):
        b32_decode("ZW*", check=True)


def test_b32_decode_check_symbol_does_not_count_as_a_data_symbol():
    assert b32_decode("000", check=True) == b"\x00"


# --- b32_normalize ------------------------------------------------------


def test_b32_normalize_empty_text():
    assert b32_normalize("") == ""


def test_b32_normalize_does_not_verify_the_check_symbol():
    assert b32_normalize("16je", check=True) == "16JE"


def test_b32_normalize_empty_text_with_check_raises_base32_error():
    with pytest.raises(Base32Error):
        b32_normalize("", check=True)


