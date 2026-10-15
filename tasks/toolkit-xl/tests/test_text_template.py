import pytest

from toolkit.text.template import TemplateError, render_template, template_variables


# --- substitution -------------------------------------------------------


def test_render_text_without_placeholders_is_unchanged():
    assert render_template("plain text, no braces", {}) == "plain text, no braces"


def test_render_whitespace_inside_braces_is_optional():
    result = render_template("{{name}}/{{   name   }}/{{\tname\n}}", {"name": "x"})
    assert result == "x/x/x"


def test_render_none_value_is_empty_text():
    assert render_template("[{{ x }}]", {"x": None}) == "[]"


def test_render_missing_nested_key_raises_key_error():
    with pytest.raises(KeyError):
        render_template("{{ user.email }}", {"user": {"name": "Ann"}})


# --- default ------------------------------------------------------------


def test_render_default_replaces_none():
    assert render_template('{{ name | default:"guest" }}', {"name": None}) == "guest"


def test_render_default_text_is_used_verbatim():
    assert render_template('[{{ x | default:"  two  words " }}]', {}) == "[  two  words ]"


# --- other filters ------------------------------------------------------


def test_render_upper_filter():
    assert render_template("{{ w | upper }}", {"w": "mixed Case"}) == "MIXED CASE"


def test_render_trim_filter():
    assert render_template("[{{ w | trim }}]", {"w": "  padded\n"}) == "[padded]"


def test_render_filters_apply_left_to_right():
    result = render_template("{{ w | trim | length }}/{{ w | length }}", {"w": " ab "})
    assert result == "2/4"


def test_render_missing_value_skips_filters_until_default():
    assert render_template('{{ x | upper | default:"none" }}', {}) == "none"


# --- syntax errors ------------------------------------------------------


def test_render_unknown_filter_raises_template_error():
    with pytest.raises(TemplateError):
        render_template("{{ name | reverse }}", {"name": "Ann"})


def test_render_empty_placeholder_raises_template_error():
    with pytest.raises(TemplateError):
        render_template("{{ }}", {})


def test_render_pipe_inside_default_text_raises_template_error():
    with pytest.raises(TemplateError):
        render_template('{{ x | default:"a|b" }}', {})


# --- literal braces -----------------------------------------------------


def test_render_backslash_escapes_opening_braces():
    result = render_template("\\{{ name }} is {{ name }}", {"name": "Ann"})
    assert result == "{{ name }} is Ann"


def test_render_backslash_not_before_braces_is_literal():
    assert render_template("C:\\dir {{ x }}", {"x": 1}) == "C:\\dir 1"


# --- template_variables -------------------------------------------------


def test_template_variables_keeps_dotted_paths():
    assert template_variables("{{ user.name }} {{ user }}") == ["user.name", "user"]


def test_template_variables_malformed_template_raises_template_error():
    with pytest.raises(TemplateError):
        template_variables("{{ a | nope }}")
