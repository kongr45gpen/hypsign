from django.contrib import admin

# Register your models here.
from .models import Display, Page, ScheduleEntry, ScheduleSequenceItem

admin.site.register(Page)

@admin.register(Display)
class DisplayAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')
    
class ScheduleSequenceInline(admin.TabularInline):
    model = ScheduleSequenceItem

@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'priority', 'start_date', 'end_date', 'start_time', 'end_time')

    inlines = [ ScheduleSequenceInline ]
