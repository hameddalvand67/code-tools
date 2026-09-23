from django.contrib import admin

from .models import Action, Category, SiteSettings, Step


class StepInline(admin.TabularInline):
    model = Step
    extra = 1
    fk_name = "parent"
    fields = ("order", "kind", "title", "language", "body", "nested", "notes")
    autocomplete_fields = ("nested",)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("icon", "name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}


class StepUsedInline(admin.TabularInline):
    model = Step
    extra = 0
    fk_name = "nested"
    verbose_name = "استفاده در"
    verbose_name_plural = "استفاده در این فلوها"
    fields = ("parent", "title", "order")
    readonly_fields = ("parent", "title", "order")
    can_delete = False


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_flow", "is_library", "updated_at")
    list_filter = ("is_flow", "is_library", "category")
    search_fields = ("title", "summary", "tags")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [StepInline, StepUsedInline]


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ("display_title", "parent", "kind", "order")
    list_filter = ("kind", "language")
    search_fields = ("title", "body", "parent__title")
    autocomplete_fields = ("parent", "nested")
