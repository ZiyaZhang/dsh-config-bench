import pytest

import toolkit.codec
from toolkit.codec.base32 import Base32Error
from toolkit.codec.bitpack import BitPackError
from toolkit.codec.hexdump import HexDumpError
from toolkit.codec.rle import RLEError


# --- pack_id ------------------------------------------------------------


def test_pack_id_one_byte_and_its_check_symbol():
    assert toolkit.codec.pack_id([5, 1], [3, 1]) == "P0W"


def test_pack_id_groups_of_three():
    assert toolkit.codec.pack_id([2024, 12, 31, 999999], [12, 4, 5, 20], 3) == "FT6-FZ8-8ZG-00"


def test_pack_id_check_symbol_counts_as_a_symbol_of_its_group():
    assert toolkit.codec.pack_id([0xABCD], [16]) == "NF6G-S"


def test_pack_id_zero_fields_keep_their_symbols():
    assert toolkit.codec.pack_id([0, 0], [8, 8]) == "0000-0"


def test_pack_id_value_that_does_not_fit_raises_value_error():
    with pytest.raises(ValueError):
        toolkit.codec.pack_id([16], [4])


# --- re-exports ---------------------------------------------------------


def test_codec_facade_exposes_base32_functions():
    assert toolkit.codec.b32_encode(b"f") == "CR"
    assert toolkit.codec.b32_decode("CR") == b"f"
    assert toolkit.codec.b32_encode_int(1234) == "16J"
    assert toolkit.codec.b32_decode_int("16J") == 1234
    assert toolkit.codec.b32_normalize("oil") == "011"


def test_codec_facade_exposes_bitpack_functions():
    assert toolkit.codec.pack_bits([5, 1], [3, 1]) == b"\xb0"
    assert toolkit.codec.unpack_bits(b"\xb0", [3, 1]) == [5, 1]
    assert toolkit.codec.encode_uvarint(300) == b"\xac\x02"
    assert toolkit.codec.decode_uvarint(b"\xac\x02") == (300, 2)
    assert toolkit.codec.encode_uvarints([1, 2]) == b"\x01\x02"
    assert toolkit.codec.decode_uvarints(b"\x01\x02") == [1, 2]


