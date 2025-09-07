import uuid
import re
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager, Group, Permission
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from apps.common.models import TimestampedModel


def validate_login_id(value):
    """
    Validate loginId format: only alphanumeric characters, @, _, and - are allowed
    """
    if not re.match(r'^[a-zA-Z0-9@_-]+$', value):
        raise ValidationError(
            'LoginId can only contain letters, numbers, @, _, and - characters.'
        )


class CustomUserManager(DjangoUserManager):
    """
    Custom user manager to handle user_type and initial role assignment.
    """
    def _create_user(self, login_id, email, password, user_type, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        if not login_id:
            raise ValueError('The given login_id must be set')
        email = self.normalize_email(email)
        user = self.model(login_id=login_id, email=email, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, login_id, email, password=None, user_type='field_staff', **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(login_id, email, password, user_type, **extra_fields)

    def create_superuser(self, login_id, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'super_admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        # Extract user_type from extra_fields to avoid duplicate parameter
        user_type = extra_fields.pop('user_type', 'super_admin')
        return self._create_user(login_id, email, password, user_type, **extra_fields)


class Department(TimestampedModel):
    """Department model for organizational structure."""

    status_choices = [
        (True, 'Active'),
        (False, 'Inactive'),
    ]
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    status = models.BooleanField(choices=status_choices, default=True)    

    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
    
    def __str__(self):
        return self.name
    

class Designation(TimestampedModel):
    """Designation model for job titles."""
    
    status_choices = [
        (True, 'Active'),
        (False, 'Inactive'),
    ]
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    status = models.BooleanField(choices=status_choices, default=True)    

    class Meta:
        db_table = 'designations'
        verbose_name = 'Designation'
        verbose_name_plural = 'Designations'
    
    def __str__(self):
        return self.name
    

class User(AbstractUser, TimestampedModel):
    """Custom user model for KTL billing system."""
    
    USER_TYPES = [
        ('super_admin', 'Super Administrator'),
        ('admin', 'Administrator'),
        ('billing_manager', 'Billing Manager'),
        ('noc_manager', 'NOC Manager'),
        ('support_staff', 'Support Staff'),
        ('reseller_admin', 'Reseller Administrator'),
        ('sub_reseller_admin', 'Sub-Reseller Administrator'),
        ('field_staff', 'Field Staff'),
    ]
    
    # Authentication fields
    login_id = models.CharField(
        max_length=150, 
        unique=True, 
        validators=[validate_login_id],
        help_text='Login ID can contain letters, numbers, @, _, and - characters only'
    )
    email = models.EmailField(unique=True)
    mobile = PhoneNumberField()
    user_type = models.CharField(max_length=50, choices=USER_TYPES)
    
    # Personal Information
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=150)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, blank=True, null=True)
    designation = models.ForeignKey('Designation', on_delete=models.SET_NULL, blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    # date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_person_name = models.CharField(max_length=150, blank=True, null=True)
    contact_person_phone = PhoneNumberField(blank=True, null=True)
    district = models.ForeignKey('common.District', on_delete=models.SET_NULL, blank=True, null=True)
    thana = models.ForeignKey('common.Thana', on_delete=models.SET_NULL, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    remarks = models.TextField(blank=True, null=True)


    # Account Status
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=True)
    
    # Security
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    
    # Token Management for Lifetime Login
    access_token = models.TextField(blank=True, null=True, help_text="Current access token")
    refresh_token = models.TextField(blank=True, null=True, help_text="Current refresh token")
    token_created_at = models.DateTimeField(blank=True, null=True, help_text="Token creation time")
    token_expires_at = models.DateTimeField(blank=True, null=True, help_text="Token expiration time")
    remember_me = models.BooleanField(default=False, help_text="Remember me for lifetime login")
    
    # Profile
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    
    # User Preferences
    language_preference = models.CharField(
        max_length=10, 
        choices=[
            ('en', 'English'),
            ('bn', 'Bengali'),
        ],
        default='en',
        help_text='User preferred language'
    )
    timezone = models.CharField(
        max_length=50,
        default='Asia/Dhaka',
        help_text='User timezone preference'
    )
    
    USERNAME_FIELD = 'login_id'
    REQUIRED_FIELDS = ['email', 'user_type']

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.name or self.get_full_name()} ({self.login_id})"
    
    @property
    def full_name(self):
        return self.name 
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return self.user_roles.filter(role__name=role_name, is_active=True).exists()
    
    def get_all_permissions(self):
        """Get all permissions from assigned roles and Django groups"""
        permissions = set()
        
        # Get permissions from roles
        for user_role in self.user_roles.filter(is_active=True):
            permissions.update(user_role.role.get_all_permissions())
        
        # Get permissions from Django groups
        for group in self.groups.all():
            permissions.update(group.permissions.values_list('codename', flat=True))
        
        # Get direct user permissions
        permissions.update(self.user_permissions.values_list('codename', flat=True))
        
        return list(permissions)
    
    def assign_role(self, role, assigned_by, **kwargs):
        """Assign a role to the user"""
        user_role, created = UserRole.objects.get_or_create(
            user=self,
            role=role,
            defaults={
                'assigned_by': assigned_by,
                **kwargs
            }
        )
        return user_role, created
    
    def revoke_role(self, role, revoked_by, reason=""):
        """Revoke a role from the user"""
        user_roles = self.user_roles.filter(role=role, is_active=True)
        for user_role in user_roles:
            user_role.is_active = False
            user_role.revoked_by = revoked_by
            user_role.revoked_at = timezone.now()
            user_role.revocation_reason = reason
            user_role.save()
        return user_roles.count()
    
    def set_tokens(self, access_token, refresh_token, expires_at=None, remember_me=False):
        """Set access and refresh tokens for the user"""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_created_at = timezone.now()
        self.token_expires_at = expires_at
        self.remember_me = remember_me
        self.save(update_fields=['access_token', 'refresh_token', 'token_created_at', 'token_expires_at', 'remember_me'])
    
    def clear_tokens(self):
        """Clear user tokens"""
        self.access_token = None
        self.refresh_token = None
        self.token_created_at = None
        self.token_expires_at = None
        self.remember_me = False
        self.save(update_fields=['access_token', 'refresh_token', 'token_created_at', 'token_expires_at', 'remember_me'])
    
    def is_token_valid(self):
        """Check if current token is valid"""
        if not self.access_token or not self.token_expires_at:
            return False
        return timezone.now() < self.token_expires_at


class Role(TimestampedModel):
    """User roles integrated with Django's Group and Permission system."""
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    
    # Integration with Django's Group system
    django_group = models.OneToOneField(
        Group, 
        on_delete=models.CASCADE, 
        related_name='custom_role',
        null=True, 
        blank=True
    )
    
    # Additional role metadata
    is_system_role = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    max_assignments = models.PositiveIntegerField(blank=True, null=True)
    role_level = models.PositiveIntegerField(default=1)  # 1=Super Admin, 2=Admin, etc.
    can_assign_roles = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.display_name
    
    def save(self, *args, **kwargs):
        """Auto-create Django Group when Role is created"""
        if not self.django_group:
            group, created = Group.objects.get_or_create(name=self.name)
            self.django_group = group
        super().save(*args, **kwargs)
    
    def get_all_permissions(self):
        """Get all permissions assigned to this role"""
        if self.django_group:
            return list(self.django_group.permissions.values_list('codename', flat=True))
        return []
    
    def add_permission(self, permission):
        """Add a permission to this role"""
        if self.django_group and isinstance(permission, Permission):
            self.django_group.permissions.add(permission)
    
    def remove_permission(self, permission):
        """Remove a permission from this role"""
        if self.django_group and isinstance(permission, Permission):
            self.django_group.permissions.remove(permission)
    
    def set_permissions(self, permissions):
        """Set all permissions for this role"""
        if self.django_group:
            self.django_group.permissions.set(permissions)


class UserRole(TimestampedModel):
    """User role assignments with scope and integration with Django Groups."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_assignments')
    
    # Scope limitations (optional) - commented out as organizations models may not exist yet
    # sdt_zone = models.ForeignKey('organizations.SDTZone', on_delete=models.CASCADE, blank=True, null=True)
    # sdt = models.ForeignKey('organizations.SDT', on_delete=models.CASCADE, blank=True, null=True)
    
    # Assignment details
    assigned_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='role_assignments_made')
    assigned_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    assignment_reason = models.TextField(blank=True)
    revocation_reason = models.TextField(blank=True)
    revoked_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='role_revocations_made')
    revoked_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'user_roles'
        unique_together = ['user', 'role']  # Simplified for now
        verbose_name = 'User Role Assignment'
        verbose_name_plural = 'User Role Assignments'
    
    def __str__(self):
        return f"{self.user.full_name} - {self.role.display_name}"
    
    def save(self, *args, **kwargs):
        """Auto-assign user to Django Group when role is assigned"""
        super().save(*args, **kwargs)
        if self.is_active and self.role.django_group:
            self.user.groups.add(self.role.django_group)
        elif not self.is_active and self.role.django_group:
            self.user.groups.remove(self.role.django_group)
    
    def delete(self, *args, **kwargs):
        """Remove user from Django Group when role assignment is deleted"""
        if self.role.django_group:
            self.user.groups.remove(self.role.django_group)
        super().delete(*args, **kwargs)


class PermissionCategory(TimestampedModel):
    """Categories for organizing permissions"""
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For UI icons
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'permission_categories'
        verbose_name = 'Permission Category'
        verbose_name_plural = 'Permission Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.display_name


class CustomPermission(TimestampedModel):
    """Custom permissions beyond Django's default model permissions"""
    
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        PermissionCategory, 
        on_delete=models.CASCADE, 
        related_name='custom_permissions',
        null=True, 
        blank=True
    )
    
    # Integration with Django Permission
    django_permission = models.OneToOneField(
        Permission,
        on_delete=models.CASCADE,
        related_name='custom_permission',
        null=True,
        blank=True
    )
    
    is_system_permission = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'custom_permissions'
        verbose_name = 'Custom Permission'
        verbose_name_plural = 'Custom Permissions'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-create Django Permission when CustomPermission is created"""
        if not self.django_permission:
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get_for_model(User)
            permission, created = Permission.objects.get_or_create(
                codename=self.codename,
                defaults={
                    'name': self.name,
                    'content_type': content_type,
                }
            )
            self.django_permission = permission
        super().save(*args, **kwargs)


