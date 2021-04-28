import io
import os
import sys

import pygraphviz
import pytest

sys.path.append(os.getcwd().split('/tests')[0])

from lib.engine import code2flow
from tests.testdata import testdata


os.chdir(os.path.dirname(os.path.abspath(__file__)))
py_tests = testdata['py']


def assert_eq(seq_a, seq_b):
    try:
        assert seq_a == seq_b
    except AssertionError:
        print("extra edges generated", file=sys.stderr)
        for el in (seq_a - seq_b):
            print(el, file=sys.stderr)
        print("missing edges", file=sys.stderr)
        for el in (seq_b - seq_a):
            print(el, file=sys.stderr)
        sys.stderr.flush()
        raise AssertionError()


@pytest.mark.parametrize("test_dict", py_tests)
def test_all(test_dict):
    language = 'py'
    print("Running test %r..." % test_dict['test_name'])
    directory_path = os.path.join('test_code', language, test_dict['directory'])
    kwargs = test_dict.get('kwargs', {})
    output_file = io.StringIO()
    code2flow([directory_path], output_file, language, **kwargs)

    generated_edges = get_edges_set_from_file(output_file)
    print("generated_edges eq", file=sys.stderr)
    assert_eq(generated_edges, set(map(tuple, test_dict['expected_edges'])))

    generated_nodes = get_nodes_set_from_file(output_file)
    print("generated_nodes eq", file=sys.stderr)
    assert_eq(generated_nodes, set(test_dict['expected_nodes']))


def get_nodes_set_from_file(dot_file):
    dot_file.seek(0)
    ag = pygraphviz.AGraph(dot_file.read())
    generated_nodes = []
    for node in ag.nodes():
        generated_nodes.append(node.attr['name'])
    ret = set(generated_nodes)
    assert_eq(sorted(list(ret)), sorted(generated_nodes))  # assert no dupes
    return ret


def get_edges_set_from_file(dot_file):
    dot_file.seek(0)
    ag = pygraphviz.AGraph(dot_file.read())
    generated_edges = []
    for edge in ag.edges():
        to_add = (edge[0].attr['name'],
                  edge[1].attr['name'])
        generated_edges.append(to_add)
    ret = set(generated_edges)
    assert_eq(sorted(list(ret)), sorted(generated_edges))  # assert no dupes
    return ret
