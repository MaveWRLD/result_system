from django.contrib import admin
from .models import AuditedItem

@admin.register(AuditedItem)
class AuditedItemAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'content_object_link', 'action_time')
    list_filter = ('action', 'user', 'content_type')
    search_fields = ('user__username',)
    readonly_fields = ('action', 'user', 'content_object', 'old_value', 'new_value', 'action_time')

    def content_object_link(self, obj):
        if obj.content_object:
            try:
                # Attempt to link to the admin view for the content object
                url = f"/admin/{obj.content_type.app_label}/{obj.content_type.model}/{obj.object_id}/change/"
                return f"<a href='{url}'>{obj.content_object}</a>"
            except Exception:
                return str(obj.content_object)
        return "N/A"
    content_object_link.allow_tags = True
    content_object_link.short_description = 'Audited Object'

# Register your models here.
