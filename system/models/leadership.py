from django.db import models
from django.conf import settings
from django.utils import timezone


from system.models import TimeStampMixin, Organisation


class LeadershipCommitment(models.Model):
    """Represents a formal leadership commitment (policy or statement).

    Examples: "Top management commits to provide resources for QMS",
    "Leadership will ensure a quality culture", etc.
    """

    COMMITMENT_TYPES = [
        ("policy", "Policy"),
        ("statement", "Statement"),
        ("plan", "Plan"),
        ("other", "Other"),
    ]
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    commitment_type = models.CharField(max_length=30, choices=COMMITMENT_TYPES, default="statement")
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="commitments")
    effective_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(blank=True, null=True)

    # structured resource info (can store budget, staff, equipment, etc.)
    resources = models.JSONField(blank=True, null=True)

    # status (draft, active, archived)
    is_active = models.BooleanField(default=True)

    related_documents = models.TextField(blank=True, help_text="URLs or internal refs to related documents")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-effective_date", "title"]

    def __str__(self):
        return f"{self.title} ({self.get_commitment_type_display()})"


class AccountabilityAssignment(models.Model):
    """Link people/roles to specific accountability items for a commitment."""

    commitment = models.ForeignKey(LeadershipCommitment, on_delete=models.CASCADE, related_name="accountabilities")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="qms_accountabilities")
    role = models.CharField(max_length=150, blank=True, help_text="Role or responsibility title e.g. 'QMS Sponsor', 'Process Owner'")
    responsibility_description = models.TextField(blank=True)

    # optional target date for completing the accountability
    target_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("commitment", "user", "role"),)

    def __str__(self):
        return f"{self.user} — {self.role or 'Accountable'} for {self.commitment.title}"


class CommitmentObjective(models.Model):
    """Specific measurable objectives derived from a leadership commitment."""

    commitment = models.ForeignKey(LeadershipCommitment, on_delete=models.CASCADE, related_name="objectives")
    description = models.TextField()
    metric = models.CharField(max_length=150, blank=True, help_text="e.g. 'Customer complaints per month'")
    baseline = models.CharField(max_length=100, blank=True)
    target = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Objective for {self.commitment.title}: {self.description[:60]}"


class CommitmentAction(models.Model):
    """Actions or tasks created to implement a commitment or achieve its objectives."""

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
        ("blocked", "Blocked"),
    ]

    commitment = models.ForeignKey(LeadershipCommitment, on_delete=models.CASCADE, related_name="actions")
    objective = models.ForeignKey(CommitmentObjective, on_delete=models.SET_NULL, related_name="actions", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="qms_actions")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="open")
    progress_notes = models.TextField(blank=True)
    due_date = models.DateField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class CommitmentReview(models.Model):
    """Periodic review/audit record for a leadership commitment."""
    commitment = models.ForeignKey(LeadershipCommitment, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="qms_reviews")
    review_date = models.DateField(default=timezone.now)
    findings = models.TextField(blank=True)
    conclusions = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    next_review_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-review_date"]

    def __str__(self):
        return f"Review {self.review_date} — {self.commitment.title}"


class CommunicationRecord(models.Model):
    """Records how leadership commitments were communicated (meetings, emails, trainings)."""
    commitment = models.ForeignKey(LeadershipCommitment, on_delete=models.CASCADE, related_name="communications")
    method = models.CharField(max_length=150, help_text="e.g. 'Townhall', 'Email', 'Training', 'Poster'")
    audience = models.TextField(blank=True, help_text="Who received the communication")
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    materials = models.TextField(blank=True, help_text="links or references to presentation, minutes, handouts")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} on {self.date} for {self.commitment.title}"


# Optional lightweight helper model for attachments if you want file storage
class CommitmentAttachment(models.Model):
    commitment = models.ForeignKey(LeadershipCommitment, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="qms/commitments/%Y/%m/%d/")
    description = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


class QualityPolicy(TimeStampMixin):
    """Represents the organisation's Quality Policy and its lifecycle."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, default="Quality Policy")
    content = models.TextField(help_text="The actual text of the quality policy")
    developed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="developed_policies")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approved_policies", null=True, blank=True)
    approval_date = models.DateField(blank=True, null=True)
    effective_date = models.DateField(default=timezone.now)
    review_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-effective_date"]

    def __str__(self):
        return f"Quality Policy (Effective {self.effective_date})"


class QualityPolicyCommunication(TimeStampMixin):
    """Records how the Quality Policy was communicated and displayed."""
    policy = models.ForeignKey(QualityPolicy, on_delete=models.CASCADE, related_name="communications")
    method = models.CharField(max_length=150, help_text="e.g. 'Email', 'Training', 'Notice Board', 'Intranet'")
    audience = models.TextField(blank=True, help_text="Who received the policy communication")
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    evidence_file = models.FileField(upload_to="qms/quality_policy/communications/%Y/%m/%d/", blank=True, null=True)

    def __str__(self):
        return f"{self.method} on {self.date} for {self.policy.title}"


class QualityPolicyEvidence(models.Model):
    """Evidence records to demonstrate that the Quality Policy is communicated and displayed."""
    policy = models.ForeignKey(QualityPolicy, on_delete=models.CASCADE, related_name="evidences")
    description = models.CharField(max_length=255, help_text="Description of the evidence, e.g. 'Photo of policy on notice board'")
    file = models.FileField(upload_to="qms/quality_policy/evidence/%Y/%m/%d/", blank=True, null=True)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description


class Risk(TimeStampMixin):
    """Identified risk within the QMS."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    identified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="identified_risks")
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
    identified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="identified_opportunities")
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
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="risk_opportunity_responses")
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Response to {target}: {self.get_response_type_display()}"
