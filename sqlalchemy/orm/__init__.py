from typing import Any, Callable, Dict, Iterator, Optional, Type

from .. import Column, Engine


class MetaData:
    def __init__(self):
        self.models: Dict[str, Type] = {}

    def register_model(self, model: Type):
        self.models[model.__tablename__] = model

    def create_all(self, bind: Engine):
        for model in self.models.values():
            bind.create_table(model)


class DeclarativeBase:
    metadata = MetaData()

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls._columns = {name: value for name, value in cls.__dict__.items() if isinstance(value, Column)}
        if hasattr(cls, "__tablename__"):
            DeclarativeBase.metadata.register_model(cls)

    def __init__(self, **kwargs: Any):
        for name, column in self._columns.items():
            if name in kwargs:
                setattr(self, name, kwargs[name])
            else:
                setattr(self, name, column.get_default())


class Session:
    def __init__(self, engine: Engine):
        self.engine = engine

    def add(self, obj: Any):
        model = type(obj)
        if model not in self.engine.tables:
            self.engine.create_table(model)
        pk_name = next((name for name, col in model._columns.items() if col.primary_key), None)
        if pk_name and getattr(obj, pk_name, None) is None:
            self.engine.counters[model] = self.engine.counters.get(model, 0) + 1
            setattr(obj, pk_name, self.engine.counters[model])
        table = self.engine.tables.setdefault(model, [])
        if obj not in table:
            table.append(obj)

    def commit(self):
        return None

    def refresh(self, obj: Any):
        return None

    def query(self, model: Type):
        return Query(self, model)

    def get(self, model: Type, identifier: Any):
        table = self.engine.tables.get(model, [])
        pk_name = next((name for name, col in model._columns.items() if col.primary_key), None)
        for obj in table:
            if pk_name is not None and getattr(obj, pk_name) == identifier:
                return obj
        return None

    def delete(self, obj: Any):
        table = self.engine.tables.get(type(obj), [])
        if obj in table:
            table.remove(obj)

    def close(self):
        return None


class Query:
    def __init__(self, session: Session, model: Type):
        self.session = session
        self.model = model
        self._order: Optional[Callable[[Any], Any]] = None
        self._descending = False

    def order_by(self, sort_spec):
        if hasattr(sort_spec, "key"):
            self._order = lambda obj: getattr(obj, sort_spec.key)
            self._descending = getattr(sort_spec, "descending", False)
        return self

    def all(self):
        items = list(self.session.engine.tables.get(self.model, []))
        if self._order:
            items.sort(key=self._order, reverse=self._descending)
        return items


def sessionmaker(bind: Engine, autoflush: bool = False, autocommit: bool = False):
    def factory() -> Session:
        return Session(bind)

    return factory
