"""Utilities for creating test python packages and modules."""

from pathlib import Path


def create_package(parent: Path, name: str, content: str = '') -> Path:
    """Create a new package.

    - content is written to __init__.py.
    - returns package folder
    """
    folder = parent / name
    folder.mkdir(parents=True)
    with open(folder / '__init__.py', 'w') as f:
        f.write(content)
    return folder


def create_module(parent: Path, name: str, content: str = '') -> Path:
    """Create a new module.

    - returns module file
    """
    parent.mkdir(parents=True, exist_ok=True)
    fn = parent / f'{name}.py'
    with open(fn, 'w') as f:
        f.write(content)
    return fn
