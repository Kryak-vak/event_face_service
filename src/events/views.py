from django.conf import settings
from django.db.models import QuerySet
from rest_framework import filters, generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Event
from .pagination import EventPagination
from .serializers import EventSerializer


class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    pagination_class = EventPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    authentication_classes = [JWTAuthentication] + (
        [SessionAuthentication] if settings.DEBUG else []
    )
    permission_classes = [IsAuthenticated]
    search_fields = ["name"]
    ordering_fields = ["date"]

    def get_queryset(self) -> QuerySet[Event]:
        return (
            Event.objects.filter(status=Event.Status.OPEN)
            .select_related("venue")
        )
