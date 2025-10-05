from django.apps import apps
from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.contrib.auth import views as auth_views
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.urls import path
from django.shortcuts import render

from system.models import OrganisationUser, ChangeControlRecord, QMSChange, JobDescription, Role, OrganizationChart
from system.models.organisation import Organisation, OrganisationLocation, OrganisationDepartment, \
    SWOTEntry, PESTLEEntry, ScopeStatement, StakeholderRequirement, Stakeholder
from system.models import (
    LeadershipCommitment,
    AccountabilityAssignment,
    CommitmentObjective,
    CommitmentAction,
    CommitmentReview,
    CommunicationRecord,
    CommitmentAttachment,
    QualityPolicy,
    QualityPolicyCommunication,
    QualityPolicyEvidence,
    Risk,
    Opportunity,
    RiskOpportunityResponse,
)
from system.models.support import ResourcePlan, TrainingRecord, AwarenessRecord, CommunicationPlan, DocumentRegister


class OrganisationLocationInline(admin.StackedInline):
    model = OrganisationLocation
    extra = 1


class DepartmentInline(admin.StackedInline):
    model = OrganisationDepartment
    extra = 1


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'address', 'tin_number', 'region', 'phone', 'sector', 'action_button']
    inlines = [OrganisationLocationInline, DepartmentInline]

    def action_button(self, obj):
        url = reverse('organisation-detail', args=[obj.pk])  # or your custom URL
        return format_html('<a class="btn btn-block btn-outline-primary" href="{}"><i class="fas fa-book"></i> OPEN</a>', url)

    action_button.short_description = 'Action'
    action_button.allow_tags = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate()  # if needed, for related fields
        if not request.user.is_superuser:
            qs = qs.filter(representative=request.user)
            try:
                orguser = OrganisationUser.objects.get(request.user)
                qs = qs.filter(pk=orguser.organisation.id)
            except OrganisationUser.DoesNotExist:
                pass
        return qs

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            cl = response.context_data['cl']
            for result in cl.result_list:
                setattr(result, '_admin_url_id', result.pk)
        except (AttributeError, KeyError):
            pass
        return response


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['department', 'organisation']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate()  # if needed, for related fields
        if not request.user.is_superuser:
            qs = qs.filter(representative=request.user)
        return qs


class StakeholderRequirementInline(admin.StackedInline):
    model = StakeholderRequirement
    extra = 1


@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "contact_person", "contact_info", "created_by", "created_at")
    list_filter = ("category",)
    search_fields = ("name", "contact_person", "relevance_to_qms")
    date_hierarchy = "created_at"
    inlines = [StakeholderRequirementInline]
    # autocomplete_fields = ["created_by"]


class SWOTEntryAdmin(admin.ModelAdmin):
    list_display = ['organisation', 'swot_type', 'description']


class PESTLEEntryAdmin(admin.ModelAdmin):
    list_display = ['organisation', 'pestle_type', 'description']


class ScopeStatementAdmin(admin.ModelAdmin):
    list_display = ['organisation', 'text', 'approved_date']


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['organisation', 'name', 'designation', 'role']


#Leadership UI
# ---------- INLINE ADMIN CLASSES ----------

class AccountabilityAssignmentInline(admin.StackedInline):
    model = AccountabilityAssignment
    extra = 1
    # autocomplete_fields = ["user"]
    fields = ("user", "role", "responsibility_description", "target_date")
    show_change_link = True


class CommitmentObjectiveInline(admin.StackedInline):
    model = CommitmentObjective
    extra = 1
    fields = ("description", "metric", "baseline", "target", "unit", "start_date", "end_date", "is_active")
    show_change_link = True


class CommitmentActionInline(admin.StackedInline):
    model = CommitmentAction
    extra = 1
    # autocomplete_fields = ["owner"]
    fields = ("title", "status", "due_date", "completed_at")
    show_change_link = True


class CommitmentReviewInline(admin.StackedInline):
    model = CommitmentReview
    extra = 0
    # autocomplete_fields = ["reviewer"]
    fields = ("review_date", "conclusions", "next_review_date")
    show_change_link = True


class CommunicationRecordInline(admin.StackedInline):
    model = CommunicationRecord
    extra = 0
    fields = ("method", "audience", "date", "notes")
    show_change_link = True


class CommitmentAttachmentInline(admin.StackedInline):
    model = CommitmentAttachment
    extra = 0
    fields = ("file", "description", "uploaded_by", "uploaded_at")
    readonly_fields = ("uploaded_at",)
    show_change_link = True


# ---------- MAIN ADMIN MODELS ----------

