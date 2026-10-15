import pytest

from toolkit.data.csvlite import CSVError, format_csv, parse_csv, parse_records


# --- parse_csv ----------------------------------------------------------


def test_parse_csv_single_record():
    assert parse_csv("a,b,c") == [["a", "b", "c"]]


def test_parse_csv_final_newline_adds_no_record():
    assert parse_csv("a,b\n1,2\n") == [["a", "b"], ["1", "2"]]


def test_parse_csv_only_a_newline_gives_one_empty_field():
    assert parse_csv("\n") == [[""]]


def test_parse_csv_keeps_whitespace():
    assert parse_csv(" a , b\t,c ") == [[" a ", " b\t", "c "]]


def test_parse_csv_quoted_field_with_line_break():
    assert parse_csv('"line1\nline2",x\ny') == [["line1\nline2", "x"], ["y"]]


def test_parse_csv_quoted_field_at_end_of_record_with_crlf():
    assert parse_csv('a,"b"\r\nc') == [["a", "b"], ["c"]]


def test_parse_csv_lone_carriage_return_is_ordinary_character():
    assert parse_csv("a\rb,c") == [["a\rb", "c"]]


def test_parse_csv_unterminated_quote_raises_csv_error():
    with pytest.raises(CSVError):
        parse_csv('a,"bc')


def test_parse_csv_custom_delimiter():
    assert parse_csv("a;b,c;d", delimiter=";") == [["a", "b,c", "d"]]


def test_parse_csv_quote_as_delimiter_raises_value_error():
    with pytest.raises(ValueError):
        parse_csv("a,b", delimiter='"')


# --- format_csv ---------------------------------------------------------


def test_format_csv_quotes_field_with_delimiter():
    assert format_csv([["a,b", "c"]]) == '"a,b",c\n'


def test_format_csv_does_not_quote_spaces_or_empty_fields():
    assert format_csv([[" padded ", "", "x"]]) == " padded ,,x\n"


def test_format_csv_row_without_fields_is_empty_line():
    assert format_csv([["a"], [], ["b"]]) == "a\n\nb\n"


# --- parse_records ------------------------------------------------------


def test_parse_records_maps_header_to_fields():
    result = parse_records("name,age\nann,3\nbob,5\n")
    assert result == [{"name": "ann", "age": "3"}, {"name": "bob", "age": "5"}]


def test_parse_records_short_row_is_filled_with_empty_strings():
    assert parse_records("a,b,c\n1\n") == [{"a": "1", "b": "", "c": ""}]


def test_parse_records_custom_delimiter():
    assert parse_records("k|v\nx|1", delimiter="|") == [{"k": "x", "v": "1"}]


