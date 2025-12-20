from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type


class Column:
    def __init__(self, column_type: Any, primary_key: bool = False, index: bool = False, nullable: bool = True, default: Any = None):
        self.column_type = column_type
        self.primary_key = primary_key
        self.index = index
        self.nullable = nullable
        self.default = default
        self.name: Optional[str] = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name, self.get_default())

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def get_default(self):
        if callable(self.default):
            return self.default()
        return self.default

    def desc(self):
        return SortSpec(self.name, descending=True)


class SortSpec:
    def __init__(self, key: str, descending: bool = False):
        self.key = key
        self.descending = descending


class Integer:
    pass


class String:
    def __init__(self, length: int):
        self.length = length


class Boolean:
    pass


class DateTime:
    def __init__(self, default: Callable[[], datetime] | None = None, nullable: bool = True):
        self.default = default
        self.nullable = nullable


class Engine:
    def __init__(self, url: str, connect_args: Optional[dict] = None):
        self.url = url
        self.connect_args = connect_args or {}
        self.tables: Dict[Type, List[Any]] = {}
        self.counters: Dict[Type, int] = {}

    def create_table(self, model: Type):
        if model not in self.tables:
            self.tables[model] = []
            self.counters[model] = 0

    def dispose(self):
        self.tables.clear()
        self.counters.clear()


def create_engine(url: str, connect_args: Optional[dict] = None):
    return Engine(url, connect_args=connect_args)


from .orm import DeclarativeBase, Session, sessionmaker  # noqa: E402  pylint: disable=wrong-import-position

__all__ = [
    "Boolean",
    "Column",
    "DateTime",
    "Integer",
    "String",
    "create_engine",
    "Engine",
    "DeclarativeBase",
    "Session",
    "sessionmaker",
]
