from django.contrib import admin
from .models import Admin, Instructor, Visitor, AdminNote, RequestCert
from django.template.response import TemplateResponse
from django.urls import path
from .models import LabVIEWPanel
from .models import VisitorSlot


# Register your models here.
admin.site.register(Admin)
admin.site.register(Instructor)
admin.site.register(Visitor)
admin.site.register(AdminNote)
@admin.register(LabVIEWPanel)
class LabVIEWPanelAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('panel/', self.admin_site.admin_view(self.panel_view), name='labview-panel'),
        ]
        return custom_urls + urls

    def panel_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
            title='RTPSimulator Panel',
        )
        return TemplateResponse(request, "admin/homepage.html", context)

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

class LabVIEWPanelAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('panel/', self.admin_site.admin_view(self.panel_view), name='labview-panel'),
        ]
        return custom_urls + urls

    def panel_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
            title='RTPSimulator Panel',
        )
        return TemplateResponse(request, "admin/test.html", context)

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(RequestCert)
class RequestCertAdmin(admin.ModelAdmin):
    list_display = ('instructor', 'student_name', 'university_name', 'date_completed', 'status')
    list_filter = ('status', 'instructor')
    search_fields = ('student_name', 'university_name', 'instructor__name')
    ordering = ('-date_completed',)

@admin.register(VisitorSlot)
class VisitorSlotAdmin(admin.ModelAdmin):
    list_display = ('slot_number', 'session_key', 'last_active')
    search_fields = ('session_key',)
    ordering = ('slot_number',)
