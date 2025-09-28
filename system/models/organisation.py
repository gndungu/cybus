from django.db import models

from account.models import CustomUser
from system.models.modelmixin import TimeStampMixin


class Organisation(TimeStampMixin):

    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'PENDING'
        ACTIVE = 'ACTIVE', 'ACTIVE'

    class Meta:
        verbose_name_plural = "Organisation"
        db_table = "Organisation"

    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    tin_number = models.CharField(max_length=255, null=True, blank=True)
    region = models.ForeignKey("conf.Region", on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    sector = models.ForeignKey("conf.Sector", on_delete=models.SET_NULL, null=True, blank=True)
    representative = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="organisation_representative")
    evaluation_level = models.ForeignKey("conf.EvaluationLevel", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=120, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class OrganisationUser(TimeStampMixin):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="organisation_user")

    class Meta:
        unique_together = ['organisation', 'user']

    def __str__(self):
        return f"{self.user.full_name} - {self.organisation.name}"


class OrganisationLocation(TimeStampMixin):
    class Meta:
        verbose_name_plural = "Organisation Location"
        db_table = "organisation_location"

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    district = models.ForeignKey('conf.District', on_delete=models.CASCADE, null=True, blank=True)
    region = models.ForeignKey('conf.Region', on_delete=models.CASCADE, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)


class OrganisationDepartment(TimeStampMixin):
    class Meta:
        verbose_name_plural = "Departments"
        db_table = "department"

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    department = models.ForeignKey("conf.Department", on_delete=models.SET_NULL, null=True)
    coordinator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name="department_coordinator")

    def __str__(self):
        return f"{self.name}"


class Role(models.Model):
    """Represents a role, department or person responsible for clause actions."""
    organisation = models.OneToOneField(
        Organisation,
        on_delete=models.CASCADE,
        related_name='organisation_role'
    )
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Employee(TimeStampMixin):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=120, null=True, blank=True, verbose_name="Job Title")
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    employee_id = models.CharField(max_length=50, null=True, blank=True, unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return f"{self.name} ({self.designation or 'No Title'})"


class SWOTEntry(TimeStampMixin):
    SWOT_TYPE_CHOICES = (
        ('strength', 'Strength'),
        ('weakness', 'Weakness'),
        ('opportunity', 'Opportunity'),
        ('threat', 'Threat'),
    )

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name='swot_entries'
    )
    swot_type = models.CharField(max_length=20, choices=SWOT_TYPE_CHOICES)
    description = models.TextField()

    class Meta:
        verbose_name = "SWOT Entry"
        verbose_name_plural = "SWOT Entries"
        ordering = ['swot_type', 'created_at']

    def __str__(self):
        return f"{self.get_swot_type_display()}: {self.description[:50]}"


class PESTLEEntry(TimeStampMixin):
    PESTLE_TYPE_CHOICES = (
        ('political', 'Political'),
        ('economic', 'Economic'),
        ('social', 'Social'),
        ('technological', 'Technological'),
        ('legal', 'Legal'),
        ('environmental', 'Environmental'),
    )

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name='pestle_entries'
    )
    pestle_type = models.CharField(max_length=20, choices=PESTLE_TYPE_CHOICES)
    description = models.TextField()

    class Meta:
        verbose_name = "PESTLE Entry"
        verbose_name_plural = "PESTLE Entries"
        ordering = ['pestle_type', 'created_at']

    def __str__(self):
        return f"{self.get_pestle_type_display()}: {self.description[:50]}"


class ScopeStatement(TimeStampMixin):
    organisation = models.OneToOneField(
        Organisation,
        on_delete=models.CASCADE,
        related_name='scope_statement'
    )
    text = models.TextField()
    approved_by = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    approved_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Scope Statement for {self.clause.clause}"


class Document(models.Model):
    """Optional attached record/evidence (could be a pointer to a file, link or note)."""
    organisation = models.OneToOneField(
        Organisation,
        on_delete=models.CASCADE,
        related_name='organisation_document'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='qms/document/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title