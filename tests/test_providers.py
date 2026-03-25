import libcst as cst
from pypkg_dependency_graph.providers import ImportProvider
from pypkg_dependency_graph.models import DOT, STAR


class Test_ImportProvider:
    def run_one(self, code):
        wrapper = cst.MetadataWrapper(cst.parse_module(code))
        res = list(wrapper.resolve(ImportProvider).values())
        assert len(res) == 1
        return res[0]

    def test_import_single_no_alias(self):
        actual = self.run_one('import a')
        assert actual == (('a',),)

    def test_import_single_with_alias(self):
        actual = self.run_one('import a as b')
        assert actual == (('a',),)

    def test_import_multiple(self):
        actual = self.run_one('import a, b as c')
        assert actual == (('a',), ('b',))

    def test_import_nested(self):
        actual = self.run_one('import a.b as c')
        assert actual == (('a', 'b',),)

    def test_import_from_single(self):
        actual = self.run_one('from a import b as c')
        assert actual == (('a', 'b',),)

    def test_import_from_nested(self):
        actual = self.run_one('from a.b import c as d')
        assert actual == (('a', 'b', 'c'),)

    def test_import_from_star(self):
        actual = self.run_one('from a import *')
        assert actual == (('a', STAR),)

    def test_relative_import(self):
        actual = self.run_one('from . import a as b')
        assert actual == ((DOT, 'a'),)

    def test_relative_import_with_module(self):
        actual = self.run_one('from .a import b as c')
        assert actual == ((DOT, 'a', 'b'),)

    def test_relative_import_higher(self):
        actual = self.run_one('from .. import a as b')
        assert actual == ((DOT, DOT, 'a'),)

    def test_relative_import_multiple(self):
        actual = self.run_one('from . import a as x, b as y')
        assert actual == ((DOT, 'a'), (DOT, 'b'))
