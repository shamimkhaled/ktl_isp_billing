import uuid
import re
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.common.models import TimestampedModel
from phonenumber_field.modelfields import PhoneNumberField


def validate_login_id(value):
    """
    Validate loginId format: only alphanumeric characters, @, _, and - are allowed
    """
    if not re.match(r'^[a-zA-Z0-9@_-]+$', value):
        raise ValidationError(
            'LoginId can only contain letters, numbers, @, _, and - characters.'
        )



class Role(TimestampedModel):
    """
    Role Model - Integrated with Django Groups
    CRITICAL: Users MUST have a role before creation
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Internal role name (lowercase_with_underscores)'
    )
    display_name = models.CharField(
        max_length=150,
        help_text='Human-readable role name'
    )
    description = models.TextField(blank=True)
    
    # Django Group Integration (AUTO-CREATED)
    django_group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='ktl_role',
        null=True,
        blank=True,
        help_text='Auto-linked Django Group for permissions'
    )
    
    # Organization
    organization_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text='Organization this role belongs to'
    )
    
    # Role properties
    role_level = models.PositiveIntegerField(
        default=100,
        help_text='Hierarchy level (lower = more powerful). super_admin=1, admin=10, user=100'
    )
    is_system_role = models.BooleanField(
        default=False,
        help_text='System-managed role (cannot be deleted)'
    )
    is_active = models.BooleanField(default=True)
    
    # Role Capabilities
    can_assign_roles = models.BooleanField(
        default=False,
        help_text='Can this role assign roles to other users'
    )
    max_users = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum users allowed with this role (null = unlimited)'
    )
    
    # Dashboard Access
    default_dashboard = models.CharField(
        max_length=50,
        default='dashboard',
        help_text='Default landing page after login'
    )
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        unique_together = ['organization_id', 'name']
        ordering = ['role_level', 'display_name']
        indexes = [
            models.Index(fields=['organization_id', 'is_active']),
            models.Index(fields=['role_level']),
        ]
    
    def __str__(self):
        return f"{self.display_name} (Level {self.role_level})"
    

    def save(self, *args, **kwargs):
        """ Auto create Django Group on save"""
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if not self.django_group:
           group_name = f"{self.organization_id}_{self.name}"
           group, created = Group.objects.get_or_create(name=group_name)
           self.django_group = group
           super().save(update_fields=['django_group'])


    def get_permissions(self):
        """Get all permissions associated with this role"""
        if self.django_group:
            return list(self.django_group.permissions.values_list('codename', flat=True))
        
        return []
    
    def assign_permission(self, permission_codenames):
        """Assign Django permissions link to this role"""
        from django.contrib.auth.models import Permission
        if self.django_group:
            permissions = Permission.objects.filter(codename__in=permission_codenames)
            self.django_group.permissions.add(*permissions)





class CustomUserManager(BaseUserManager):
    """Custom manager for User model"""
    
    def create_user(self, login_id, email, password=None, **extra_fields):
        """
        Create regular user
        REQUIRES: role parameter
        """
        if not login_id:
            raise ValueError('User must have a login_id')
        if not email:
            raise ValueError('User must have an email')
        
        # Validate role is provided
        role = extra_fields.get('role')
        if not role:
            raise ValueError('User must be assigned a role before creation')
        
        email = self.normalize_email(email)
        user = self.model(
            login_id=login_id,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        
        # Add user to role's Django group
        if role and role.django_group:
            user.groups.add(role.django_group)
        
        return user
    
    def create_superuser(self, login_id, email, password=None, **extra_fields):
        """
        Create superuser with super_admin role
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        # Find or create super_admin role
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM organizations LIMIT 1")
            row = cursor.fetchone()
            org_id = row[0] if row else uuid.uuid4()
        
        super_admin_role, created = Role.objects.get_or_create(
            name='super_admin',
            organization_id=org_id,
            defaults={
                'display_name': 'Super Administrator',
                'role_level': 1,
                'is_system_role': True,
                'can_assign_roles': True
            }
        )
        
        extra_fields['role'] = super_admin_role
        extra_fields['organization_id'] = org_id
        
        return self.create_user(login_id, email, password, **extra_fields)





