from django.contrib import admin

from .models import Display, Page, ScheduleEntry, ScheduleSequenceItem

from adminsortable2.admin import SortableTabularInline, SortableAdminBase

from django.db import models
from django.forms import NumberInput

admin.site.register(Page)

@admin.register(Display)
class DisplayAdmin(admin.ModelAdmin):
    list_display = ('description', 'code')
    
class ScheduleSequenceInline(admin.TabularInline):
    model = ScheduleSequenceItem
    extra = 1

    formfield_overrides = {
        models.FloatField: {'widget': NumberInput(attrs={'size':8})},
        models.PositiveIntegerField: {'widget': NumberInput(attrs={'size':5})},
    }

@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ('__str__', 'priority', 'start_date', 'end_date', 'start_time', 'end_time')

    inlines = [ ScheduleSequenceInline ]
