from django.contrib import admin
from .models import District, Thana


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_bn', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'name_bn', 'code']
    ordering = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Thana)
class ThanaAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_bn', 'district', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'district', 'created_at']
    search_fields = ['name', 'name_bn', 'code', 'district__name']
    ordering = ['district__name', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('district')
