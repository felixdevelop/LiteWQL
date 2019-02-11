import asyncio
from collections import OrderedDict

from litewql.fields import FieldsFactory


class Model(object):

    def __init__(self, parent_field=None):
        self.parent_field = parent_field

    @classmethod
    def _get_res_object(cls):
        return OrderedDict()

    @staticmethod
    def _default_resolver(field, init_data):
        if not init_data:
            return None
        if not isinstance(init_data, dict):
            return init_data

        return init_data.get(field.name)

    def _get_meta(self):
        meta = getattr(self, "Meta", None)

        if isinstance(meta, type):
            return meta

    def _get_default_fields(self):
        meta = self._get_meta()
        if meta:
            default_fields = getattr(meta, "default_fields", None)

            if default_fields:
                return default_fields

        return [fn for fn in dir(self) if isinstance(getattr(self, fn, None), FieldsFactory)]

    def get_resolver(self, field, resolver_name=None):

        if self.parent_field and self.parent_field.parent_model:

            field_name = "resolve_%s__%s" % (self.parent_field.name, field.name)
            field_resolver = self.parent_field.parent_model.get_resolver(
                self.parent_field, field_name
            )

            if field_resolver and field_resolver != self._default_resolver:
                return field_resolver

        field_resolver = resolver_name or field.resolver or "resolve_%s" % field.name

        if isinstance(field_resolver, str):
            field_resolver = getattr(self, field_resolver, None)

        if not callable(field_resolver):
            return self._default_resolver

        return field_resolver

    def get_query_fields(self, query=None):

        fields = OrderedDict()

        query_obj = query or {f: {} for f in self._get_default_fields()}

        for field_name, field_params in query_obj.items():
            field_name = field_name.split("#")[0]

            field_factory = getattr(self, field_name, None)
            if not field_factory:
                continue

            field_alias = field_params.get("alias") or field_name

            fields[field_alias] = field_factory.build(
                field_name,
                parent_model=self,
                **field_params
            )

        return fields

    def fetch_fields_data(self, fields, init_data=None):
        res_obj = {}

        for field_alias, field in fields.items():
            field_resolver = self.get_resolver(field)
            field_data = field_resolver(field, init_data)

            res_obj[field_alias] = field_data

        return res_obj

    def prepare_fields_data(self, fields_data, fields):
        res_obj = self._get_res_object()

        for field_alias, field_data in fields_data.items():
            field = fields[field_alias]
            res_obj[field_alias] = field.represent(field_data)

        return res_obj

    def execute(self, query_obj=None, init_data=None):
        fields = self.get_query_fields(query_obj)
        fields_data = self.fetch_fields_data(fields, init_data)

        return self.prepare_fields_data(fields_data, fields)


class AsyncModel(Model):

    @staticmethod
    async def _default_resolver(field, init_data):
        if not init_data:
            return None
        if not isinstance(init_data, dict):
            return init_data

        return init_data.get(field.name)

    async def fetch_fields_data(self, fields, init_data=None):
        results = await asyncio.gather(*[
            self.get_resolver(field)(field, init_data)
            for field in fields.values()
        ])

        return {field_alias: results[index] for index, field_alias in enumerate(fields.keys())}

    async def prepare_fields_data(self, fields_data, fields):
        res_obj = self._get_res_object()

        for field_alias, field_data in fields_data.items():
            field = fields[field_alias]
            res_obj[field_alias] = await field.represent(field_data)

        return res_obj

    async def execute(self, query_obj=None, init_data=None):
        fields = self.get_query_fields(query_obj)
        fields_data = await self.fetch_fields_data(fields, init_data)

        return await self.prepare_fields_data(fields_data, fields)
