# forms.py
import random
import string
import traceback

from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.db import transaction
from django.forms import inlineformset_factory

from account.models import CustomUser
from system.models.organisation import Organisation

class RegistrationForm(forms.Form):
    full_name = forms.CharField(label='Full Name')
    email = forms.EmailField(label='Email')
    phone_number = forms.CharField(label='Phone Number')
    company_name = forms.CharField(label="Company / Organisation Name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('full_name', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('company_name', css_class='form-group col-md-12 mb-3'),
            ),
            Submit('register', 'Register', css_class='btn btn-primary btn-block')
        )
    #

    def clean(self):
        data = super().clean()  # ensures field-specific clean() methods run
        email = data.get('email')
        phone_number = data.get('phone_number')
        company_name = data.get('company_name')

        if email and CustomUser.objects.filter(email=email).exists():
            self.add_error('email', 'Email exists. Please provide another email')

        if phone_number and CustomUser.objects.filter(phone_number=phone_number).exists():
            self.add_error('phone_number', 'Phone Number exists. Please provide another phonenumber')

        if company_name and Organisation.objects.filter(name=company_name).exists():
            self.add_error('company_name', 'Company / Organisation exists. Please provide another company name')

        return data


    def send_password_email(self, password):
        subject = 'Your Password for Registration'
        message = f'Hello {self.cleaned_data["full_name"]}, your password is: {password}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.cleaned_data["email"]]
        # Sample data for the SMS
        sms_data = {
            'recipient': self.cleaned_data["phone_number"],  # Phone number of the recipient
            'message': message,  # Content of the message
        }
        # Call the send_sms function with the sample data
        # sent_message = send_sms(sms_data)
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    def register_user(self):
        # Generate a random password
        password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
        try:
            with transaction.atomic():
                # Create a new user with the provided information
                user = CustomUser.objects.create(email=self.cleaned_data['email'], phone_number=self.cleaned_data.get('phone_number'), is_active=True, is_staff=True, account_type=CustomUser.AccountType.CUSTOMER)
                user.full_name= f"{self.cleaned_data['full_name']} "
                user.set_password(password)

                self.send_password_email(password)

                # Create or get the "SMS users" group
                sms_users_group, created = Group.objects.get_or_create(name=CustomUser.AccountType.CUSTOMER)

                # Add the user to the "SMS users" group
                user.groups.add(sms_users_group)
                user.save()
                return user
        except Exception as e:
            print("Exception occurred:")
            traceback.print_exc()  # <-- This prints full traceback to the console
            # raise forms.ValidationError(e)
            return None