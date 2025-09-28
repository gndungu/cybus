from django.db import models
from django.contrib.auth.models import User


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        editable=False
    )

    class Meta:
        abstract = True
