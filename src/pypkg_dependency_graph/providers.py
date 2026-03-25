import libcst as cst
from .models import DOT, STAR, Import


class ImportProvider(cst.BatchableMetadataProvider[tuple[Import, ...]]):
    """
    Marks Name nodes found as a parameter to a function.
    """
    def __init__(self) -> None:
        super().__init__()

    def visit_Import(self, node: cst.Import) -> None:
        imports = []
        for alias in node.names:
            name = alias.name
            imports.append(get_name(name))
        self.set_metadata(node, tuple(imports))

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        imports = []
        if node.relative:
            relative = (DOT,) * len(node.relative)
        else:
            relative = ()
        prefix = relative + get_name(node.module)
        if isinstance(node.names, cst.ImportStar):
            imports.append((STAR,))
        else:
            for alias in node.names:
                name = alias.name
                imports.append(get_name(name))
        self.set_metadata(node, tuple(prefix + imp for imp in imports))


def get_name(node: cst.CSTNode | None) -> Import:
    if node is None:
        return ()
    if isinstance(node, cst.Name):
        return (node.value,)
    elif isinstance(node, cst.Attribute):
        return get_name(node.value) + get_name(node.attr)
    raise TypeError(f'Cannot get name for node type {type(node)}')
