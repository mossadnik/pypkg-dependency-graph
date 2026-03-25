import libcst as cst
from .package import Package, LocalModule
from .providers import ImportProvider


def get_package_dependency_graph(package: Package) -> tuple[set[LocalModule], set[tuple[LocalModule, LocalModule]]]:
    """Create a module dependency graph from package code.

    Returns
    -------
        nodes, edges
    """
    nodes = set()
    edges = set()
    for module in package:
        nodes.add(module)
        for dependency in get_dependencies(module, package):
            edges.add((module, dependency))
    return nodes, edges


def get_dependencies(module: LocalModule, package: Package) -> set[LocalModule]:
    with open(module.code_path) as f:
        code = f.read()
    wrapper = cst.MetadataWrapper(cst.parse_module(code))
    res = wrapper.resolve(ImportProvider)
    resolved_imports = (
        package.resolve_import(module, imp)
        for import_statement in res.values()
        for imp in import_statement
    )
    return {imp for imp in resolved_imports if isinstance(imp, LocalModule)}


def get_package_tree(package: Package) -> tuple[set[LocalModule], set[tuple[LocalModule, LocalModule]]]:
    nodes = set()
    edges = set()
    for module in package:
        nodes.add(module)
        parent = module.get_parent()
        if parent:
            edges.add((module, parent))
    return nodes, edges
