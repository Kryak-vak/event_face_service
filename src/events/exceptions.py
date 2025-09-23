class EventRegistrationError(Exception):
    """Base exception for registration errors."""


class EventClosedError(EventRegistrationError):
    """Raised when trying to register for a closed event."""

    def __init__(self, message="Event is closed for registration."):
        super().__init__(message)

class AlreadyRegisteredError(EventRegistrationError):
    """Raised when a user is already registered for an event."""

    def __init__(self, message="Credentials are already registered for this event."):
        super().__init__(message)


class NotificationSendError(EventRegistrationError):
    """Raised when sending a notification fails."""
    
    def __init__(self, message="Failed to send notification."):
        super().__init__(message)
