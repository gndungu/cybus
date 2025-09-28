import traceback
import logging
from django.conf import settings
from django.shortcuts import render, redirect
from django.db import transaction
from django.urls import reverse_lazy
from django.views import View
from django.contrib import admin, messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, DetailView

from system.models import Organisation
from .forms import RegistrationForm

logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = "admin/login.html"

    def form_valid(self, form):
        # Call the parent class's form_valid method to perform standard login
        self.request.session['otp_verified'] = False
        response = super().form_valid(form)
        return response  # Redirect to the default success URL

    def get_success_url(self):
        # Define the custom success URL where you want to redirect the user
        # return reverse_lazy('otp-verification')  # Replace 'custom_dashboard' with your desired URL name
        # if Subscription.objects.filter(organisation=self.request.user):
        #     pass
        if self.request.user.is_superuser:
            return reverse_lazy('admin:index')
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        # Get the parent context data
        context = super().get_context_data(**kwargs)

        # Add custom context data
        context['title'] = 'Login'

        return context


class RegisterView(View):
    template_name = 'registration/register.html'
    title = "Sign Up"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('admin:index')  # Redirect to the index page if the user is already logged in
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = RegistrationForm()
        return render(request, self.template_name, {'form': form, 'title': self.title})

    def post(self, request):
        form = RegistrationForm(request.POST)

        if not form.is_valid():
            # Form is invalid — re-render page with errors
            return render(request, self.template_name, {'form': form, 'title': self.title})

        try:
            with transaction.atomic():
                # Register the user
                user = form.register_user()
                print(user)
                # Create organisation linked to user
                Organisation.objects.create(
                    representative=user,
                    name=form.cleaned_data['company_name']
                )

            messages.success(
                request,
                "Sign Up successful. Your password has been sent to your email."
            )
            return redirect(reverse_lazy("login"))

        except Exception as e:
            # Log full traceback for debugging
            logger.error("Registration error: %s", str(e))
            logger.debug(traceback.format_exc())
            form.add_error(None, f"Sorry, something went wrong during registration. {e}")
            return render(request, self.template_name, {'form': form, 'title': self.title})