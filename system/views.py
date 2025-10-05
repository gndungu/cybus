from django.shortcuts import render
from django.views import View
from django.contrib import admin, messages
from django.views.generic import TemplateView, DetailView

from system.models import Organisation


class HomeView(TemplateView):
    template_name = "admin/home.html"

class OrganisationView(TemplateView):
    template_name = "system/organisation_view.html"

class LeadershipView(TemplateView):
    template_name = "system/leadership_view.html"

class PlanningView(TemplateView):
    template_name = "system/planning_view.html"

class SupportView(TemplateView):
    template_name = "system/support_view.html"

class OrganisationDetailView(DetailView):
    template_name = 'admin/organisation/organisation_detail.html'
    model = Organisation

    def get_context_data(self, **kwargs):
        context = super(OrganisationDetailView, self).get_context_data(**kwargs)
        context['available_apps'] = admin.site.get_app_list(self.request)
        context['title'] = "Home"
        return context