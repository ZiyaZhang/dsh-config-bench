import pytest

from toolkit.net.ipv4 import (
    IPv4Error,
    broadcast_address,
    cidr_contains,
    format_ipv4,
    network_address,
    parse_cidr,
    parse_ipv4,
    split_cidr,
    summarize_addresses,
)


# --- parse_ipv4 ---------------------------------------------------------


def test_parse_ipv4_returns_the_value():
    assert parse_ipv4("192.168.1.10") == 3232235786


def test_parse_ipv4_largest_address():
    assert parse_ipv4("255.255.255.255") == 4294967295


def test_parse_ipv4_five_parts_raise_ipv4_error():
    with pytest.raises(IPv4Error):
        parse_ipv4("1.2.3.4.5")


def test_parse_ipv4_double_zero_raises_ipv4_error():
    with pytest.raises(IPv4Error):
        parse_ipv4("0.0.0.00")


def test_parse_ipv4_trailing_dot_raises_ipv4_error():
    with pytest.raises(IPv4Error):
        parse_ipv4("1.2.3.4.")


def test_parse_ipv4_trailing_newline_raises_ipv4_error():
    with pytest.raises(IPv4Error):
        parse_ipv4("1.2.3.4\n")


def test_parse_ipv4_minus_sign_raises_ipv4_error():
    with pytest.raises(IPv4Error):
        parse_ipv4("-1.2.3.4")


def test_parse_ipv4_hexadecimal_part_raises_ipv4_error():
    with pytest.raises(IPv4Error):
        parse_ipv4("1.2.3.0x4")


def test_parse_ipv4_letter_after_digits_raises_ipv4_error():
    with pytest.raises(IPv4Error):
        parse_ipv4("1.2.3.4x")


# --- format_ipv4 --------------------------------------------------------


def test_format_ipv4_zero():
    assert format_ipv4(0) == "0.0.0.0"


def test_format_ipv4_round_trip():
    assert format_ipv4(parse_ipv4("10.20.30.40")) == "10.20.30.40"
    assert parse_ipv4(format_ipv4(2886729729)) == 2886729729


# --- parse_cidr ---------------------------------------------------------


def test_parse_cidr_returns_network_value_and_length():
    assert parse_cidr("192.168.1.0/24") == (3232235776, 24)


def test_parse_cidr_host_bits_cleared_inside_a_part():
    assert parse_cidr("10.0.0.77/26") == (parse_ipv4("10.0.0.64"), 26)


def test_parse_cidr_without_slash_raises_ipv4_error():
    with pytest.raises(IPv4Error):
        parse_cidr("10.0.0.0")


def test_parse_cidr_empty_length_raises_ipv4_error():
    with pytest.raises(IPv4Error):
        parse_cidr("10.0.0.0/")


def test_parse_cidr_netmask_instead_of_length_raises_ipv4_error():
    with pytest.raises(IPv4Error):
        parse_cidr("10.0.0.0/255.0.0.0")


def test_parse_cidr_malformed_address_raises_ipv4_error():
    with pytest.raises(IPv4Error):
        parse_cidr("10.0.0.256/8")


# --- network_address, broadcast_address ---------------------------------


def test_network_address_of_length_zero():
    assert network_address("10.9.8.7/0") == "0.0.0.0"


def test_broadcast_address_of_length_32_is_the_address():
    assert broadcast_address("10.9.8.7/32") == "10.9.8.7"


def test_broadcast_address_with_odd_length():
    assert broadcast_address("172.16.99.200/20") == "172.16.111.255"


# --- cidr_contains ------------------------------------------------------


def test_cidr_contains_address_inside():
    assert cidr_contains("10.0.0.0/8", "10.200.3.4") is True


def test_cidr_contains_address_just_outside():
    assert cidr_contains("192.168.1.0/24", "192.168.0.255") is False
    assert cidr_contains("192.168.1.0/24", "192.168.2.0") is False


def test_cidr_contains_itself():
    assert cidr_contains("10.1.0.0/16", "10.1.0.0/16") is True


def test_cidr_contains_other_network_elsewhere_is_false():
    assert cidr_contains("10.0.0.0/8", "192.168.0.0/16") is False


def test_cidr_contains_malformed_address_raises_ipv4_error():
    with pytest.raises(IPv4Error):
        cidr_contains("10.0.0.0/8", "10.0.0")


# --- split_cidr ---------------------------------------------------------


def test_split_cidr_into_four_subnets():
    assert split_cidr("192.168.0.0/24", 26) == [
        "192.168.0.0/26",
        "192.168.0.64/26",
        "192.168.0.128/26",
        "192.168.0.192/26",
    ]


def test_split_cidr_clears_host_bits_first():
    assert split_cidr("10.1.2.3/8", 8) == ["10.0.0.0/8"]
    assert split_cidr("192.168.5.77/24", 25) == ["192.168.5.0/25", "192.168.5.128/25"]


def test_split_cidr_shorter_new_length_raises_ipv4_error():
    with pytest.raises(IPv4Error):
        split_cidr("10.0.0.0/24", 16)


def test_split_cidr_by_keyword_returns_a_list():
    result = split_cidr(cidr="10.0.0.0/31", new_length=32)
    assert type(result) is list and result == ["10.0.0.0/32", "10.0.0.1/32"]


# --- summarize_addresses ------------------------------------------------


def test_summarize_addresses_run_of_two_is_a_range():
    assert summarize_addresses(["10.0.0.1", "10.0.0.2"]) == ["10.0.0.1-10.0.0.2"]


def test_summarize_addresses_sorts_by_value_not_by_text():
    assert summarize_addresses(["10.0.0.10", "10.0.0.9", "10.0.0.100"]) == [
        "10.0.0.9-10.0.0.10",
        "10.0.0.100",
    ]


def test_summarize_addresses_runs_cross_part_boundaries():
    assert summarize_addresses(["10.0.1.0", "10.0.0.255", "10.0.0.254"]) == [
        "10.0.0.254-10.0.1.0"
    ]


def test_summarize_addresses_extreme_values():
    assert summarize_addresses(["255.255.255.255", "0.0.0.0", "255.255.255.254"]) == [
        "0.0.0.0",
        "255.255.255.254-255.255.255.255",
    ]


