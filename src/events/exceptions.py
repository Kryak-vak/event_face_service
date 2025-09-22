class EventRegistrationError(Exception):
    """Base exception for registration errors."""


class EventClosedError(EventRegistrationError):
    """Raised when trying to register for a closed event."""


class AlreadyRegisteredError(EventRegistrationError):
    """Raised when a user is already registered for an event."""


class NotificationSendError(EventRegistrationError):
    """Raised when sending a notification fails."""