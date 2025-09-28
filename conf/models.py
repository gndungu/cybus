from django.db import models
from system.models.modelmixin import TimeStampMixin


class Region(TimeStampMixin):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class District(TimeStampMixin):
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Sector(TimeStampMixin):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Department(TimeStampMixin):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class EvaluationLevel(TimeStampMixin):
    name = models.CharField(max_length=255, unique=True)
    days = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Standards(TimeStampMixin):
    class Meta:
        verbose_name_plural = "Standards"
        db_table = "standards"

    standard_no = models.CharField(max_length=255, unique=True)
    edition = models.PositiveIntegerField(null=True, blank=True)
    standard_title = models.CharField(max_length=255, verbose_name="Standard Title", null=True, blank=True)
    year = models.IntegerField(verbose_name="Year of Publication", null=True, blank=True)
    scope = models.TextField(null=True, blank=True)
    ics_no = models.CharField(max_length=255, verbose_name="ICS No.", null=True, blank=True)
    hsc_code = models.TextField(verbose_name="HSC Code",null=True, blank=True)
    pages = models.IntegerField(verbose_name="Pages", null=True, blank=True)

    def __str__(self):
        return f"{self.standard_no} {self.standard_title}"


class Activity(TimeStampMixin):
    class Meta:
        verbose_name_plural = "Activity"

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.name}"


class Category(TimeStampMixin):
    class Meta:
        verbose_name_plural = "Category"

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.name}"


class StandardOperatingProcedure(TimeStampMixin):
    class Meta:
        verbose_name_plural = "SOP"

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True, null=True)
    sop_file = models.FileField(upload_to="sop", null=True, blank=True)

    def __str__(self):
        return F"{self.name}"


class Forms(TimeStampMixin):
    class Meta:
        verbose_name_plural = "Form"

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True, null=True)

    def __str__(self):
        return F"{self.name}"

