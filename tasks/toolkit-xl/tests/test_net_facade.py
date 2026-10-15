import pytest

import toolkit.net
from toolkit.net.header import HeaderError
from toolkit.net.ipv4 import IPv4Error
from toolkit.net.query import QueryError
from toolkit.net.urlparts import URLError


# --- canonical_url ------------------------------------------------------


def test_canonical_url_normalises_sorts_and_drops_the_fragment():
    url = "HTTP://Example.COM:80/a/../b?z=1&a=2&a=1#top"
    assert toolkit.net.canonical_url(url) == "http://example.com/b?a=2&a=1&z=1"


def test_canonical_url_removes_the_fragment():
    assert toolkit.net.canonical_url("http://h/p#section") == "http://h/p"


def test_canonical_url_drops_a_query_of_empty_pieces():
    assert toolkit.net.canonical_url("http://h/p?&&") == "http://h/p"


def test_canonical_url_sorts_by_decoded_keys():
    assert toolkit.net.canonical_url("http://h/?a%21=2&a+b=1") == "http://h/?a+b=1&a%21=2"


def test_canonical_url_relative_reference():
    assert toolkit.net.canonical_url("/a/./b?y=1&x=2#f") == "/a/b?x=2&y=1"


def test_canonical_url_malformed_escape_in_query_raises_query_error():
    with pytest.raises(QueryError):
        toolkit.net.canonical_url("http://a/?x=%zz")


# --- re-exports ---------------------------------------------------------


def test_net_facade_exposes_urlparts_functions():
    parts = toolkit.net.split_url("http://h/p?q")
    assert parts["host"] == "h" and parts["query"] == "q"
    assert toolkit.net.join_url(parts) == "http://h/p?q"
    assert toolkit.net.remove_dot_segments("/a/../b") == "/b"
    assert toolkit.net.normalize_url("HTTP://H") == "http://h/"


def test_net_facade_error_classes_are_the_classes_of_the_modules():
    with pytest.raises(IPv4Error):
        toolkit.net.parse_ipv4("1.2.3")
    with pytest.raises(HeaderError):
        toolkit.net.parse_media_type("text")
    assert toolkit.net.IPv4Error is IPv4Error
    assert toolkit.net.URLError is URLError
    assert toolkit.net.QueryError is QueryError
    assert toolkit.net.HeaderError is HeaderError


