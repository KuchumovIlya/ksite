from django.contrib import admin

from .models import Message, Topic, Section

admin.site.register(Message)
admin.site.register(Topic)
admin.site.register(Section)
