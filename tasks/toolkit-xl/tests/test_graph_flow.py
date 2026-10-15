import pytest

from toolkit.graph.flow import (
    bfs_order,
    degree_summary,
    degrees,
    dfs_order,
    is_bipartite,
    two_colouring,
)


# --- degrees ------------------------------------------------------------


def test_degrees_empty_graph_gives_empty_dict():
    assert degrees({}) == {}


def test_degrees_keys_are_in_ascending_order():
    result = degrees({"c": ["a"], "b": ["d"]})
    assert list(result) == ["a", "b", "c", "d"]


def test_degrees_self_loop_next_to_other_edges():
    assert degrees({"a": ["a", "b"], "b": ["a"]}) == {"a": (2, 2), "b": (1, 1)}


def test_degrees_values_may_be_tuples_and_sets():
    graph = {"a": ("b", "c"), "b": {"c"}, "c": frozenset(["a"])}
    assert degrees(graph) == {"a": (1, 2), "b": (1, 1), "c": (2, 1)}


# --- degree_summary -----------------------------------------------------


def test_degree_summary_example():
    graph = {"b": ["c", "a", "c"], "a": ["a"], "d": []}
    assert degree_summary(graph) == {
        "nodes": 4,
        "edges": 3,
        "sources": ["b", "d"],
        "sinks": ["c", "d"],
        "isolated": ["d"],
    }


def test_degree_summary_counts_different_edges():
    assert degree_summary({"a": ["b", "b"], "b": ["a"]})["edges"] == 2


def test_degree_summary_sinks_are_sorted():
    assert degree_summary({"m": ["z", "c", "k"]})["sinks"] == ["c", "k", "z"]


def test_degree_summary_counts_are_ints():
    result = degree_summary({"a": ["b"]})
    assert type(result["nodes"]) is int and type(result["edges"]) is int


# --- two_colouring ------------------------------------------------------


def test_two_colouring_edge_gives_different_colours():
    assert two_colouring({"a": ["b"]}) == {"a": 0, "b": 1}


def test_two_colouring_direction_is_ignored():
    assert two_colouring({"a": ["c"], "b": ["c"]}) == {"a": 0, "b": 0, "c": 1}


def test_two_colouring_undirected_triangle_gives_none():
    assert two_colouring({"a": ["b", "c"], "b": ["c"]}) is None


def test_two_colouring_odd_cycle_in_a_later_component_gives_none():
    graph = {"a": ["b"], "x": ["y"], "y": ["z"], "z": ["x"]}
    assert two_colouring(graph) is None


def test_two_colouring_integers_are_compared_as_numbers():
    assert two_colouring({10: [9]}) == {9: 0, 10: 1}


# --- is_bipartite -------------------------------------------------------


def test_is_bipartite_tree_is_true():
    assert is_bipartite({"a": ["b", "c"], "c": ["d"]}) is True


def test_is_bipartite_self_loop_is_false():
    assert is_bipartite({"a": ["a"]}) is False


# --- bfs_order ----------------------------------------------------------


def test_bfs_order_visits_level_by_level():
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["e"]}
    assert bfs_order(graph, "a") == ["a", "b", "c", "d", "e"]


def test_bfs_order_leaves_out_unreachable_nodes():
    graph = {"a": ["b"], "c": ["a"], "d": []}
    assert bfs_order(graph, "a") == ["a", "b"]


def test_bfs_order_integers_are_compared_as_numbers():
    assert bfs_order({1: [10, 9, 100]}, 1) == [1, 9, 10, 100]


def test_bfs_order_self_loop():
    assert bfs_order({"a": ["a", "b"]}, "a") == ["a", "b"]


# --- dfs_order ----------------------------------------------------------


def test_dfs_order_successors_in_ascending_order():
    graph = {"a": ["z", "m", "b"]}
    assert dfs_order(graph, "a") == ["a", "b", "m", "z"]


def test_dfs_order_leaves_out_unreachable_nodes():
    graph = {"a": ["b"], "c": ["a"], "d": []}
    assert dfs_order(graph, "a") == ["a", "b"]


def test_dfs_order_set_of_successors_is_read_in_ascending_order():
    assert dfs_order({0: {8, 1, 16}, 8: {9}}, 0) == [0, 1, 8, 9, 16]


