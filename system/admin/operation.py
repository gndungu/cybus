from django.contrib import admin

from system.models.operation import DesignRecord
from system.models.operation import (
    SOP,
    ContractReview,
    DesignProject,
    DesignRecord,
    SupplierEvaluation,
    ServiceReport,
    ProductRelease,
    NCRRegister
)

# --------------------
# Inline for Design Records
# --------------------
class DesignRecordInline(admin.StackedInline):
    model = DesignRecord
    extra = 1
    # autocomplete_fields = ["created_by"]


# --------------------
# Admins
# --------------------
@admin.register(SOP)
class SOPAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "created_by", "created_at", "is_active")
    list_filter = ("department", "is_active")
    search_fields = ("title", "description")
    date_hierarchy = "created_at"
    # autocomplete_fields = ["created_by"]


@admin.register(ContractReview)
class ContractReviewAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "contract_number", "department", "reviewed_by", "review_date")
    list_filter = ("department",)
    search_fields = ("customer_name", "contract_number", "findings")
    date_hierarchy = "review_date"
    # autocomplete_fields = ["reviewed_by"]


@admin.register(DesignProject)
class DesignProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "owner", "start_date", "planned_end_date", "status")
    list_filter = ("department", "status")
    search_fields = ("title", "notes")
    date_hierarchy = "start_date"
    inlines = [DesignRecordInline]
    # autocomplete_fields = ["owner"]


@admin.register(DesignRecord)
class DesignRecordAdmin(admin.ModelAdmin):
    list_display = ("project", "record_type", "created_by", "created_at")
    list_filter = ("record_type",)
    search_fields = ("description",)
    date_hierarchy = "created_at"
    # autocomplete_fields = ["project", "created_by"]


@admin.register(SupplierEvaluation)
class SupplierEvaluationAdmin(admin.ModelAdmin):
    list_display = ("name", "supplier_type", "evaluation_date", "evaluator")
    list_filter = ("supplier_type",)
    search_fields = ("name", "contact_person", "evaluation_result")
    date_hierarchy = "evaluation_date"
    # autocomplete_fields = ["evaluator"]


@admin.register(ServiceReport)
class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ("title", "service_provider", "service_date", "compliance_with_requirements")
    list_filter = ("compliance_with_requirements",)
    search_fields = ("title", "description")
    date_hierarchy = "service_date"
    # autocomplete_fields = ["service_provider"]


@admin.register(ProductRelease)
class ProductReleaseAdmin(admin.ModelAdmin):
    list_display = ("product_name", "release_date", "approved_by", "status")
    list_filter = ("status",)
    search_fields = ("product_name", "description")
    date_hierarchy = "release_date"
    # autocomplete_fields = ["approved_by"]


@admin.register(NCRRegister)
class NCRRegisterAdmin(admin.ModelAdmin):
    list_display = ("title", "reported_by", "department", "detected_date", "status")
    list_filter = ("department", "status")
    search_fields = ("title", "description", "corrective_action_taken")
    date_hierarchy = "detected_date"
    # autocomplete_fields = ["reported_by"]
