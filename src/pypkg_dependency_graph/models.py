from enum import StrEnum


class ImportConst(StrEnum):
    star = '*'
    dot = '.'


type ImportPart = str | ImportConst
DOT = ImportConst.dot
STAR = ImportConst.star

type Import = tuple[ImportPart, ...]
type ModuleIdentifier = tuple[str, ...]
