import pytest

from toolkit.codec.hexdump import HexDumpError, ascii_column, format_dump, parse_dump


# --- ascii_column -------------------------------------------------------


def test_ascii_column_printable_characters_are_kept():
    assert ascii_column(b"Hello, world!") == "Hello, world!"


def test_ascii_column_first_and_last_printable_byte():
    assert ascii_column(b"\x1f\x20\x7e\x7f") == ". ~."


def test_ascii_column_accepts_a_bytearray_and_returns_a_str():
    result = ascii_column(bytearray(b"ok\x01"))
    assert type(result) is str and result == "ok."


# --- format_dump: one line ----------------------------------------------


def test_format_dump_short_line_is_filled_with_spaces():
    assert format_dump(b"abc") == "00000000  61 62 63" + " " * 42 + "|abc|"


def test_format_dump_hex_digits_are_lower_case():
    assert format_dump(b"\xab\xcd", width=2) == "00000000  ab cd  |..|"


# --- format_dump: several lines -----------------------------------------


def test_format_dump_second_line_starts_at_offset_sixteen():
    lines = format_dump(bytes(range(65, 82))).split("\n")
    assert lines == [
        "00000000  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|",
        "00000010  51" + " " * 48 + "|Q|",
    ]


def test_format_dump_one_byte_per_line():
    assert format_dump(b"ab", width=1) == "00000000  61  |a|\n00000001  62  |b|"


# --- format_dump: width, group, start -----------------------------------


def test_format_dump_group_larger_than_width():
    assert format_dump(b"abcd", 4, 100) == "00000000  61 62 63 64  |abcd|"


def test_format_dump_group_of_three():
    expected = "00000000  00 01 02  03 04 05  06 07  |........|"
    assert format_dump(bytes(range(8)), width=8, group=3) == expected


def test_format_dump_offset_with_more_than_eight_digits():
    assert format_dump(b"A", width=1, start=2 ** 32) == "100000000  41  |A|"


def test_format_dump_group_zero_raises_value_error():
    with pytest.raises(ValueError):
        format_dump(b"a", group=0)


# --- parse_dump: accepted dumps -----------------------------------------


def test_parse_dump_reads_back_other_widths_and_start_offsets():
    data = bytes(range(256))
    assert parse_dump(format_dump(data, width=7, group=3, start=4096)) == (4096, data)


def test_parse_dump_result_is_a_tuple_of_int_and_bytes():
    result = parse_dump("00000000  41  |A|")
    assert type(result) is tuple and type(result[0]) is int and type(result[1]) is bytes


def test_parse_dump_upper_case_hex_digits():
    assert parse_dump("0000000A  4A 4B  |JK|") == (10, b"JK")


def test_parse_dump_lines_may_have_different_numbers_of_bytes():
    result = parse_dump("00000000  41 42 43  |ABC|\n00000003  44  |D|\n00000004  45 46  |EF|")
    assert result == (0, b"ABCDEF")


def test_parse_dump_space_in_the_text_column():
    assert parse_dump("00000000  61 20 62  |a b|") == (0, b"a b")


# --- parse_dump: errors -------------------------------------------------


def test_parse_dump_other_character_instead_of_the_closing_bar_raises_hexdump_error():
    with pytest.raises(HexDumpError):
        parse_dump("00000000  61 62  |ab!")


def test_parse_dump_bar_only_raises_hexdump_error():
    with pytest.raises(HexDumpError):
        parse_dump("||")


def test_parse_dump_byte_that_is_not_hexadecimal_raises_hexdump_error():
    with pytest.raises(HexDumpError):
        parse_dump("00000000  6g  |a|")


def test_parse_dump_text_column_that_does_not_agree_raises_hexdump_error():
    with pytest.raises(HexDumpError):
        parse_dump("00000000  61 62  |aB|")


def test_parse_dump_gap_in_the_offsets_raises_hexdump_error():
    with pytest.raises(HexDumpError):
        parse_dump("00000000  61  |a|\n00000002  62  |b|")


def test_parse_dump_carriage_return_at_the_line_end_raises_hexdump_error():
    with pytest.raises(HexDumpError):
        parse_dump("00000000  61  |a|\r\n00000001  62  |b|\r\n")


