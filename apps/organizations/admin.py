from django.contrib import admin
from .models import Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_code', 'business_license', 'vat_registration', 'contact_email', 'contact_phone', 'website', 'logo_img', 'created_at', 'updated_at')
    search_fields = ('company_name', 'company_code')
    ordering = ('-created_at',)
