from django.db import models
from django.conf import settings
from django.utils import timezone
from system.models import TimeStampMixin, Organisation

from django.contrib.auth import get_user_model

User = get_user_model()


class Risk(TimeStampMixin):
    """Identified risk within the QMS."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    identified_by = models.ForeignKey("account.CustomUser", on_delete=models.PROTECT, related_name="identified_risks")
    identified_date = models.DateField(default=timezone.now)
    likelihood = models.PositiveSmallIntegerField(help_text="Scale 1 (Low) - 5 (High)")
    impact = models.PositiveSmallIntegerField(help_text="Scale 1 (Low) - 5 (High)")
    score = models.PositiveSmallIntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, default="open", help_text="e.g. open, mitigated, closed")

    def save(self, *args, **kwargs):
        if self.likelihood and self.impact:
            self.score = self.likelihood * self.impact
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Risk: {self.title} (Score {self.score})"


class Opportunity(TimeStampMixin):
    """Identified opportunity within the QMS."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    identified_by = models.ForeignKey("account.CustomUser", on_delete=models.PROTECT, related_name="identified_opportunities")
    identified_date = models.DateField(default=timezone.now)
    benefit = models.PositiveSmallIntegerField(help_text="Scale 1 (Low) - 5 (High)")
    feasibility = models.PositiveSmallIntegerField(help_text="Scale 1 (Low) - 5 (High)")
    score = models.PositiveSmallIntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, default="open", help_text="e.g. open, implemented, closed")

    def save(self, *args, **kwargs):
        if self.benefit and self.feasibility:
            self.score = self.benefit * self.feasibility
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Opportunity: {self.title} (Score {self.score})"


class RiskOpportunityResponse(models.Model):
    """Plans and actions in response to risks or opportunities."""
    RESPONSE_TYPES = [
        ("mitigate", "Mitigate"),
        ("accept", "Accept"),
        ("transfer", "Transfer"),
        ("avoid", "Avoid"),
        ("exploit", "Exploit"),
        ("enhance", "Enhance"),
        ("share", "Share"),
    ]

    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name="responses", null=True, blank=True)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="responses", null=True, blank=True)
    response_type = models.CharField(max_length=50, choices=RESPONSE_TYPES)
    description = models.TextField()
    owner = models.ForeignKey("account.CustomUser", on_delete=models.PROTECT, related_name="risk_opportunity_responses")
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Response to : {self.get_response_type_display()}"


class QMSChange(models.Model):
    """
    Represents a planned or implemented change to the QMS.
    """
    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("implemented", "Implemented"),
        ("rejected", "Rejected"),
        ("closed", "Closed"),
    ]

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Describe the nature and reason for the change.")
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="qms_changes_requested")
    department = models.CharField(max_length=150, blank=True, null=True)
    planned_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="qms_changes_approved")
    approved_date = models.DateField(blank=True, null=True)
    implemented_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="qms_changes_implemented")
    implemented_date = models.DateField(blank=True, null=True)
    impact_assessment = models.TextField(blank=True, null=True, help_text="Describe potential impacts of the change on QMS processes.")
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "QMS Change"
        verbose_name_plural = "QMS Changes"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ChangeControlRecord(models.Model):
    """
    Detailed control record linked to a QMS change.
    """
    change = models.ForeignKey(QMSChange, on_delete=models.CASCADE, related_name="control_records")
    control_action = models.CharField(max_length=255, help_text="Describe the control or action taken.")
    responsible_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="change_controls_responsible")
    control_date = models.DateField()
    verification = models.TextField(blank=True, null=True, help_text="Describe verification or validation of the change.")
    document_reference = models.CharField(max_length=255, blank=True, null=True)
    evidence = models.FileField(upload_to="qms/change_evidence/", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Change Control Record"
        verbose_name_plural = "Change Control Records"
        ordering = ["-control_date"]

    def __str__(self):
        return f"Control for {self.change.title}"