import pytest

from toolkit.text.table import render_table


def test_render_table_with_headers_and_separator():
    result = render_table([["ann", "paris"], ["bob", "rome"]], headers=["name", "city"])
    assert result == (
        "| name | city  |\n"
        "|------|-------|\n"
        "| ann  | paris |\n"
        "| bob  | rome  |"
    )


def test_render_table_no_rows_and_no_headers_gives_empty_string():
    assert render_table([]) == ""


def test_render_table_headers_only():
    assert render_table([], headers=["id", "name"]) == "| id | name |\n|----|------|"


def test_render_table_short_rows_are_padded_with_empty_cells():
    assert render_table([["a", "b", "c"], ["d"]]) == "| a | b | c |\n| d |   |   |"


def test_render_table_right_alignment():
    assert render_table([["a", 1], ["bbb", 100]], align="lr") == "| a   |   1 |\n| bbb | 100 |"


def test_render_table_columns_beyond_align_are_left_aligned():
    result = render_table([["a", "b"], ["ccc", "ddd"]], align="r")
    assert result == "|   a | b   |\n| ccc | ddd |"


def test_render_table_invalid_align_character_raises_value_error():
    with pytest.raises(ValueError):
        render_table([["a"]], align="x")


def test_render_table_max_width_truncates_long_cells():
    assert render_table([["abcdefghij", "xy"]], max_width=7) == "| abcd... | xy |"


def test_render_table_max_width_applies_to_converted_values():
    assert render_table([[123456789]], max_width=5) == "| 12... |"


def test_render_table_column_of_empty_cells_has_width_zero():
    assert render_table([["a", ""], ["b", None]]) == "| a |  |\n| b |  |"


def test_render_table_accepts_tuples():
    result = render_table((("a", "b"),), headers=("x", "y"))
    assert result == "| x | y |\n|---|---|\n| a | b |"
