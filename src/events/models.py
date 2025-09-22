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
