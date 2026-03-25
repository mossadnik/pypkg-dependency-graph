import pytest
from pypkg_dependency_graph.project import (
    is_module,
    is_package,
    Package,
    SubModule,
    SubPackage,
    LibraryModule
)
from pypkg_dependency_graph import models
from pypkg_dependency_graph.testing import create_module, create_package


class Test_Package_resolve_path:
    def test_raises_if_path_not_exists(self, tmp_path):
        pkg = create_package(tmp_path, 'pkg')
        with pytest.raises(ValueError):
            Package(pkg).resolve_path(pkg / 'my_module.py')

    def test_module(self, tmp_path):
        pkg = create_package(tmp_path, 'pkg')
        mod = create_module(pkg, 'mod')
        package = Package(pkg)
        actual = package.resolve_path(mod)
        assert actual == SubModule(mod, package)

    def test_module_nested(self, tmp_path):
        pkg = create_package(tmp_path, 'pkg')
        sub_pkg = create_package(pkg, 'sub_pkg')
        mod = create_module(sub_pkg, 'mod')
        package = Package(pkg)
        actual = package.resolve_path(mod)
        assert actual == SubModule(mod, package)

    def test_package(self, tmp_path):
        pkg = create_package(tmp_path, 'pkg')
        sub_pkg = create_package(pkg, 'sub_pkg')
        package = Package(pkg)
        actual = package.resolve_path(sub_pkg)
        assert actual == SubPackage(sub_pkg, package)

    def test_package_init_py(self, tmp_path):
        pkg = create_package(tmp_path, 'pkg')
        sub_pkg = create_package(pkg, 'sub_pkg')
        package = Package(pkg)
        actual = package.resolve_path(sub_pkg / '__init__.py')
        assert actual == SubPackage(sub_pkg, package)


class Test_Package_resolve_identifier:
    def test_module(self, tmp_path):
        pkg = create_package(tmp_path, 'pkg')
        mod = create_module(pkg, 'mod')
        package = Package(pkg)
        identifier = ('pkg', 'mod')
        actual = package.resolve_identifier(identifier)
        assert actual == SubModule(mod, package)
        assert actual.identifier == identifier

    def test_package(self, tmp_path):
        pkg = create_package(tmp_path, 'pkg')
        sub_pkg = create_package(pkg, 'sub_pkg')
        package = Package(pkg)
        identifier = ('pkg', 'sub_pkg')
        actual = package.resolve_identifier(identifier)
        assert actual == SubPackage(sub_pkg, package)
        assert actual.identifier == identifier


class Test_Package_resolve_import:
    def test_resolves_absolute_library_import(self, tmp_path):
        pkg = create_package(tmp_path, 'pkg')
        package = Package(pkg)
        actual = package.resolve_import(package, ('library', 'module'))
        assert actual == LibraryModule(('library', 'module'))

    def test_resolves_absolute_local_import(self, tmp_path):
        pkg = create_package(tmp_path, 'pkg')
        mod = create_module(pkg, 'mod')
        other = create_module(pkg, 'other')
        package = Package(pkg)
        sub_module = SubModule(mod, package)
        actual = package.resolve_import(sub_module, ('pkg', 'other'))
        assert actual == SubModule(other, package)

    def test_resolves_absolute_local_imported_symbol(self, tmp_path):
        pkg = create_package(tmp_path, 'pkg')
        mod = create_module(pkg, 'mod')
        other = create_module(pkg, 'other')
        package = Package(pkg)
        sub_module = SubModule(mod, package)
        actual = package.resolve_import(sub_module, ('pkg', 'other', 'symbol'))
        assert actual == SubModule(other, package)

    def test_resolves_relative_import(self, tmp_path):
        """
        From sub-module run

        - from . import other
        """
        pkg = create_package(tmp_path, 'pkg')
        mod = create_module(pkg, 'mod')
        other = create_module(pkg, 'other')
        package = Package(pkg)
        sub_module = SubModule(mod, package)
        actual = package.resolve_import(sub_module, (models.DOT, 'other'))
        assert actual == SubModule(other, package)

    def test_resolves_relative_import_from_init_py(self, tmp_path):
        """
        From top-level run

        - from . import other
        """
        pkg = create_package(tmp_path, 'pkg')
        other = create_module(pkg, 'other')
        package = Package(pkg)
        actual = package.resolve_import(package, (models.DOT, 'other'))
        assert actual == SubModule(other, package)

    def test_resolves_relative_import_from_nested_init_py(self, tmp_path):
        """
        From nested sub-package run:

        - from . import other
        - from .. import other
        """
        pkg = create_package(tmp_path, 'pkg')
        top_other = create_module(pkg, 'other')
        subpkg = create_package(pkg, 'nested')
        nested_other = create_module(subpkg, 'other')
        package = Package(pkg)
        nested = SubPackage(subpkg, package)
        actual = package.resolve_import(nested, (models.DOT, 'other'))
        assert actual == SubModule(nested_other, package)
        actual = package.resolve_import(nested, (models.DOT, models.DOT, 'other'))
        assert actual == SubModule(top_other, package)


class Test_is_module:
    def test_rejects_folder(self, tmp_path):
        assert not is_module(tmp_path)

    @pytest.mark.parametrize('filename', ['wrong_extension.txt', 'many.extensions.py', '__init__.py'])
    def test_rejects(self, tmp_path, filename):
        fn = tmp_path / filename
        with open(fn, 'w') as f:
            f.write('')
        assert not is_module(fn)

    def test_accepts(self, tmp_path):
        fn = create_module(tmp_path, 'my_module')
        assert is_module(fn)

    def test_rejects_if_not_exists(self, tmp_path):
        assert not is_module(tmp_path / 'mod.py')


class Test_is_package:
    def test_rejects_files(self, tmp_path):
        fn = create_module(tmp_path, 'my_module')
        assert not is_package(fn)

    def test_rejects_folder_without_init_py(self, tmp_path):
        assert not is_package(tmp_path)

    def test_rejects_if_not_exists(self, tmp_path):
        assert not is_package(tmp_path / 'folder')

    def test_accepts_folder_with_init_py(self, tmp_path):
        fn = create_package(tmp_path, 'my_package')
        assert is_package(fn)
