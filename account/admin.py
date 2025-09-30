from django.apps import apps
from django.contrib import admin
from conf.models import *

from conf.baseModelAdmin import register_all_models, BaseModelAdmin, BaseTabularInLine


register_all_models(apps.get_app_config("account"), exclude=[])

