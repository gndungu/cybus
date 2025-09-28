from django.apps import apps
from django.contrib import admin
from conf.models import *

from conf.baseModelAdmin import register_all_models, BaseModelAdmin, BaseTabularInLine

# class RegionAdmin(admin.ModelAdmin):
#     list_display = ['name']
#
#
# class DistrictAdmin(admin.ModelAdmin):
#     list_display = ['name', 'region']
#
#
# class SectionAdmin(admin.ModelAdmin):
#     list_display = ['name']
#
#
# class EvaluationLevelAdmin(admin.ModelAdmin):
#     list_display = ['name', 'days']
#
# class StandardsAdmin(admin.ModelAdmin):
#     list_display = ['standard_no', 'edition', 'standard_title']


register_all_models(apps.get_app_config("conf"), exclude=[])

# admin.site.register(Region, RegionAdmin)
# admin.site.register(District, DistrictAdmin)
# admin.site.register(Sector, SectionAdmin)
# admin.site.register(EvaluationLevel, EvaluationLevelAdmin)
# admin.site.register(Standards, StandardsAdmin)