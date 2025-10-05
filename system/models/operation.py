from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from system.models import Organisation

User = get_user_model()


# --------------------
# Operational Planning & Control
# --------------------
class SOP(models.Model):
    """
    Standard Operating Procedures or Work Instructions for service delivery.
    """
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=150, choices=[("operations", "Operations"), ("QA", "Quality Assurance")])
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="qms/sops/%Y/%m/%d/")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_sops")
    created_at = models.DateTimeField(auto_now_add=True)
    review_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "SOP"
        verbose_name_plural = "SOPs"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# --------------------
# Customer Requirements
# --------------------
class ContractReview(models.Model):
    """
    Records review of customer contracts and requirements.
    """
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    customer_name = models.CharField(max_length=255)
    contract_number = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=150, choices=[("sales", "Sales"), ("QA", "Quality Assurance")])
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="contract_reviews")
    review_date = models.DateField(default=timezone.now)
    findings = models.TextField(blank=True, null=True)
    document_reference = models.FileField(upload_to="qms/contract_reviews/%Y/%m/%d/", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Contract Review"
        verbose_name_plural = "Contract Reviews"
        ordering = ["-review_date"]

    def __str__(self):
        return f"{self.customer_name} - {self.contract_number or 'No Contract'}"


# --------------------
# Design & Development
# --------------------
class DesignProject(models.Model):
    """
    Represents a design/development project (if applicable)
    """
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=150, choices=[("technical", "Technical"), ("QA", "Quality Assurance")])
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="design_projects")
    start_date = models.DateField(default=timezone.now)
    planned_end_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=[("planned", "Planned"), ("in_progress", "In Progress"), ("completed", "Completed"), ("on_hold", "On Hold")],
        default="planned"
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Design Project"
        verbose_name_plural = "Design Projects"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title


class DesignRecord(models.Model):
    """
    Stores design & development evidence (plan, review, verification, validation)
    """
    project = models.ForeignKey(DesignProject, on_delete=models.CASCADE, related_name="records")
    record_type = models.CharField(
        max_length=100,
        choices=[("plan", "Plan"), ("review", "Review"), ("verification", "Verification"), ("validation", "Validation"), ("other", "Other")]
    )
    description = models.TextField(blank=True, null=True)
    document_file = models.FileField(upload_to="qms/design_records/%Y/%m/%d/")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_design_records")
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Design Record"
        verbose_name_plural = "Design Records"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.record_type} - {self.project.title}"


# --------------------
# Control of External Providers
# --------------------
class SupplierEvaluation(models.Model):
    """
    Evaluate and monitor suppliers/contractors.
    """
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    supplier_type = models.CharField(max_length=100, blank=True, null=True)
    contact_person = models.CharField(max_length=150, blank=True, null=True)
    contact_info = models.CharField(max_length=255, blank=True, null=True)
    evaluation_date = models.DateField(default=timezone.now)
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="evaluated_suppliers")
    evaluation_result = models.TextField(blank=True, null=True)
    document_reference = models.FileField(upload_to="qms/supplier_evaluations/%Y/%m/%d/", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Supplier Evaluation"
        verbose_name_plural = "Supplier Evaluations"
        ordering = ["-evaluation_date"]

    def __str__(self):
        return f"{self.name} ({self.evaluation_date})"


# --------------------
# Service Delivery
# --------------------
class ServiceReport(models.Model):
    """
    Records delivery of services per requirements.
    """
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    service_provider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="service_reports")
    service_date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    compliance_with_requirements = models.BooleanField(default=True)
    document_reference = models.FileField(upload_to="qms/service_reports/%Y/%m/%d/", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Service Report"
        verbose_name_plural = "Service Reports"
        ordering = ["-service_date"]

    def __str__(self):
        return f"{self.title} ({self.service_date})"


# --------------------
# Release of Products/Services
# --------------------
class ProductRelease(models.Model):
    """
    Verify and approve products/services before delivery.
    """
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    product_name = models.CharField(max_length=255)
    release_date = models.DateField(default=timezone.now)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="product_approvals")
    description = models.TextField(blank=True, null=True)
    document_reference = models.FileField(upload_to="qms/product_approvals/%Y/%m/%d/", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending"
    )

    class Meta:
        verbose_name = "Product Release"
        verbose_name_plural = "Product Releases"
        ordering = ["-release_date"]

    def __str__(self):
        return f"{self.product_name} ({self.get_status_display()})"


# --------------------
# Nonconforming Outputs
# --------------------
class NCRRegister(models.Model):
    """
    Identify, control, and correct nonconformities.
    """
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reported_ncrs")
    department = models.CharField(max_length=150, choices=[("QA", "QA"), ("Operations", "Operations")], default="QA")
    description = models.TextField()
    detected_date = models.DateField(default=timezone.now)
    corrective_action_taken = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=[("open", "Open"), ("in_progress", "In Progress"), ("closed", "Closed")],
        default="open"
    )
    document_reference = models.FileField(upload_to="qms/ncr/%Y/%m/%d/", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Nonconforming Output"
        verbose_name_plural = "NCR Register"
        ordering = ["-detected_date"]

    def __str__(self):
        return f"{self.title} ({self.status})"
