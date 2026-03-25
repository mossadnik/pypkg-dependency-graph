from dataclasses import dataclass
from pathlib import Path
import itertools as it
from . import models


@dataclass
class AnyModule:
    @property
    def identifier(self) -> models.ModuleIdentifier:
        raise NotImplementedError()


@dataclass
class LibraryModule(AnyModule):
    _identifier: models.ModuleIdentifier

    @property
    def identifier(self) -> models.ModuleIdentifier:
        return self._identifier


@dataclass
class LocalModule(AnyModule):
    path: Path


@dataclass
class SubModule(LocalModule):
    package: 'Package'

    @property
    def identifier(self) -> models.ModuleIdentifier:
        parts = self.path.relative_to(self.package.path).parts
        return (
            self.package.name,
            *parts[:-1],
            parts[-1].split('.')[0]
        )

    def resolve_import(self, identifier: models.Import) -> AnyModule:
        return self.package.resolve_import(self, identifier)


@dataclass
class SubPackage(LocalModule):
    package: 'Package'

    @property
    def identifier(self) -> models.ModuleIdentifier:
        parts = self.path.relative_to(self.package.path).parts
        return (
            self.package.name,
            *parts,
        )


@dataclass
class Package(LocalModule):
    """A Python package."""

    @property
    def identifier(self) -> models.ModuleIdentifier:
        return (self.name,)

    @property
    def name(self) -> str:
        return self.path.name

    def resolve_path(self, path: Path) -> AnyModule:
        if not path.exists():
            raise ValueError(f'path does not exist: {path}')
        if path == self.path:
            return self
        elif is_module(path):
            return SubModule(path, self)
        elif is_package(path):
            return SubPackage(path, self)
        elif is_init_py(path):
            return self.resolve_path(path.parent)
        else:
            raise ValueError(f'Not a package or module: {path}')

    def resolve_identifier(self, identifier: models.ModuleIdentifier) -> AnyModule:
        if identifier[0] != self.name:
            return LibraryModule(identifier)
        path = self.path.parent / Path(*identifier)
        if is_package(path):
            return SubPackage(path, self)
        path = self.path.parent / Path(*identifier[:-1]) / f'{identifier[-1]}.py'
        if is_module(path):
            return SubModule(path, self)
        raise ValueError(f'Module not found: {".".join(identifier)}')

    def resolve_import(self, module: LocalModule, identifier: models.Import) -> AnyModule:
        is_relative = identifier[0] == models.DOT
        is_local = is_relative or identifier[0] == self.name
        if identifier[-1] == models.STAR:
            identifier = identifier[:-1]
        if not is_local:
            return LibraryModule(identifier)
        if is_relative:
            level = len(list(it.takewhile(lambda x: x == models.DOT, identifier)))
            if isinstance(module, (Package, SubPackage)):
                level -= 1
            search_path = module.identifier
            if level > 0:
                search_path = search_path[:-level]
            search_path = search_path + identifier
        else:
            search_path = identifier
        try:
            return self.resolve_identifier(search_path)
        except ValueError:
            return self.resolve_identifier(search_path[:-1])


def is_init_py(path: Path) -> bool:
    return path.name == '__init__.py'


def is_package(path: Path) -> bool:
    if not path.is_dir():
        return False
    return any(is_init_py(f) for f in path.iterdir())


def is_module(path: Path) -> bool:
    if not path.exists():
        return False
    if path.is_dir():
        return False
    return path.suffixes == ['.py'] and not is_init_py(path)
