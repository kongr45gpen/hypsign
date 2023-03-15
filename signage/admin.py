from django.contrib import admin

# Register your models here.
from .models import Display, Page

admin.site.register(Display)
admin.site.register(Page)