from django.apps import apps
from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.contrib.auth import views as auth_views
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.urls import path
from django.shortcuts import render

from system.models import OrganisationUser
from system.models.organisation import Organisation,  OrganisationLocation, OrganisationDepartment,\
    SWOTEntry, PESTLEEntry, ScopeStatement, Employee

class OrganisationLocationInline(admin.StackedInline):
    model = OrganisationLocation
    extra = 1


class DepartmentInline(admin.StackedInline):
    model = OrganisationDepartment
    extra = 1


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'address', 'tin_number', 'region', 'phone', 'sector', 'action_button']
    inlines = [OrganisationLocationInline, DepartmentInline]

    def action_button(self, obj):
        url = reverse('organisation-detail', args=[obj.pk])  # or your custom URL
        return format_html('<a class="btn btn-block btn-outline-primary" href="{}"><i class="fas fa-book"></i> OPEN</a>', url)

    action_button.short_description = 'Action'
    action_button.allow_tags = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate()  # if needed, for related fields
        if not request.user.is_superuser:
            qs = qs.filter(representative=request.user)
            try:
                orguser = OrganisationUser.objects.get(request.user)
                qs = qs.filter(pk=orguser.organisation.id)
            except OrganisationUser.DoesNotExist:
                pass
        return qs

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            cl = response.context_data['cl']
            for result in cl.result_list:
                setattr(result, '_admin_url_id', result.pk)
        except (AttributeError, KeyError):
            pass
        return response


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['department', 'organisation']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate()  # if needed, for related fields
        if not request.user.is_superuser:
            qs = qs.filter(representative=request.user)
        return qs


class SWOTEntryAdmin(admin.ModelAdmin):
    list_display = ['organisation', 'swot_type', 'description']


class PESTLEEntryAdmin(admin.ModelAdmin):
    list_display = ['organisation', 'pestle_type', 'description']


class ScopeStatementAdmin(admin.ModelAdmin):
    list_display = ['organisation', 'text', 'approved_by', 'approved_date']


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['organisation', 'name', 'designation', 'role']


# Register your custom user model with the custom admin class
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(OrganisationDepartment, DepartmentAdmin)
admin.site.register(SWOTEntry, SWOTEntryAdmin)
admin.site.register(PESTLEEntry, PESTLEEntryAdmin)
admin.site.register(ScopeStatement, ScopeStatementAdmin)
admin.site.register(Employee, EmployeeAdmin)

