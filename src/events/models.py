from uuid import uuid4

from django.db import models


class Venue(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )
    provider_id = models.UUIDField(unique=True, null=True, blank=True)
    
    name = models.CharField("Название", max_length=255, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        verbose_name = "Площадка"
        verbose_name_plural = "Площадки"

    def __str__(self):
        return self.name


class Event(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )
    provider_id = models.UUIDField(unique=True, null=True, blank=True)

    name = models.CharField("Название", max_length=255)
    date = models.DateTimeField("Дата проведения мероприятия")
    status = models.CharField(
        "Текущий статус",
        max_length=6,
        choices=Status.choices,
        default=Status.OPEN
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Площадка"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"

    def __str__(self):
        return f"{self.name} ({self.date.date()})"


class EventRegistration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.ForeignKey(
        "Event", on_delete=models.CASCADE, related_name="registrations"
    )
    
    fullname = models.CharField(max_length=128)
    email = models.EmailField()
    confirmation_code = models.CharField(max_length=32)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("event", "email")
        verbose_name = "Регистрация на мероприятие"
        verbose_name_plural = "Регистрации на мероприятия"

    def __str__(self):
        return f"{self.fullname} ({self.email}) -> {self.event.name}"


class OutboxMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    
    topic = models.CharField(max_length=255)
    payload = models.JSONField()
    
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic} - sent: {self.sent}"

