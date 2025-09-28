from django.contrib import admin
from django.conf import settings
from django.utils.html import format_html

class BaseModelAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    actions_on_top = False

    def image_tag(self, obj, field_name):
        if hasattr(obj, field_name):
            image_field = getattr(obj, field_name)
            if image_field:
                return format_html('<img src="{}" style="max-width:80px;max-height:80px"/>'.format(image_field.url))
        return ""

    def created_date(self, obj):
        return obj.creation_date.strftime("%Y-%m-%d %H:%M:%S")

    created_date.short_description = "Created At"

    def updated_date(self, obj):
        return obj.creation_date.strftime("%Y-%m-%d %H:%M:%S")

    updated_date.short_description = "Updated At"

    def has_change_permission(self, request, obj=None):
        if 'view_form' in request.GET:
            return False
        return super().has_change_permission(request, obj)

    def get_list_display(self, request):
        model = self.model
        list_display = [field.name for field in model._meta.fields if field.name not in ['id', 'created_at', 'description', 'updated_at', 'created_by']]
        for field_name in settings.IMAGE_FIELDS:
            if field_name in [field.name for field in model._meta.fields]:
                def image_field(obj, field_name=field_name):
                    return self.image_tag(obj, field_name)

                image_field.short_description = field_name.capitalize()
                list_display.append(image_field)
        return list_display + ['created_at', 'updated_at', 'created_by']

    def get_search_fields(self, request):
        model = self.model
        excluded_field_names = ['id', 'updated_date']
        # search_fields = [field.name for field in model._meta.fields]
        search_fields=[]
        for field in model._meta.fields:
            if (
                    not field.is_relation
                    and field.name not in excluded_field_names
                    and field.related_model is None
            ):
                search_fields.append(field.name)

        return search_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)

        # Update empty label for the foreign key field
        formfield.empty_label = 'Choose'

        return formfield

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter the queryset to show only results for the current user
            try:
                queryset = queryset.filter(user=request.user)
            except Exception as e:
                pass

        return queryset

    def save_model(self, request, obj, form, change):
        if not change and hasattr(obj, 'created_by') and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.created_by:
                instance.created_by = request.user
            instance.save()
        formset.save_m2m()

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change=False, **kwargs)

        # Loop through the fields and set 'required' based on the model
        for field_name, field in form.base_fields.items():
            if form._meta.model._meta.get_field(field_name).null is False:
                field.required = True

        return form

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)

        # Loop through the inlines and set required fields where necessary
        for inline in inline_instances:
            formset = inline.get_formset(request, obj)
            for field_name, field in formset.form.base_fields.items():
                if formset.form._meta.model._meta.get_field(field_name).null is False:
                    field.required = True

        return inline_instances



class BaseTabularInLine(admin.TabularInline):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)

        # Set the empty label for foreign key fields to "Choose"
        formfield.empty_label = 'Choose'

        return formfield

class BaseStackedInLine(admin.StackedInline):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)

        # Set the empty label for foreign key fields to "Choose"
        formfield.empty_label = 'Choose'

        return formfield

def register_all_models(app, exclude=[]):
    for model in app.get_models():
        try:
            admin_class_name = f'{model.__name__}Admin'
            if admin_class_name in exclude:
                continue
            admin_class = type(admin_class_name, (BaseModelAdmin,), {'model': model})
            admin.site.register(model, admin_class)
        except admin.sites.AlreadyRegistered:
            pass