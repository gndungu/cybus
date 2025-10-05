from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from system.models import Organisation, TimeStampMixin

User = get_user_model()


# --------------------
# Resource Management
# --------------------
class ResourcePlan(TimeStampMixin):
    """
    Tracks resources provided by management (people, equipment, IT, facilities)
    """
    RESOURCE_TYPES = [
        ("people", "People"),
        ("equipment", "Equipment"),
        ("IT", "IT Systems"),
        ("facility", "Facility"),
        ("other", "Other"),
    ]
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    description = models.TextField(blank=True, null=True)
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="resource_plans")
    planned_date = models.DateField(default=timezone.now)
    review_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, default="planned", choices=[("planned", "Planned"), ("provided", "Provided"), ("reviewed", "Reviewed")])
    notes = models.TextField(blank=True, null=True)
    document_reference = models.FileField(upload_to="qms/resource_plans/", blank=True, null=True)

    class Meta:
        verbose_name = "Resource Plan"
        verbose_name_plural = "Resource Plans"
        ordering = ["-planned_date"]

    def __str__(self):
        return f"{self.title} ({self.resource_type})"


# --------------------
# Competence & Training
# --------------------
class TrainingRecord(TimeStampMixin):
    """
    Records training needs, completion, and effectiveness assessment
    """
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="trainings")
    training_type = models.CharField(max_length=150, blank=True, null=True)
    date_conducted = models.DateField(default=timezone.now)
    effectiveness = models.TextField(blank=True, null=True, help_text="Assessment of training effectiveness")
    trainer = models.CharField(max_length=150, blank=True, null=True)
    document_reference = models.FileField(upload_to="qms/training_records/", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Training Record"
        verbose_name_plural = "Training Records"
        ordering = ["-date_conducted"]

    def __str__(self):
        return f"{self.title} - {self.employee}"


# --------------------
# Awareness
# --------------------
class AwarenessRecord(TimeStampMixin):
    """
    Records communication of quality policy, objectives, and roles
    """
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    target_audience = models.TextField(help_text="Who received the communication")
    method = models.CharField(max_length=150, help_text="e.g., Meeting, Email, Poster, Training")
    date = models.DateField(default=timezone.now)
    communicator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="awareness_communicated")
    document_reference = models.FileField(upload_to="qms/awareness_records/", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Awareness Record"
        verbose_name_plural = "Awareness Records"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} ({self.method})"


# --------------------
# Communication
# --------------------
class CommunicationPlan(TimeStampMixin):
    """
    Defines internal/external communication channels and responsibilities
    """
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    audience = models.TextField(help_text="Target audience")
    method = models.CharField(max_length=150)
    responsible_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="communication_plans")
    frequency = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Weekly, Monthly")
    start_date = models.DateField(default=timezone.now)
    review_date = models.DateField(blank=True, null=True)
    document_reference = models.FileField(upload_to="qms/communication_plans/", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Communication Plan"
        verbose_name_plural = "Communication Plans"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title


# --------------------
# Documented Information
# --------------------
class DocumentRegister(TimeStampMixin):
    """
    Registers controlled documents such as procedures, manuals, and records
    """
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=150, blank=True, null=True)
    responsible_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="document_registers")
    issue_date = models.DateField(default=timezone.now)
    revision_date = models.DateField(blank=True, null=True)
    version = models.CharField(max_length=50, blank=True, null=True)
    file = models.FileField(upload_to="qms/document_registers/")
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Document Register"
        verbose_name_plural = "Document Registers"
        ordering = ["-issue_date"]

    def __str__(self):
        return f"{self.title} (v{self.version})"
