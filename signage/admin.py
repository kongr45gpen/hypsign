from django.contrib import admin

from .models import Display, Page, ScheduleEntry, ScheduleSequenceItem

from adminsortable2.admin import SortableTabularInline, SortableAdminBase

admin.site.register(Page)

@admin.register(Display)
class DisplayAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')
    
class ScheduleSequenceInline(SortableTabularInline):
    model = ScheduleSequenceItem
    extra = 1

@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ('__str__', 'priority', 'start_date', 'end_date', 'start_time', 'end_time')

    inlines = [ ScheduleSequenceInline ]
