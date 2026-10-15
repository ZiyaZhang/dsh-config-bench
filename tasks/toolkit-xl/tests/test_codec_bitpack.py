import pytest

from toolkit.codec.bitpack import (
    BitPackError,
    decode_uvarint,
    decode_uvarints,
    encode_uvarint,
    encode_uvarints,
    pack_bits,
    unpack_bits,
)


# --- pack_bits ----------------------------------------------------------


def test_pack_bits_two_fields_in_one_byte():
    assert pack_bits([5, 1], [3, 1]) == b"\xb0"


def test_pack_bits_no_fields_give_empty_bytes():
    assert pack_bits([], []) == b""


def test_pack_bits_exactly_one_byte_has_no_padding():
    assert pack_bits([255], [8]) == b"\xff"


def test_pack_bits_sixteen_bit_field_is_big_endian():
    assert pack_bits([0x1234], [16]) == b"\x12\x34"


def test_pack_bits_field_wider_than_32_bits():
    assert pack_bits([2 ** 40 - 1], [40]) == b"\xff\xff\xff\xff\xff"


def test_pack_bits_does_not_modify_its_arguments():
    values, widths = [5, 1], [3, 1]
    pack_bits(values, widths)
    assert values == [5, 1] and widths == [3, 1]


def test_pack_bits_width_zero_raises_value_error():
    with pytest.raises(ValueError):
        pack_bits([0], [0])


def test_pack_bits_more_widths_than_values_raise_value_error():
    with pytest.raises(ValueError):
        pack_bits([1], [4, 4])


# --- unpack_bits --------------------------------------------------------


def test_unpack_bits_field_across_a_byte_border():
    assert unpack_bits(b"\xbf\xf8", [1, 1, 1, 10]) == [1, 0, 1, 1023]


def test_unpack_bits_sixteen_bit_field():
    assert unpack_bits(b"\x12\x34", [16]) == [0x1234]


def test_unpack_bits_same_data_with_other_widths():
    assert unpack_bits(b"\x12\x34", [4, 4, 4, 4]) == [1, 2, 3, 4]


def test_unpack_bits_highest_padding_bit_set_raises_bitpack_error():
    with pytest.raises(BitPackError):
        unpack_bits(b"\xb8", [3, 1])


def test_unpack_bits_empty_data_for_fields_raises_bitpack_error():
    with pytest.raises(BitPackError):
        unpack_bits(b"", [3, 1])


def test_unpack_bits_error_is_a_value_error():
    with pytest.raises(ValueError):
        unpack_bits(b"\xff\xff", [3])


# --- encode_uvarint -----------------------------------------------------


def test_encode_uvarint_smallest_two_byte_value():
    assert encode_uvarint(128) == b"\x80\x01"


def test_encode_uvarint_smallest_three_byte_value():
    assert encode_uvarint(16384) == b"\x80\x80\x01"


def test_encode_uvarint_result_is_bytes():
    assert type(encode_uvarint(5)) is bytes


# --- decode_uvarint -----------------------------------------------------


def test_decode_uvarint_zero():
    assert decode_uvarint(b"\x00") == (0, 1)


def test_decode_uvarint_at_an_offset():
    assert decode_uvarint(b"\x05\xac\x02\x07", 1) == (300, 3)


def test_decode_uvarint_zero_byte_after_a_continuation_byte_of_an_earlier_varint():
    assert decode_uvarint(b"\x80\x00", 1) == (0, 2)


def test_decode_uvarint_empty_data_raises_bitpack_error():
    with pytest.raises(BitPackError):
        decode_uvarint(b"")


def test_decode_uvarint_offset_at_the_end_raises_bitpack_error():
    with pytest.raises(BitPackError):
        decode_uvarint(b"\x05", 1)


def test_decode_uvarint_trailing_zero_byte_raises_bitpack_error():
    with pytest.raises(BitPackError):
        decode_uvarint(b"\xac\x82\x00")


# --- encode_uvarints, decode_uvarints -----------------------------------


def test_encode_uvarints_of_no_numbers():
    assert encode_uvarints([]) == b""


def test_decode_uvarints_reads_all_varints():
    assert decode_uvarints(b"\x01\xac\x02\x00") == [1, 300, 0]


def test_decode_uvarints_is_the_inverse_of_encode_uvarints():
    numbers = [0, 1, 127, 128, 16383, 16384, 2 ** 32, 2 ** 64, 5]
    assert decode_uvarints(encode_uvarints(numbers)) == numbers


