from django.urls import path, include
from system.views import HomeView, OrganisationView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("organisation", OrganisationView.as_view(), name="organisation-menu"),
    path("organisation/detail/<int:pk>/", OrganisationView.as_view(), name="organisation-detail")
]