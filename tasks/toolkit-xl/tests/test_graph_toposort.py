import pytest

from toolkit.graph.toposort import CycleError, find_cycle, topo_layers, topo_order


# --- topo_order ---------------------------------------------------------


def test_topo_order_empty_graph_gives_empty_list():
    assert topo_order({}) == []


def test_topo_order_chain_against_the_alphabet():
    assert topo_order({"c": ["b"], "b": ["a"]}) == ["c", "b", "a"]


def test_topo_order_takes_smallest_available_node_each_time():
    assert topo_order({"b": ["a"], "c": []}) == ["b", "a", "c"]


def test_topo_order_diamond():
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"]}
    assert topo_order(graph) == ["a", "b", "c", "d"]


def test_topo_order_integer_nodes():
    assert topo_order({3: [1], 2: [1]}) == [2, 3, 1]


def test_topo_order_order_of_successors_does_not_matter():
    assert topo_order({"a": ["c", "b"]}) == ["a", "b", "c"]


def test_topo_order_cycle_raises_cycle_error():
    with pytest.raises(CycleError):
        topo_order({"a": ["b"], "b": ["a"]})


def test_topo_order_self_loop_raises_cycle_error_with_one_node():
    with pytest.raises(CycleError) as info:
        topo_order({"a": ["b"], "b": ["b"]})
    assert info.value.cycle == ["b"]


# --- topo_layers --------------------------------------------------------


def test_topo_layers_empty_graph_gives_empty_list():
    assert topo_layers({}) == []


def test_topo_layers_independent_nodes_share_one_sorted_layer():
    assert topo_layers({"c": [], "a": [], "b": []}) == [["a", "b", "c"]]


def test_topo_layers_layer_number_is_length_of_longest_path():
    graph = {"a": ["b", "e"], "b": ["c"], "c": ["d"], "d": ["e"]}
    assert topo_layers(graph) == [["a"], ["b"], ["c"], ["d"], ["e"]]


def test_topo_layers_clothes_example():
    graph = {
        "shirt": ["tie", "belt"],
        "tie": ["jacket"],
        "trousers": ["belt", "shoes"],
        "belt": ["jacket"],
    }
    assert topo_layers(graph) == [
        ["shirt", "trousers"],
        ["belt", "shoes", "tie"],
        ["jacket"],
    ]


def test_topo_layers_edge_listed_twice_counts_once():
    assert topo_layers({"a": ["b", "b"], "c": ["b"]}) == [["a", "c"], ["b"]]


def test_topo_layers_does_not_modify_the_graph():
    graph = {"b": ["a", "a"]}
    topo_layers(graph)
    assert graph == {"b": ["a", "a"]}


# --- find_cycle ---------------------------------------------------------


def test_find_cycle_acyclic_graph_gives_none():
    assert find_cycle({"a": ["b", "c"], "b": ["c"]}) is None


def test_find_cycle_follows_the_direction_of_the_edges():
    assert find_cycle({"a": ["c"], "c": ["b"], "b": ["a"]}) == ["a", "c", "b"]


def test_find_cycle_smallest_node_on_any_cycle_comes_before_length():
    assert find_cycle({1: [2], 2: [3], 3: [1, 2]}) == [1, 2, 3]


def test_find_cycle_equal_length_gives_smallest_list_of_strings():
    graph = {"a": ["c", "b"], "b": ["d"], "c": ["d"], "d": ["a"]}
    assert find_cycle(graph) == ["a", "b", "d"]


def test_find_cycle_node_that_is_on_no_cycle_is_skipped():
    assert find_cycle({"a": ["b"], "b": ["c"], "c": ["b"]}) == ["b", "c"]


def test_find_cycle_undirected_loop_is_not_a_cycle():
    assert find_cycle({"a": ["b"], "c": ["b"], "d": ["c", "a"]}) is None


def test_find_cycle_long_cycle_needs_no_recursion():
    graph = {}
    for number in range(3000):
        graph[number] = [(number + 1) % 3000]
    assert find_cycle(graph) == list(range(3000))
