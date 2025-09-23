from django_filters import rest_framework as filters

from .models import Event


class EventFilter(filters.FilterSet):
    # Example: case-insensitive "contains" search for name
    name = filters.CharFilter(
        field_name="name", lookup_expr="icontains"
    )

    registration_deadline_after = filters.IsoDateTimeFilter(
        field_name="registration_deadline", lookup_expr="gte"
    )

    registration_deadline_before = filters.IsoDateTimeFilter(
        field_name="registration_deadline", lookup_expr="lte"
    )

    class Meta:
        model = Event
        fields = ["status", "name"]