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

from system.models.organisation import Organisation, OrganisationDepartment, OrganisationLocation


class OrganisationForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = ['name', 'address', 'tin_number', 'region', 'phone', 'email', 'sector', 'evaluation_level', 'status', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # important for formsets
        self.helper.layout = Layout(
            Row(Column('name', css_class='form-group col-md-6')),
            Row(Column('tin_number', css_class='form-group col-md-6')),
            Row(Column('address', css_class='form-group col-md-12')),
            Row(Column('phone', css_class='form-group col-md-6'),
                Column('email', css_class='form-group col-md-6')),
            Row(Column('region', css_class='form-group col-md-6'),
                Column('sector', css_class='form-group col-md-6')),
            Row(Column('evaluation_level', css_class='form-group col-md-6')),
            Row(Column('notes', css_class='form-group col-md-12')),
        )


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = OrganisationDepartment
        fields = ['name', 'coordinator']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(Column('name', css_class='form-group col-md-6'),
                Column('coordinator', css_class='form-group col-md-6')),
        )


class OrganisationLocationForm(forms.ModelForm):
    class Meta:
        model = OrganisationLocation
        fields = ['address', 'city', 'district', 'region', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(Column('address', css_class='form-group col-md-6'),
                Column('city', css_class='form-group col-md-6')),
            Row(Column('district', css_class='form-group col-md-6'),
                Column('region', css_class='form-group col-md-6')),
            Row(Column('notes', css_class='form-group col-md-12')),
        )


DepartmentFormSet = inlineformset_factory(
    Organisation, OrganisationDepartment, form=DepartmentForm,
    fields=['name', 'coordinator'], extra=1, can_delete=True
)


LocationFormSet = inlineformset_factory(
    Organisation, OrganisationLocation, form=OrganisationLocationForm,
    fields=['address', 'city', 'district', 'region', 'notes'], extra=1, can_delete=True
)