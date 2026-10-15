import pytest

from toolkit.graph.paths import (
    NegativeWeightError,
    path_weight,
    shortest_distances,
    shortest_path,
)


# --- shortest_distances -------------------------------------------------


def test_shortest_distances_single_node():
    assert shortest_distances({"a": {}}, "a") == {"a": 0}


def test_shortest_distances_unreachable_nodes_are_left_out():
    graph = {"a": {"b": 1}, "c": {"a": 1}, "d": {}}
    assert shortest_distances(graph, "a") == {"a": 0, "b": 1}


def test_shortest_distances_zero_weight_edge():
    graph = {"a": {"b": 0}, "b": {"c": 2}}
    assert shortest_distances(graph, "a") == {"a": 0, "b": 0, "c": 2}


def test_shortest_distances_larger_example():
    graph = {
        "a": {"b": 7, "c": 9, "f": 14},
        "b": {"c": 10, "d": 15},
        "c": {"d": 11, "f": 2},
        "d": {"e": 6},
        "f": {"e": 9},
    }
    assert shortest_distances(graph, "a") == {"a": 0, "b": 7, "c": 9, "f": 11, "e": 20, "d": 20}


def test_shortest_distances_key_order_with_zero_weight_edge():
    graph = {"s": {"z": 5}, "z": {"a": 0}}
    assert list(shortest_distances(graph, "s")) == ["s", "a", "z"]


def test_shortest_distances_float_weights():
    graph = {"a": {"b": 0.5}, "b": {"c": 0.25}}
    result = shortest_distances(graph, "a")
    assert result["c"] == pytest.approx(0.75, rel=1e-9, abs=1e-9)


def test_shortest_distances_unknown_source_raises_key_error():
    with pytest.raises(KeyError):
        shortest_distances({"a": {"b": 1}}, "q")


def test_shortest_distances_negative_weight_on_unreachable_edge_raises():
    with pytest.raises(NegativeWeightError):
        shortest_distances({"a": {"b": 1}, "x": {"y": -0.5}}, "a")


def test_shortest_distances_does_not_modify_the_graph():
    graph = {"a": {"b": 1}}
    shortest_distances(graph, "a")
    assert graph == {"a": {"b": 1}}


# --- shortest_path ------------------------------------------------------


def test_shortest_path_to_itself_ignores_cycles():
    assert shortest_path({"a": {"b": 0}, "b": {"a": 0}}, "a", "a") == ["a"]


def test_shortest_path_weight_counts_more_than_number_of_edges():
    graph = {"a": {"d": 4, "b": 1}, "b": {"c": 1}, "c": {"d": 1}}
    assert shortest_path(graph, "a", "d") == ["a", "b", "c", "d"]


def test_shortest_path_equal_weight_prefers_fewer_edges():
    graph = {"a": {"b": 1, "c": 2}, "b": {"c": 1}}
    assert shortest_path(graph, "a", "c") == ["a", "c"]


def test_shortest_path_smallest_list_is_decided_at_the_first_difference():
    graph = {"a": {"b": 1, "c": 1}, "b": {"e": 1}, "c": {"d": 1}, "d": {"z": 1}, "e": {"z": 1}}
    assert shortest_path(graph, "a", "z") == ["a", "b", "e", "z"]


def test_shortest_path_tie_with_different_weights_on_the_way():
    graph = {"a": {"b": 3, "c": 1}, "b": {"d": 1}, "c": {"d": 3}}
    assert shortest_path(graph, "a", "d") == ["a", "b", "d"]


def test_shortest_path_integer_nodes_are_compared_as_numbers():
    graph = {1: {10: 1, 2: 1}, 10: {3: 1}, 2: {3: 1}}
    assert shortest_path(graph, 1, 3) == [1, 2, 3]


def test_shortest_path_larger_example():
    graph = {
        "a": {"b": 7, "c": 9, "f": 14},
        "b": {"c": 10, "d": 15},
        "c": {"d": 11, "f": 2},
        "d": {"e": 6},
        "f": {"e": 9},
    }
    assert shortest_path(graph, "a", "e") == ["a", "c", "f", "e"]


def test_shortest_path_negative_weight_raises():
    with pytest.raises(NegativeWeightError):
        shortest_path({"a": {"b": 1}, "x": {"y": -2}}, "a", "b")


# --- path_weight --------------------------------------------------------


def test_path_weight_of_single_node_is_zero():
    assert path_weight({"a": {"b": 5}}, ["a"]) == 0


def test_path_weight_accepts_a_tuple():
    assert path_weight({"a": {"b": 2}, "b": {"c": 3}}, ("a", "b", "c")) == 5


def test_path_weight_need_not_be_the_cheapest_path():
    graph = {"a": {"b": 10, "c": 1}, "c": {"b": 2}}
    assert path_weight(graph, ["a", "b"]) == 10


def test_path_weight_missing_edge_raises_value_error():
    with pytest.raises(ValueError):
        path_weight({"a": {"b": 1}, "c": {}}, ["a", "c"])


def test_path_weight_unknown_node_raises_key_error():
    with pytest.raises(KeyError):
        path_weight({"a": {"b": 1}}, ["a", "q"])


