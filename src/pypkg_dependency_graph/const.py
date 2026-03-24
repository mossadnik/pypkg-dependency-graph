from enum import StrEnum


class ImportConst(StrEnum):
    star = '*'
    dot = '.'


type ImportPart = str | ImportConst
DOT = ImportConst.dot
STAR = ImportConst.star