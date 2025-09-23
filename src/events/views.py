from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .exceptions import AlreadyRegisteredError, EventClosedError
from .models import Event
from .pagination import EventPagination
from .serializers import EventRegistrationSerializer, EventSerializer
from .services import register_event


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides `list` and `retrieve` for Events
    """
    queryset = Event.objects.filter(status=Event.Status.OPEN).select_related("venue")
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination
    authentication_classes = [JWTAuthentication] + (
        [SessionAuthentication] if settings.DEBUG else []
    )

    @action(detail=True, methods=["post"], serializer_class=EventRegistrationSerializer)
    def register(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = get_object_or_404(Event, pk=pk)

        try:
            register_event(
                event,
                serializer.validated_data["full_name"],
                serializer.validated_data["email"],
            )
            return Response(
                {"detail": "Succefully registered"},
                status=status.HTTP_200_OK
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
