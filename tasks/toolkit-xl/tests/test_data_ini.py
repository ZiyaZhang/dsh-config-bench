import pytest

from toolkit.data.ini import INIError, parse_ini, parse_value


# --- parse_ini ----------------------------------------------------------


def test_parse_ini_empty_text_gives_empty_dict():
    assert parse_ini("") == {}


def test_parse_ini_sections_keep_order_of_first_appearance():
    text = "[zeta]\nk = 1\n[alpha]\nk = 2\n[zeta]\nj = 3\n[mid]\n"
    assert list(parse_ini(text)) == ["zeta", "alpha", "mid"]


def test_parse_ini_no_unnamed_section_without_top_level_keys():
    assert parse_ini("# just a comment\n\n[s]\nk = 2\n") == {"s": {"k": 2}}


def test_parse_ini_blank_lines_are_ignored():
    assert parse_ini("\n\n[s]\n\n  \nk = 1\n\n") == {"s": {"k": 1}}


def test_parse_ini_value_may_contain_equals_sign():
    assert parse_ini("[s]\nformula = a = b + c\n") == {"s": {"formula": "a = b + c"}}


def test_parse_ini_section_without_keys_is_empty_dict():
    assert parse_ini("[empty]\n") == {"empty": {}}


def test_parse_ini_quoted_value_and_inline_comments():
    text = '[s]\npath = "C:\\dir; x" ; the path\nport = 80 # default\n'
    assert parse_ini(text) == {"s": {"path": "C:\\dir; x", "port": 80}}


def test_parse_ini_unclosed_section_header_raises_ini_error():
    with pytest.raises(INIError):
        parse_ini("[section\nk = 1\n")


def test_parse_ini_unclosed_quote_in_value_raises_ini_error():
    with pytest.raises(INIError):
        parse_ini('[s]\nk = "open\n')


# --- parse_value --------------------------------------------------------


def test_parse_value_signed_integers_and_leading_zeros():
    values = [parse_value("-7"), parse_value("+12"), parse_value("007")]
    assert values == [-7, 12, 7]
    assert [type(v) for v in values] == [int, int, int]


def test_parse_value_other_number_like_text_stays_string():
    texts = ["0x1F", "1_000", "1,5", ".", "1.2.3", "12abc"]
    assert [parse_value(text) for text in texts] == texts


def test_parse_value_null_words_give_none():
    assert [parse_value(text) is None for text in ["null", "None", "NULL"]] == [True, True, True]


def test_parse_value_quoted_text_keeps_spaces():
    assert parse_value('"  padded  "') == "  padded  "


def test_parse_value_quoted_text_keeps_comment_characters():
    assert parse_value('"a # b ; c"') == "a # b ; c"


def test_parse_value_comment_directly_after_closing_quote_is_ignored():
    assert parse_value('"text";comment') == "text"


def test_parse_value_inline_comment_after_whitespace_is_removed():
    value = parse_value("8080 # the port")
    assert value == 8080 and type(value) is int


def test_parse_value_that_is_only_a_comment_gives_empty_string():
    assert parse_value("# nothing here") == ""


