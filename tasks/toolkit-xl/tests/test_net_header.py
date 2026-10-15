import pytest

from toolkit.net.header import (
    HeaderError,
    best_match,
    format_media_type,
    parse_accept,
    parse_media_type,
)


# --- parse_media_type ---------------------------------------------------


def test_parse_media_type_without_parameters():
    assert parse_media_type("text/html") == ("text/html", {})


def test_parse_media_type_is_lower_cased():
    assert parse_media_type("Text/HTML")[0] == "text/html"


def test_parse_media_type_blanks_around_pieces_are_stripped():
    assert parse_media_type(" \ttext/html ;\tcharset=utf-8  ") == ("text/html", {"charset": "utf-8"})


def test_parse_media_type_token_characters_in_type_and_subtype():
    assert parse_media_type("application/vnd.api+json")[0] == "application/vnd.api+json"
    assert parse_media_type("x-a!#$%&'*+.^_`|~/b")[0] == "x-a!#$%&'*+.^_`|~/b"


def test_parse_media_type_escaped_quote_in_quoted_value():
    assert parse_media_type('a/b; t="say \\"hi\\""')[1] == {"t": 'say "hi"'}


def test_parse_media_type_escaped_backslash_then_closing_quote():
    assert parse_media_type('a/b; t="x\\\\"; u=1')[1] == {"t": "x\\", "u": "1"}


def test_parse_media_type_empty_quoted_value():
    assert parse_media_type('a/b; t=""')[1] == {"t": ""}


def test_parse_media_type_first_of_duplicate_parameters_wins():
    assert parse_media_type("a/b; v=1; v=2")[1] == {"v": "1"}


def test_parse_media_type_empty_value_raises_header_error():
    with pytest.raises(HeaderError):
        parse_media_type("")


def test_parse_media_type_empty_type_raises_header_error():
    with pytest.raises(HeaderError):
        parse_media_type("/html")


def test_parse_media_type_parameter_without_equals_raises_header_error():
    with pytest.raises(HeaderError):
        parse_media_type("text/html; charset")


def test_parse_media_type_empty_unquoted_value_raises_header_error():
    with pytest.raises(HeaderError):
        parse_media_type("text/html; charset=")


def test_parse_media_type_value_with_slash_raises_header_error():
    with pytest.raises(HeaderError):
        parse_media_type("text/html; type=a/b")


def test_parse_media_type_escaped_closing_quote_raises_header_error():
    with pytest.raises(HeaderError):
        parse_media_type('text/html; title="abc\\"')


def test_parse_media_type_text_before_opening_quote_raises_header_error():
    with pytest.raises(HeaderError):
        parse_media_type('text/html; title=abc"def"')


# --- format_media_type --------------------------------------------------


def test_format_media_type_without_parameters():
    assert format_media_type("image/png") == "image/png"


def test_format_media_type_quotes_values_that_are_not_tokens():
    assert format_media_type("a/b", {"t": "hello world"}) == 'a/b; t="hello world"'


def test_format_media_type_params_none_and_empty_dict():
    assert format_media_type("a/b", None) == "a/b" and format_media_type("a/b", params={}) == "a/b"


def test_format_media_type_round_trip_through_parse():
    params = {"charset": "utf-8", "title": 'a "b"; c\\d', "empty": ""}
    assert parse_media_type(format_media_type("text/x-test", params)) == ("text/x-test", params)


# --- parse_accept -------------------------------------------------------


def test_parse_accept_result_types():
    result = parse_accept("text/html;q=0.5")
    assert type(result) is list and type(result[0]) is tuple
    assert type(result[0][1]) is float and type(result[0][2]) is dict


def test_parse_accept_sorts_by_q_descending():
    result = parse_accept("a/a;q=0.2, b/b;q=0.9, c/c;q=0.5")
    assert [entry[0] for entry in result] == ["b/b", "c/c", "a/a"]


def test_parse_accept_equal_keys_keep_header_order():
    result = parse_accept("b/b, a/a, c/c")
    assert [entry[0] for entry in result] == ["b/b", "a/a", "c/c"]


def test_parse_accept_q_zero_entries_are_kept_last():
    assert parse_accept("a/b;q=0, c/d") == [("c/d", 1.0, {}), ("a/b", 0.0, {})]


def test_parse_accept_quoted_q_value_is_accepted():
    assert parse_accept('a/b;q="0.5"') == [("a/b", 0.5, {})]


def test_parse_accept_empty_pieces_are_skipped():
    assert parse_accept(", a/b, ,c/d,") == [("a/b", 1.0, {}), ("c/d", 1.0, {})]


def test_parse_accept_q_above_one_raises_header_error():
    with pytest.raises(HeaderError):
        parse_accept("a/b;q=1.5")


def test_parse_accept_q_one_with_non_zero_decimals_raises_header_error():
    with pytest.raises(HeaderError):
        parse_accept("a/b;q=1.001")


def test_parse_accept_malformed_entry_raises_header_error():
    with pytest.raises(HeaderError):
        parse_accept("text/html, nonsense")


# --- best_match ---------------------------------------------------------


def test_best_match_subtype_wildcard():
    assert best_match(["image/png", "text/css"], "text/*") == "text/css"


def test_best_match_ties_go_to_the_first_available():
    assert best_match(["b/b", "a/a"], "a/a, b/b") == "b/b"
    assert best_match(["a/a", "b/b"], "*/*;q=0.3") == "a/a"


def test_best_match_type_wildcard_beats_full_wildcard():
    accept = "*/*;q=0.9, text/*;q=0.2, image/png;q=0.5"
    assert best_match(["text/plain", "image/png"], accept) == "image/png"


def test_best_match_entry_parameters_must_be_present():
    assert best_match(["text/html"], "text/html;level=1") is None


def test_best_match_more_parameters_are_more_specific():
    accept = "text/html;q=0.9, text/html;level=1;q=0.2"
    assert best_match(["text/html;level=1", "text/plain"], "text/plain;q=0.5, " + accept) == "text/plain"


def test_best_match_empty_header_accepts_the_first_available():
    assert best_match(["a/b", "c/d"], "") == "a/b"
    assert best_match(("c/d", "a/b"), " , ") == "c/d"


def test_best_match_malformed_available_type_raises_header_error():
    with pytest.raises(HeaderError):
        best_match(["text"], "*/*")


def test_best_match_by_keyword_arguments():
    assert best_match(available=["a/b", "c/d"], accept="c/d, a/b;q=0.5") == "c/d"
