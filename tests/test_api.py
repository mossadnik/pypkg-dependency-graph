from pathlib import Path
from pypkg_dependency_graph.api import get_package_dependency_graph, get_package_tree
from pypkg_dependency_graph.package import Package, SubModule, SubPackage
from pypkg_dependency_graph.testing import create_module, create_package


class Test_get_package_dependency_graph:
    def test_dependency_list(self, tmp_path: Path):
        top = create_package(tmp_path, 'pkg', 'import pkg.nested.other')
        top_other = create_module(top, 'other', 'import itertools as it')
        nested = create_package(top, 'nested', 'from . import other\nfrom ..other import *')
        nested_other = create_module(nested, 'other')
        top = Package(top)
        top_other = SubModule(top_other, top)
        nested = SubPackage(nested, top)
        nested_other = SubModule(nested_other, top)
        expected_edges = {
            (top, nested_other),
            (nested, nested_other),
            (nested, top_other)
        }
        nodes, edges = get_package_dependency_graph(top)
        assert nodes =={top, top_other, nested, nested_other}
        assert edges == expected_edges


class Test_get_package_tree_edges:
    def test_simple(self, tmp_path: Path):
        top = create_package(tmp_path, 'pkg')
        top_other = create_module(top, 'other')
        nested = create_package(top, 'nested')
        nested_other = create_module(nested, 'other')
        top = Package(top)
        top_other = SubModule(top_other, top)
        nested = SubPackage(nested, top)
        nested_other = SubModule(nested_other, top)
        expected_edges = {
            (nested_other, nested),
            (nested, top),
            (top_other, top)
        }
        nodes, edges = get_package_tree(top)
        assert nodes == {top, top_other, nested, nested_other}
        assert edges == expected_edges
