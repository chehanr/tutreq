from django.contrib import admin

from .models import Course, Program, Request, Slot, Unit, Feedback

# Register your models here.

admin.site.register(Program)
admin.site.register(Course)
admin.site.register(Unit)
admin.site.register(Request)
admin.site.register(Slot)
admin.site.register(Feedback)