@admin.register(LeadershipCommitment)
class LeadershipCommitmentAdmin(admin.ModelAdmin):
    list_display = ("title", "commitment_type", "leader", "effective_date", "expiry_date", "is_active")
    list_filter = ("commitment_type", "is_active", "effective_date")
    search_fields = ("title", "summary", "leader__username")
    date_hierarchy = "effective_date"
    # autocomplete_fields = ["leader", "organisation"]
    inlines = [
        AccountabilityAssignmentInline,
        CommitmentObjectiveInline,
        CommitmentActionInline,
        CommunicationRecordInline,
        CommitmentReviewInline,
        CommitmentAttachmentInline,
    ]
    fieldsets = (
        (None, {
            "fields": (
                "organisation",
                "title",
                "summary",
                "commitment_type",
                "leader",
                "effective_date",
                "expiry_date",
                "is_active",
            )
        }),
        ("Resources & References", {
            "fields": ("resources", "related_documents"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ("created_at", "updated_at")


# @admin.register(QualityPolicyCommunication)
# class QualityPolicyCommunicationAdmin(admin.ModelAdmin):
#     list_display = ("policy", "method", "date", "audience")
#     search_fields = ("method", "audience", "notes")
#     date_hierarchy = "date"
#     # autocomplete_fields = ["policy"]
#
#
# @admin.register(QualityPolicyEvidence)
# class QualityPolicyEvidenceAdmin(admin.ModelAdmin):
#     list_display = ("policy", "description", "submitted_by", "submitted_at")
#     # autocomplete_fields = ["policy", "submitted_by"]
#     readonly_fields = ("submitted_at",)
#     date_hierarchy = "submitted_at"


class QualityPolicyCommunicationInline(admin.StackedInline):
    model = QualityPolicyCommunication
    extra = 1
    fields = ("method", "audience", "date", "notes", "evidence_file")
    show_change_link = True


class QualityPolicyEvidenceInline(admin.StackedInline):
    model = QualityPolicyEvidence
    extra = 1
    fields = ("description", "file", "submitted_by", "submitted_at")
    readonly_fields = ("submitted_at",)
    show_change_link = True


@admin.register(QualityPolicy)
class QualityPolicyAdmin(admin.ModelAdmin):
    list_display = ("title", "developed_by", "approved_by", "effective_date", "is_active")
    list_filter = ("is_active", "effective_date")
    search_fields = ("title", "content")
    # autocomplete_fields = ["developed_by", "approved_by", "organisation"]
    date_hierarchy = "effective_date"
    inlines = [
        QualityPolicyCommunicationInline,
        QualityPolicyEvidenceInline,
    ]


class JobDescriptionInline(admin.StackedInline):
    model = JobDescription
    extra = 0


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "reports_to", "is_active")
    list_filter = ("department", "is_active")
    search_fields = ("title", "purpose")
    inlines = [JobDescriptionInline]
    # autocomplete_fields = ["department", "reports_to"]


@admin.register(OrganizationChart)
class OrganizationChartAdmin(admin.ModelAdmin):
    list_display = ("title", "version", "date_issued", "uploaded_by")
    search_fields = ("title", "version")
    date_hierarchy = "date_issued"
    # autocomplete_fields = ["uploaded_by"]


# Planning
@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ("title", "identified_by", "identified_date", "likelihood", "impact", "score", "status")
    list_filter = ("status", "identified_date")
    search_fields = ("title", "description")
    # autocomplete_fields = ["identified_by", "organisation"]
    readonly_fields = ("score",)
    date_hierarchy = "identified_date"


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "identified_by", "identified_date", "benefit", "feasibility", "score", "status")
    list_filter = ("status", "identified_date")
    search_fields = ("title", "description")
    # autocomplete_fields = ["identified_by", "organisation"]
    readonly_fields = ("score",)
    date_hierarchy = "identified_date"


@admin.register(RiskOpportunityResponse)
class RiskOpportunityResponseAdmin(admin.ModelAdmin):
    list_display = ("response_type", "owner", "status", "due_date", "risk", "opportunity")
    list_filter = ("response_type", "status")
    search_fields = ("description",)
    # autocomplete_fields = ["owner", "risk", "opportunity"]
    date_hierarchy = "due_date"
    fieldsets = (
        (None, {
            "fields": (
                "risk",
                "opportunity",
                "response_type",
                "description",
                "owner",
                "due_date",
                "status",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ("created_at", "updated_at")


class ChangeControlRecordInline(admin.StackedInline):
    model = ChangeControlRecord
    extra = 1


@admin.register(QMSChange)
class QMSChangeAdmin(admin.ModelAdmin):
    list_display = ("title", "requested_by", "department", "status", "planned_date", "approved_by", "implemented_by")
    list_filter = ("status", "department", "planned_date")
    search_fields = ("title", "description", "department")
    date_hierarchy = "planned_date"
    inlines = [ChangeControlRecordInline]


#Support
@admin.register(ResourcePlan)
class ResourcePlanAdmin(admin.ModelAdmin):
    list_display = ("title", "resource_type", "responsible", "planned_date", "status")
    list_filter = ("resource_type", "status")
    search_fields = ("title", "description")
    date_hierarchy = "planned_date"
    # autocomplete_fields = ["responsible"]


@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = ("title", "employee", "training_type", "date_conducted", "trainer")
    search_fields = ("title", "training_type", "trainer")
    date_hierarchy = "date_conducted"
    # autocomplete_fields = ["employee"]


@admin.register(AwarenessRecord)
class AwarenessRecordAdmin(admin.ModelAdmin):
    list_display = ("title", "method", "date", "communicator")
    search_fields = ("title", "method", "target_audience")
    date_hierarchy = "date"
    # autocomplete_fields = ["communicator"]


@admin.register(CommunicationPlan)
class CommunicationPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "method", "responsible_person", "start_date", "frequency")
    search_fields = ("title", "method", "audience")
    date_hierarchy = "start_date"
    # autocomplete_fields = ["responsible_person"]


@admin.register(DocumentRegister)
class DocumentRegisterAdmin(admin.ModelAdmin):
    list_display = ("title", "document_type", "version", "responsible_person", "issue_date")
    search_fields = ("title", "document_type")
    date_hierarchy = "issue_date"
    # autocomplete_fields = ["responsible_person"]


# Register your custom user model with the custom admin class
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(OrganisationDepartment, DepartmentAdmin)
admin.site.register(SWOTEntry, SWOTEntryAdmin)
admin.site.register(PESTLEEntry, PESTLEEntryAdmin)
admin.site.register(ScopeStatement, ScopeStatementAdmin)

