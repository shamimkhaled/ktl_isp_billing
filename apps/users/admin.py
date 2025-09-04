from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User, Role, UserRole, PermissionCategory, CustomPermission


class UserRoleInline(admin.TabularInline):
    """Inline for managing user roles in User admin"""
    model = UserRole
    fk_name = 'user'  # Specify which ForeignKey to use
    extra = 0
    fields = ('role', 'is_active', 'assigned_by', 'assigned_at', 'expires_at', 'assignment_reason')
    readonly_fields = ('assigned_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('role', 'assigned_by')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin with role management"""
    
    list_display = ('login_id', 'email', 'name', 'user_type', 'is_active', 'is_staff', 'get_roles')
    list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser', 'user_roles__role')
    search_fields = ('login_id', 'email', 'name', 'employee_id')
    ordering = ('login_id',)
    
    fieldsets = (
        (None, {'fields': ('login_id', 'password')}),
        ('Personal info', {
            'fields': ('name', 'email', 'mobile', 'employee_id', 'designation', 'department')
        }),
        ('Account Type', {
            'fields': ('user_type',)
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
    
    inlines = [UserRoleInline]
    
    def get_roles(self, obj):
        """Display user roles in list view"""
        roles = obj.user_roles.filter(is_active=True).select_related('role')
        if roles:
            role_list = [f'<span class="badge badge-primary">{ur.role.display_name}</span>' for ur in roles]
            return mark_safe(' '.join(role_list))
        return '-'
    get_roles.short_description = 'Active Roles'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('user_roles__role')


class UserRoleInlineForRole(admin.TabularInline):
    """Inline for managing user assignments in Role admin"""
    model = UserRole
    fk_name = 'role'  # Specify which ForeignKey to use
    extra = 0
    fields = ('user', 'is_active', 'assigned_by', 'assigned_at', 'expires_at')
    readonly_fields = ('assigned_at',)


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
            'fields': ('role_level', 'is_active', 'is_system_role', 'can_assign_roles', 'max_assignments')
        }),
        ('Django Integration', {
            'fields': ('django_group', 'get_group_permissions'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('django_group', 'get_group_permissions')
    inlines = [UserRoleInlineForRole]
    
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
        count = obj.user_assignments.filter(is_active=True).count()
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


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """User Role Assignment Admin"""
    
    list_display = ('user', 'role', 'is_active', 'assigned_by', 'assigned_at', 'expires_at')
    list_filter = ('is_active', 'role', 'assigned_at', 'expires_at')
    search_fields = ('user__login_id', 'user__email', 'user__first_name', 'user__last_name', 'role__name')
    date_hierarchy = 'assigned_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'role', 'is_active')
        }),
        ('Assignment Details', {
            'fields': ('assigned_by', 'assigned_at', 'expires_at', 'assignment_reason')
        }),
        ('Revocation Details', {
            'fields': ('revoked_by', 'revoked_at', 'revocation_reason'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('assigned_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'role', 'assigned_by', 'revoked_by')


@admin.register(PermissionCategory)
class PermissionCategoryAdmin(admin.ModelAdmin):
    """Permission Category Admin"""
    
    list_display = ('display_name', 'name', 'order', 'get_permissions_count')
    list_editable = ('order',)
    search_fields = ('name', 'display_name', 'description')
    ordering = ('order', 'name')
    
    def get_permissions_count(self, obj):
        """Display custom permissions count"""
        count = obj.custom_permissions.count()
        return f'{count} permissions'
    get_permissions_count.short_description = 'Custom Permissions'


@admin.register(CustomPermission)
class CustomPermissionAdmin(admin.ModelAdmin):
    """Custom Permission Admin"""
    
    list_display = ('name', 'codename', 'category', 'is_active', 'is_system_permission', 'get_django_permission')
    list_filter = ('is_active', 'is_system_permission', 'category')
    search_fields = ('name', 'codename', 'description')
    
    fieldsets = (
        (None, {
            'fields': ('codename', 'name', 'description', 'category')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_system_permission')
        }),
        ('Django Integration', {
            'fields': ('django_permission',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('django_permission',)
    
    def get_django_permission(self, obj):
        """Display Django permission link"""
        if obj.django_permission:
            url = reverse('admin:auth_permission_change', args=[obj.django_permission.id])
            return format_html('<a href="{}">View Django Permission</a>', url)
        return 'Not created'
    get_django_permission.short_description = 'Django Permission'


# Customize Django's Group admin to show related Role
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


# Unregister the default Group admin and register our custom one
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


# Admin site customization
admin.site.site_header = 'KTL ISP Billing Administration'
admin.site.site_title = 'KTL Super Admin'
admin.site.index_title = 'Welcome to KTL ISP Billing Administration'
