import pytest

from toolkit.net.urlparts import (
    URLError,
    join_url,
    normalize_url,
    remove_dot_segments,
    split_url,
)


# --- split_url ----------------------------------------------------------


def test_split_url_full_url():
    assert split_url("https://ann:pw@example.org:8443/a/b?x=1#top") == {
        "scheme": "https",
        "userinfo": "ann:pw",
        "host": "example.org",
        "port": 8443,
        "path": "/a/b",
        "query": "x=1",
        "fragment": "top",
    }


def test_split_url_keeps_case_and_escapes():
    parts = split_url("HTTP://Example.ORG/%7euser?Q=%41")
    assert parts["scheme"] == "HTTP" and parts["host"] == "Example.ORG"
    assert parts["path"] == "/%7euser" and parts["query"] == "Q=%41"


def test_split_url_without_path_has_empty_path():
    parts = split_url("http://example.org")
    assert parts["path"] == "" and parts["host"] == "example.org"


def test_split_url_question_mark_after_hash_belongs_to_the_fragment():
    parts = split_url("/a/b#x?y")
    assert parts["query"] is None and parts["fragment"] == "x?y" and parts["path"] == "/a/b"


def test_split_url_empty_string():
    parts = split_url("")
    assert parts["path"] == "" and parts["scheme"] is None and parts["host"] is None


def test_split_url_scheme_must_start_with_a_letter():
    parts = split_url("1http://x")
    assert parts["scheme"] is None and parts["host"] is None and parts["path"] == "1http://x"


def test_split_url_colon_in_query_is_not_a_scheme():
    parts = split_url("?a:b")
    assert parts["scheme"] is None and parts["path"] == "" and parts["query"] == "a:b"


def test_split_url_userinfo_without_password():
    parts = split_url("ftp://ann@files.example/pub")
    assert parts["userinfo"] == "ann" and parts["host"] == "files.example"


def test_split_url_colon_in_userinfo_is_not_a_port():
    parts = split_url("http://user:secret@host/")
    assert parts["userinfo"] == "user:secret" and parts["host"] == "host" and parts["port"] is None


def test_split_url_port_with_leading_zeros():
    assert split_url("http://host:0080/")["port"] == 80


def test_split_url_port_above_65535_raises_url_error():
    with pytest.raises(URLError):
        split_url("http://host:65536/")


def test_split_url_non_ascii_digit_port_raises_url_error():
    with pytest.raises(URLError):
        split_url("http://host:\u0668\u0660/")


def test_split_url_ipv6_literal_without_port():
    parts = split_url("http://[::1]/")
    assert parts["host"] == "[::1]" and parts["port"] is None


def test_split_url_text_after_ipv6_literal_raises_url_error():
    with pytest.raises(URLError):
        split_url("http://[::1]x/")


def test_split_url_newline_raises_url_error():
    with pytest.raises(URLError):
        split_url("http://example.org/\n")


# --- join_url -----------------------------------------------------------


def test_join_url_missing_keys_count_as_absent():
    assert join_url({"scheme": "https", "host": "example.org", "path": "/"}) == "https://example.org/"


def test_join_url_empty_query_and_fragment_keep_their_marks():
    assert join_url({"path": "/p", "query": "", "fragment": ""}) == "/p?#"


def test_join_url_scheme_without_host():
    assert join_url({"scheme": "mailto", "path": "ann@example.org"}) == "mailto:ann@example.org"


def test_join_url_relative_path_with_host_raises_url_error():
    with pytest.raises(URLError):
        join_url({"host": "h", "path": "p"})


def test_join_url_does_not_modify_its_argument():
    parts = {"scheme": "http", "host": "h"}
    join_url(parts)
    assert parts == {"scheme": "http", "host": "h"}


# --- remove_dot_segments ------------------------------------------------


def test_remove_dot_segments_path_without_dots_is_unchanged():
    assert remove_dot_segments("/a/b/c") == "/a/b/c"
    assert remove_dot_segments("") == ""


def test_remove_dot_segments_cannot_go_above_the_root():
    assert remove_dot_segments("/../a") == "/a"
    assert remove_dot_segments("/a/../../b") == "/b"


def test_remove_dot_segments_trailing_slash_is_kept():
    assert remove_dot_segments("/a/./b/") == "/a/b/"
    assert remove_dot_segments("/a/b/../") == "/a/"


def test_remove_dot_segments_only_dots():
    assert remove_dot_segments(".") == ""
    assert remove_dot_segments("..") == ""
    assert remove_dot_segments("/.") == "/"
    assert remove_dot_segments("/..") == "/"


def test_remove_dot_segments_escaped_dots_are_not_dots():
    assert remove_dot_segments("/a/%2E%2E/b") == "/a/%2E%2E/b"


# --- normalize_url ------------------------------------------------------


def test_normalize_url_keeps_case_of_userinfo_path_query_fragment():
    assert normalize_url("http://User:PW@h/A?B=C#D") == "http://User:PW@h/A?B=C#D"


def test_normalize_url_keeps_other_ports():
    assert normalize_url("http://example.com:8080/") == "http://example.com:8080/"
    assert normalize_url("http://example.com:443/") == "http://example.com:443/"


def test_normalize_url_empty_path_with_host_becomes_slash():
    assert normalize_url("http://example.com") == "http://example.com/"
    assert normalize_url("http://example.com?x=1") == "http://example.com/?x=1"


def test_normalize_url_decodes_escaped_unreserved_characters():
    assert normalize_url("http://a/%41%62%7e%2d%5F%2e%30") == "http://a/Ab~-_.0"


def test_normalize_url_leaves_incomplete_escapes_alone():
    assert normalize_url("http://a/100%/%4/%zz") == "http://a/100%/%4/%zz"


def test_normalize_url_removes_dot_segments():
    assert normalize_url("http://a/b/./c/../d") == "http://a/b/d"


def test_normalize_url_absolute_path_without_host_loses_dot_segments():
    assert normalize_url("/a/./b/../c") == "/a/c"


def test_normalize_url_everything_at_once():
    url = "HTTP://Example.COM:80/a/./b/../c%7euser/%3f?q=%41%2f#Frag%2e"
    assert normalize_url(url) == "http://example.com/a/c~user/%3F?q=A%2F#Frag."


