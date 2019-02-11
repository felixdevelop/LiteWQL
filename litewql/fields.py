import asyncio
from types import FunctionType

from litewql.exceptions import CastError


class Field(object):

    CAST_FUNCS = {
        "str": str,
        "string": str,
        "int": int,
        "integer": int,
        "float": float,
        "double": float,
        "dict": dict,
        "list": list,
        "array": list,
        "set": set,
        "bool": bool,
        "boolean": bool,
        "mapid": lambda obj: list(map(lambda x: int(x["id"]), obj)) if isinstance(obj, list) else obj["id"]
    }

    AUTO_TYPE = "auto"

    def __init__(self, name, factory, data_type=None, params=None, parent_model=None, model_cls=None, subquery=None):
        assert not data_type or \
            data_type in self.CAST_FUNCS or \
            data_type == self.AUTO_TYPE or callable(data_type), "Invalid data_type"

        self.name = name
        self.factory = factory
        self.resolver = factory.resolver
        self.data_type = data_type or self.AUTO_TYPE
        self.params = params or {}
        self.parent_model = parent_model or None
        self.model_cls = model_cls or None
        self.subquery = subquery or {}

    def cast_type(self, data):
        try:
            if callable(self.data_type):
                data = self.data_type(data)
            else:
                assert self.data_type in self.CAST_FUNCS, "Invalid data_type"

                cast_func = self.CAST_FUNCS.get(self.data_type)
                if callable(cast_func):
                    data = cast_func(data)

            return data
        except Exception as e:
            raise CastError(e)

    def execute_model(self, data):
        context = {}
        if self.parent_model and self.parent_model.context:
            context = self.parent_model.context

        model = self.model_cls(self, context)

        if isinstance(data, (list, set, tuple)):
            _data = []
            for data_item in data:
                _data.append(model.execute(self.subquery, data_item))
            data = _data
        else:
            data = model.execute(self.subquery, data)

        return data

    def represent(self, data):
        if data is None:
            return None

        if self.model_cls:
            data = self.execute_model(data)

        if self.data_type and self.data_type != self.AUTO_TYPE:
            data = self.cast_type(data)

        return data


class AsyncField(Field):

    async def execute_model(self, data):
        model = self.model_cls(self)

        if isinstance(data, (list, set, tuple)):
            data = await asyncio.gather(*[model.execute(self.subquery, data_item) for data_item in data])
        else:
            data = await model.execute(self.subquery, data)

        return data

    async def represent(self, data):
        if data is None:
            return None

        if self.model_cls:
            data = await self.execute_model(data)

        if self.data_type and self.data_type != self.AUTO_TYPE:
            data = self.cast_type(data)

        return data


class BaseFieldsFactory(object):
    def build(self, field_name, parent_model=None, field_params=None):
        raise NotImplementedError


class FieldsFactory(BaseFieldsFactory):

    default_field_class = Field

    def __init__(self, field_class=None, default_type="auto", resolver=None, default_params=None,
                 model=None, default_query=None, ):

        self.field_class = field_class or self.default_field_class
        self.default_type = default_type or "auto"
        self.resolver = resolver
        self.default_params = default_params or {}
        self.model = model
        self.default_query = default_query or {}

    def build(self, field_name, parent_model=None, **field_params):

        if isinstance(self.model, FunctionType):
            model_cls = self.model()
        else:
            model_cls = self.model

        field_params = field_params or {}

        return self.field_class(
            name=field_name,
            factory=self,
            data_type=field_params.get("type") or self.default_type,
            parent_model=parent_model,
            model_cls=model_cls,
            params=field_params.get("params") or self.default_params,
            subquery=field_params.get("subquery") or self.default_query,

        )