class Department(TimestampedModel):
    """Department model for organizational structure."""

    status_choices = [
        (True, 'Active'),
        (False, 'Inactive'),
    ]
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, default='dept', unique=True, db_index=True)
    description = models.TextField(blank=True)
    status = models.BooleanField(choices=status_choices, default=True)    

    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='sub_departments'
    )
    head = models.ForeignKey(
        'User', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='headed_departments'
    )
    is_active = models.BooleanField(default=True, db_index=True)
    order = models.PositiveIntegerField(default=0)
    
    # Organization relationship (if multi-tenant)
    organization = models.ForeignKey(
        'organizations.Organizations',
        on_delete=models.CASCADE,
        related_name='departments',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['code', 'organization']),
        ]
        unique_together = ['code', 'organization']


    @property
    def full_name(self):
        """Get full department path"""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def get_all_users(self):
        """Get all users in this department and sub-departments"""
        department_ids = [self.id]
        department_ids.extend(self.get_all_sub_department_ids())
        return User.objects.filter(department_id__in=department_ids, is_active=True)
    
    def get_all_sub_department_ids(self):
        """Get all sub-department IDs recursively"""
        ids = []
        for sub_dept in self.sub_departments.filter(is_active=True):
            ids.append(sub_dept.id)
            ids.extend(sub_dept.get_all_sub_department_ids())
        return ids
    

