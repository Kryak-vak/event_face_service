from django.contrib import admin

from .models import Event, Venue

admin.site.register((Venue, Event))
