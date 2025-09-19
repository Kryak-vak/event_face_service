from django.db.models import QuerySet
from rest_framework import filters, generics

from .models import Event
from .pagination import EventPagination
from .serializers import EventSerializer


class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    pagination_class = EventPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["date"]

    def get_queryset(self) -> QuerySet[Event]:
        return (
            Event.objects.filter(status="open")
            .select_related("venue")
        )