class Designation(TimestampedModel):
    """Designation model for job titles with hierarchy."""
    
    DESIGNATION_LEVELS = [
        (1, 'Entry Level'),
        (2, 'Junior Level'),
        (3, 'Mid Level'),
        (4, 'Senior Level'),
        (5, 'Lead Level'),
        (6, 'Manager Level'),
        (7, 'Director Level'),
        (8, 'Executive Level')
    ]
    
    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=20, default='designation', db_index=True)
    description = models.TextField(blank=True)
    level = models.PositiveIntegerField(
        choices=DESIGNATION_LEVELS, 
        default=1,
        db_index=True
    )

    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='designations',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True, db_index=True)
    
    # Salary range
    # min_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # max_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Organization relationship
    organization = models.ForeignKey(
        'organizations.Organizations',
        on_delete=models.CASCADE,
        related_name='designations',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'designations'
        verbose_name = 'Designation'
        verbose_name_plural = 'Designations'
        ordering = ['level', 'name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['department', 'level']),
            models.Index(fields=['level', 'is_active']),
        ]
        unique_together = ['code', 'organization']
    
    def __str__(self):
        return self.name

    
    

class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    
    # Authentication fields
    login_id = models.CharField(
        max_length=150, 
        unique=True, 
        validators=[validate_login_id],
        help_text='Login ID can contain letters, numbers, @, _, and - characters only'
    )
    email = models.EmailField(unique=True)
    mobile = PhoneNumberField()
    

    # Personal Information
    employee_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    name = models.CharField(max_length=150, db_index=True)
    department = models.ForeignKey(
        'Department', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='users'
    )
    designation = models.ForeignKey(
        'Designation', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='users'
    )
    
    # Employment Details
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    contact_person_name = models.CharField(max_length=150, blank=True, null=True)
    contact_person_phone = PhoneNumberField(blank=True, null=True)
    
    # Address Information
    address = models.TextField(blank=True, null=True)
    district = models.ForeignKey(
        'common.District', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='users'
    )
    thana = models.ForeignKey(
        'common.Thana', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='users'
    )
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Additional Information
    remarks = models.TextField(blank=True, null=True)

    # ROLE (REQUIRED - No user without role)
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        null=True,
        blank=True,
        help_text='Primary role for this user (REQUIRED)'
    )
    


    # Account Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=True)
    
    # Security
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    password_changed_at = models.DateTimeField(blank=True, null=True)
    password_expires_at = models.DateTimeField(blank=True, null=True)
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


    organization = models.ForeignKey(
        'organizations.Organizations',
        on_delete=models.CASCADE,
        related_name='users',
        blank=True,
        null=True
    )
    
    USERNAME_FIELD = 'login_id'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['organization_id']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
        
    
  
    def __str__(self):
        return f"{self.name} ({self.login_id}) - {self.role.display_name}"
    
    def clean(self):
        """Validate user has role and belongs to same organization as role"""
        if not self.role:
            raise ValidationError("User must have a role assigned")

        if self.organization and self.role.organization_id != self.organization.id:
            raise ValidationError("User and role must belong to same organization")
    
    def save(self, *args, **kwargs):
        """Auto-add user to role's Django group"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Sync with Django groups
        if self.role and self.role.django_group:
            # Remove from all other groups first
            self.groups.clear()
            # Add to role's group
            self.groups.add(self.role.django_group)
    
    def has_role(self, role_name):
        """Check if user has specific role"""
        return self.role.name == role_name
    
    def has_permission_level(self, required_level):
        """Check if user's role level is sufficient"""
        return self.role.role_level <= required_level
    
    def is_super_admin(self):
        """Check if user is super admin"""
        return self.role.name == 'super_admin'
    
    def set_tokens(self, access_token, refresh_token, expires_at, remember_me=False):
        """Store JWT tokens"""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = expires_at
        self.remember_me = remember_me
        self.save(update_fields=['access_token', 'refresh_token', 'token_expires_at', 'remember_me'])
    
    def clear_tokens(self):
        """Clear stored tokens"""
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.save(update_fields=['access_token', 'refresh_token', 'token_expires_at'])

    def assign_role(self, role, assigned_by=None, assignment_reason='', expires_at=None):
        """Assign a role to the user by changing the role field"""
        previous_role = self.role
        self.role = role
        self.save()

        # Log history
        RoleAssignmentHistory.objects.create(
            user=self,
            previous_role=previous_role,
            new_role=role,
            changed_by=assigned_by,
            reason=assignment_reason
        )

        return self.role, True

    def revoke_role(self, role, revoked_by=None, reason=''):
        """Revoke a role from the user by clearing the role field"""
        if self.role == role:
            previous_role = self.role
            self.role = None
            self.save()

            # Log history
            RoleAssignmentHistory.objects.create(
                user=self,
                previous_role=previous_role,
                new_role=None,
                changed_by=revoked_by,
                reason=reason
            )
            return 1
        return 0

    def get_all_permissions(self):
        """Get all permissions for the user from the assigned role"""
        permissions = set()
        if self.role and self.role.django_group:
            permissions.update(self.role.django_group.permissions.values_list('codename', flat=True))
        return list(permissions)


class PermissionCategory(TimestampedModel):
    """
    Permission Category for organizing permissions
    """
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'permission_categories'
        verbose_name = 'Permission Category'
        verbose_name_plural = 'Permission Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.display_name


class CustomPermission(TimestampedModel):
    """
    Custom Permission model
    """
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_system_permission = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    django_permission = models.OneToOneField(
        'auth.Permission',
        on_delete=models.CASCADE,
        related_name='custom_permission',
        blank=True,
        null=True
    )
    category = models.ForeignKey(
        PermissionCategory,
        on_delete=models.CASCADE,
        related_name='custom_permissions',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'custom_permissions'
        verbose_name = 'Custom Permission'
        verbose_name_plural = 'Custom Permissions'

    def __str__(self):
        return self.name



class RoleAssignmentHistory(TimestampedModel):
    """
    Track role changes for audit purposes
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_history')
    previous_role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='previous_assignments')
    new_role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='new_assignments')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='role_changes_made')
    reason = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'role_assignment_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.login_id}: {self.previous_role} → {self.new_role}"


