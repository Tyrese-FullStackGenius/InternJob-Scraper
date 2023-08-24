from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from customauth.models import User
from internships.models import Company
from internships.models import Program
from internships.models import Region

admin.site.register(User, UserAdmin)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'region', 'category', 'get_external_link']
    ordering = ['-id']
    list_filter = ['company', 'region', 'category', 'is_application_open']
    search_fields = ['title']
