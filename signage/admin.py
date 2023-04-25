from django.contrib import admin

# Register your models here.
from .models import Display, Page, ScheduleEntry

admin.site.register(Page)
admin.site.register(ScheduleEntry)

@admin.register(Display)
class DisplayAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')