from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User, Role, Department, Designation, RoleAssignmentHistory




admin.site.register([Department, Designation])



@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin with role management"""
    
    list_display = ('login_id', 'email', 'name', 'is_active', 'is_staff', 'is_superuser', 'get_roles')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'role')
    search_fields = ('login_id', 'email', 'name', 'employee_id')
    ordering = ('login_id',)
    
    fieldsets = (
        (None, {'fields': ('login_id', 'password')}),
        ('Personal info', {
            'fields': ('name', 'email', 'mobile', 'employee_id', 'designation', 'department')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Account Status', {
            'fields': ('is_email_verified', 'is_phone_verified', 'is_first_login'),
            'classes': ('collapse',)
        }),
        ('Security', {
            'fields': ('failed_login_attempts', 'locked_until', 'two_factor_enabled'),
            'classes': ('collapse',)
        }),
        ('Profile', {
            'fields': ('profile_photo', 'language_preference', 'timezone'),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login_id', 'email', 'user_type', 'password1', 'password2'),
        }),
        ('Personal info', {
            'fields': ('name', 'mobile'),
        }),
    )
    

    
    def get_roles(self, obj):
        """Display user role in list view"""
        if obj.role:
            return f'<span class="badge badge-primary">{obj.role.display_name}</span>'
        return '-'
    get_roles.short_description = 'Role'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('role')
    
    def has_add_permission(self, request):
        """Only super_admin and admin can add users"""
        if request.user.is_superuser:
            return True
        return request.user.user_type in ['super_admin', 'admin']
    
    def has_change_permission(self, request, obj=None):
        """Only super_admin and admin can change users"""
        if request.user.is_superuser:
            return True
        return request.user.user_type in ['super_admin', 'admin']
    
    def has_delete_permission(self, request, obj=None):
        """Only super_admin can delete users"""
        if request.user.is_superuser:
            return True
        return request.user.user_type == 'super_admin'
    
    def has_view_permission(self, request, obj=None):
        """Allow viewing for super_admin, admin, and billing_manager"""
        if request.user.is_superuser:
            return True
        return request.user.user_type in ['super_admin', 'admin', 'billing_manager']




@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Role Admin with Django Group integration"""
    
    list_display = ('display_name', 'name', 'role_level', 'is_active', 'is_system_role', 'get_permissions_count', 'get_users_count')
    list_filter = ('is_active', 'is_system_role', 'role_level', 'can_assign_roles')
    search_fields = ('name', 'display_name', 'description')
    ordering = ('role_level', 'display_name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'display_name', 'description')
        }),
        ('Role Settings', {
            'fields': ('role_level', 'is_active', 'is_system_role', 'can_assign_roles', 'max_users')
        }),
        ('Django Integration', {
            'fields': ('django_group', 'get_group_permissions'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('django_group', 'get_group_permissions')

    
    def get_permissions_count(self, obj):
        """Display permission count"""
        if obj.django_group:
            count = obj.django_group.permissions.count()
            url = reverse('admin:auth_group_change', args=[obj.django_group.id])
            return format_html('<a href="{}">{} permissions</a>', url, count)
        return '0 permissions'
    get_permissions_count.short_description = 'Permissions'
    
    def get_users_count(self, obj):
        """Display active users count"""
        count = User.objects.filter(role=obj, is_active=True).count()
        return f'{count} users'
    get_users_count.short_description = 'Active Users'
    
    def get_group_permissions(self, obj):
        """Display Django group permissions"""
        if obj.django_group:
            permissions = obj.django_group.permissions.all()[:10]  # Show first 10
            if permissions:
                perm_list = [f'<li>{p.name}</li>' for p in permissions]
                more = obj.django_group.permissions.count() - 10
                if more > 0:
                    perm_list.append(f'<li><em>... and {more} more</em></li>')
                return mark_safe(f'<ul>{"".join(perm_list)}</ul>')
        return 'No permissions assigned'
    get_group_permissions.short_description = 'Group Permissions'
    
    def save_model(self, request, obj, form, change):
        """Auto-create Django Group when saving Role"""
        super().save_model(request, obj, form, change)
        if not obj.django_group:
            group, created = Group.objects.get_or_create(name=obj.name)
            obj.django_group = group
            obj.save()
    
    def has_add_permission(self, request):
        """Only super_admin and admin can add roles"""
        if request.user.is_superuser:
            return True
        return request.user.user_type in ['super_admin', 'admin']
    
    def has_change_permission(self, request, obj=None):
        """Only super_admin and admin can change roles"""
        if request.user.is_superuser:
            return True
        return request.user.user_type in ['super_admin', 'admin']
    
    def has_delete_permission(self, request, obj=None):
        """Only super_admin can delete roles"""
        if request.user.is_superuser:
            return True
        return request.user.user_type == 'super_admin'
    
    def has_view_permission(self, request, obj=None):
        """Allow viewing for super_admin, admin, and billing_manager"""
        if request.user.is_superuser:
            return True
        return request.user.user_type in ['super_admin', 'admin', 'billing_manager']

#  Customize Django's Group admin to show related Role
class GroupAdmin(admin.ModelAdmin):
    """Enhanced Group Admin showing related Role"""
    
    list_display = ('name', 'get_custom_role', 'get_permissions_count', 'get_users_count')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)
    
    def get_custom_role(self, obj):
        """Display related custom role"""
        try:
            role = obj.custom_role
            url = reverse('admin:users_role_change', args=[role.id])
            return format_html('<a href="{}">{}</a>', url, role.display_name)
        except:
            return 'No custom role'
    get_custom_role.short_description = 'Custom Role'
    
    def get_permissions_count(self, obj):
        """Display permissions count"""
        return obj.permissions.count()
    get_permissions_count.short_description = 'Permissions'
    
    def get_users_count(self, obj):
        """Display users count"""
        return obj.user_set.count()
    get_users_count.short_description = 'Users'
    
    def has_add_permission(self, request):
        """Only super_admin and admin can add groups"""
        if request.user.is_superuser:
            return True
        return request.user.user_type in ['super_admin', 'admin']
    
    def has_change_permission(self, request, obj=None):
        """Only super_admin and admin can change groups"""
        if request.user.is_superuser:
            return True
        return request.user.user_type in ['super_admin', 'admin']
    
    def has_delete_permission(self, request, obj=None):
        """Only super_admin can delete groups"""
        if request.user.is_superuser:
            return True
        return request.user.user_type == 'super_admin'
    
    def has_view_permission(self, request, obj=None):
        """Allow viewing for super_admin, admin, and billing_manager"""
        if request.user.is_superuser:
            return True
        return request.user.user_type in ['super_admin', 'admin', 'billing_manager']


# Unregister the default Group admin and register our custom one
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


# Admin site customization
admin.site.site_header = 'KTL ISP Billing Administration'
admin.site.site_title = 'KTL Super Admin'
admin.site.index_title = 'Welcome to KTL ISP Billing Administration'
