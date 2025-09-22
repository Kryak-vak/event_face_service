from django.conf import settings
from django.db.models import QuerySet
from rest_framework import filters, generics, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .exceptions import AlreadyRegisteredError, EventClosedError, NotificationSendError
from .models import Event
from .pagination import EventPagination
from .serializers import EventRegistrationSerializer, EventSerializer
from .services import register_event


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

class EventRegisterView(generics.GenericAPIView):
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] + (
        [SessionAuthentication] if settings.DEBUG else []
    )

    def post(self, request, event_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        owner_id = request.data.get("owner_id")
        if not owner_id:
            return Response(
                {"detail": "owner_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response(
                {"detail": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            register_event(
                event,
                serializer.validated_data["full_name"],
                serializer.validated_data["email"],
                owner_id
            )
        except EventClosedError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except AlreadyRegisteredError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except NotificationSendError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
