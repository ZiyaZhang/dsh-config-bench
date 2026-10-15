import pytest

from toolkit.graph.components import (
    UnionFind,
    connected_components,
    strongly_connected_components,
)


# --- connected_components -----------------------------------------------


def test_connected_components_empty_graph_gives_empty_list():
    assert connected_components({}) == []


def test_connected_components_direction_is_ignored():
    assert connected_components({"a": ["c"], "b": ["c"]}) == [["a", "b", "c"]]


def test_connected_components_nodes_of_a_component_are_sorted():
    graph = {"m": ["z", "a"], "z": ["k"]}
    assert connected_components(graph) == [["a", "k", "m", "z"]]


def test_connected_components_integers_are_compared_as_numbers():
    assert connected_components({10: [2], 3: [3]}) == [[2, 10], [3]]


def test_connected_components_three_groups():
    graph = {"d": ["c"], "a": ["c"], "b": [], "y": ["x"]}
    assert connected_components(graph) == [["a", "c", "d"], ["b"], ["x", "y"]]


def test_connected_components_long_chain():
    graph = {}
    for number in range(3000, 0, -1):
        graph[number] = [number - 1]
    assert connected_components(graph) == [list(range(3001))]


# --- strongly_connected_components --------------------------------------


def test_strongly_connected_components_one_way_edge_gives_two_components():
    assert strongly_connected_components({"a": ["b"]}) == [["a"], ["b"]]


def test_strongly_connected_components_cycle_with_tail():
    graph = {"a": ["b"], "b": ["a", "c"]}
    assert strongly_connected_components(graph) == [["a", "b"], ["c"]]


def test_strongly_connected_components_two_cycles_joined_one_way():
    graph = {"a": ["b"], "b": ["a", "c"], "c": ["d"], "d": ["c"], "e": ["a"]}
    assert strongly_connected_components(graph) == [["a", "b"], ["c", "d"], ["e"]]


def test_strongly_connected_components_node_that_occurs_only_in_a_value():
    assert strongly_connected_components({"x": ["y", "w"]}) == [["w"], ["x"], ["y"]]


def test_strongly_connected_components_path_back_through_several_nodes():
    graph = {1: [2], 2: [3], 3: [4], 4: [2], 5: [1]}
    assert strongly_connected_components(graph) == [[1], [2, 3, 4], [5]]


# --- UnionFind ----------------------------------------------------------


def test_union_find_new_object_is_empty():
    sets = UnionFind()
    assert sets.count() == 0 and sets.groups() == []


def test_union_find_accepts_a_generator():
    sets = UnionFind(number for number in [3, 1, 2])
    assert sets.groups() == [[1], [2], [3]]


def test_union_find_add_of_known_item_keeps_it_in_its_set():
    sets = UnionFind(["a", "b"])
    sets.union("a", "b")
    sets.add("b")
    assert sets.groups() == [["a", "b"]]


def test_union_find_find_does_not_depend_on_argument_order():
    sets = UnionFind(["a", "b", "c", "d"])
    sets.union("a", "b")
    sets.union("d", "c")
    sets.union("c", "b")
    assert [sets.find(item) for item in "abcd"] == ["a", "a", "a", "a"]


def test_union_find_union_returns_true_when_sets_are_joined():
    sets = UnionFind(["a", "b"])
    assert sets.union("a", "b") is True


def test_union_find_connected():
    sets = UnionFind(["a", "b", "c"])
    sets.union("a", "c")
    assert sets.connected("c", "a") is True and sets.connected("a", "b") is False


def test_union_find_size():
    sets = UnionFind(["a", "b", "c", "d"])
    sets.union("a", "b")
    sets.union("b", "c")
    assert [sets.size(item) for item in "abcd"] == [3, 3, 3, 1]


def test_union_find_count_goes_up_with_add():
    sets = UnionFind(["a"])
    sets.add("b")
    sets.add("a")
    assert sets.count() == 2


def test_union_find_find_unknown_item_raises_key_error():
    with pytest.raises(KeyError):
        UnionFind(["a"]).find("z")


def test_union_find_connected_with_unknown_item_raises_key_error():
    with pytest.raises(KeyError):
        UnionFind(["a"]).connected("a", "z")


