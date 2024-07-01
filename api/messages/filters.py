from django.db.models import Q

from api.core.filters import BaseFilterAPI


class MessageFilter(BaseFilterAPI):
    custom_filter = {
        "query": lambda queryset, value: queryset.filter(
            Q(title__icontains=value)
        )
    }
