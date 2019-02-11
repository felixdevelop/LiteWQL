from collections import OrderedDict

import regex as re

from litewql.exceptions import ParsingError


class Parser(object):

    def __init__(self, allow_comments=True):
        self.allow_comments = allow_comments

    def _prepare_query(self, query):
        if self.allow_comments:
            query = re.sub(r"//.*", "", query)
            query = re.sub(r"/\*(?>[^/*]|(?R))*\*/", "", query)
            query = re.sub(r"/\*[\w\W]*", "", query)
            query = re.sub(r"/\*", "", query)
        else:
            if "//" in query or "/*" in query:
                raise ParsingError("Comments not allowed!")

        # query = re.sub(r"([?=&#:])\W+([^\W]+[?=&#:{])", r"\g<1>\g<2>", query)

        query = re.sub(r"^[^{]*{", r"", query)
        query = re.sub(r"}[^}]*$", r"", query)

        return query.strip()

    @staticmethod
    def _split_fields(query):
        return re.findall(r'([a-z0-9_]\w*)'
                          r'(?:#([a-z0-9_]\w*))?'
                          r'(?:\:(\w+))?'
                          r'(?:\?((?:[^?=&]+=[^{&} ,\n]+&?)+))?'
                          r'(\{(?>(?R)|[^{}])*\})?'
                          r'(?:[\n ]?)', query, re.IGNORECASE)

    def _prepare_field(self, field_source):
        field_name, field_alias, field_type, field_params, field_subquery = field_source

        field_params = dict([p.split("=") for p in field_params.strip("&").split("&") if p])

        if field_subquery:
            field_subquery = self.parse(field_subquery)
        else:
            field_subquery = {}

        return "%s#%s" % (field_name, field_alias), {
            "name": field_name,
            "alias": field_alias,
            "type": field_type or "auto",
            "params": field_params,
            "subquery": field_subquery
        }

    def parse(self, query):
        query = self._prepare_query(query)
        fields = self._split_fields(query)

        return OrderedDict([self._prepare_field(f) for f in fields])
