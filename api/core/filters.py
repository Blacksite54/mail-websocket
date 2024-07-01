from typing import Dict, Callable

from django.db import models
from django.db.models import QuerySet

from rest_framework.filters import BaseFilterBackend


class BaseFilterAPI(BaseFilterBackend):
    filter_keys = {}
    custom_filter: Dict[
        str, Callable[[models.query.QuerySet, str], models.query.QuerySet]
    ] = {}

    def filter_queryset(self, request, queryset, view):
        query_params = request.query_params

        _filter = {}
        for filter_key in self.filter_keys:
            query_param = query_params.get(filter_key, "").strip()
            if query_param and self.filter_keys[filter_key]:
                _filter[self.filter_keys[filter_key]] = query_param

        queryset = queryset.filter(**_filter)

        for filter_custom_key in self.custom_filter:
            query_param = query_params.get(filter_custom_key, "").strip()
            if query_param and self.custom_filter[filter_custom_key]:
                for _value in query_param.split():
                    queryset = self.custom_filter[filter_custom_key](
                        queryset, _value
                    )

        sort = query_params.get("sort")
        if sort:
            queryset = self.sort_query(sort, queryset)

        return queryset

    def get_schema_operation_parameters(self, view):
        query_filters = list(
            map(
                lambda field: {
                    "name": field,
                    "in": "query",
                    "required": False,
                    "description": field,
                    "schema": {"type": "string"},
                },
                {**self.filter_keys, **self.custom_filter},
            )
        )
        return query_filters

    def sort_query(self, sort_param: str, queryset: QuerySet) -> QuerySet:
        valid_field_name = sort_param

        if sort_param.startswith("-"):
            valid_field_name = sort_param[1:]

        for field in queryset.model._meta.fields:
            if valid_field_name == field.name:
                queryset = queryset.order_by(sort_param)
                break

        return queryset
