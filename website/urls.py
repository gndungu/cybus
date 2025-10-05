from django.urls import path, include
from system.views import HomeView, OrganisationView, LeadershipView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("organisation", OrganisationView.as_view(), name="organisation-menu"),
    path("leadership", LeadershipView.as_view(), name="leadership-menu"),
    path("organisation/detail/<int:pk>/", OrganisationView.as_view(), name="organisation-detail")
]