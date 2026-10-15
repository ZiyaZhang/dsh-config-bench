import pytest

import toolkit.text
from toolkit.text.template import TemplateError


# --- toc ----------------------------------------------------------------


def test_toc_renders_numbered_table_with_anchors():
    assert toolkit.text.toc(["Install", "Usage"]) == (
        "| # | Title   | Anchor   |\n"
        "|---|---------|----------|\n"
        "| 1 | Install | #install |\n"
        "| 2 | Usage   | #usage   |"
    )


def test_toc_number_column_is_right_aligned():
    titles = ["t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9", "t10"]
    lines = toolkit.text.toc(titles).split("\n")
    assert lines[0] == "|  # | Title | Anchor |"
    assert lines[2] == "|  1 | t1    | #t1    |"
    assert lines[11] == "| 10 | t10   | #t10   |"


def test_toc_anchor_number_skips_slug_taken_by_another_title():
    lines = toolkit.text.toc(["FAQ", "FAQ 2", "FAQ"]).split("\n")
    assert lines[2:] == [
        "| 1 | FAQ   | #faq   |",
        "| 2 | FAQ 2 | #faq-2 |",
        "| 3 | FAQ   | #faq-3 |",
    ]


# --- re-exports ---------------------------------------------------------


def test_facade_exposes_render_table():
    assert toolkit.text.render_table([["a", "b"]]) == "| a | b |"


def test_text_facade_template_error_is_the_class_of_the_template_module():
    with pytest.raises(TemplateError):
        toolkit.text.render_template("{{ a", {})
    assert toolkit.text.TemplateError is TemplateError
