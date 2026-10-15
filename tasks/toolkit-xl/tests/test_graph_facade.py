import pytest

import toolkit.graph
from toolkit.graph.paths import NegativeWeightError
from toolkit.graph.toposort import CycleError


# --- component_order ----------------------------------------------------


def test_component_order_empty_graph_gives_empty_list():
    assert toolkit.graph.component_order({}) == []


def test_component_order_component_comes_before_the_ones_it_points_to():
    graph = {"a": ["b"], "b": ["a"], "c": ["a"]}
    assert toolkit.graph.component_order(graph) == [["c"], ["a", "b"]]


def test_component_order_representative_is_the_smallest_node_of_the_component():
    graph = {"m": ["a"], "a": ["m"], "k": ["x"]}
    assert toolkit.graph.component_order(graph) == [["a", "m"], ["k"], ["x"]]


def test_component_order_self_loop_raises_nothing():
    assert toolkit.graph.component_order({"a": ["a", "b"]}) == [["a"], ["b"]]


def test_component_order_does_not_modify_the_graph():
    graph = {"b": ["a", "a"], "a": ["b"]}
    toolkit.graph.component_order(graph)
    assert graph == {"b": ["a", "a"], "a": ["b"]}


# --- re-exports ---------------------------------------------------------


def test_graph_facade_exposes_components_functions():
    assert toolkit.graph.connected_components({"a": ["b"]}) == [["a", "b"]]
    assert toolkit.graph.strongly_connected_components({"a": ["b"]}) == [["a"], ["b"]]
    assert toolkit.graph.UnionFind(["b", "a"]).groups() == [["a"], ["b"]]


