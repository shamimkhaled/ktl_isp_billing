from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, Role, UserRole, PermissionCategory, CustomPermission
from apps.common.models import District, Thana
from apps.common.serializers import DistrictSerializer, ThanaSerializer


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Django Permission model"""
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Django Group model"""
    
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'permission_ids']
    
    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        instance = super().update(instance, validated_data)
        
        if permission_ids is not None:
            permissions = Permission.objects.filter(id__in=permission_ids)
            instance.permissions.set(permissions)
        
        return instance


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model"""
    
    permissions = PermissionSerializer(source='django_group.permissions', many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of permission IDs to assign to this role"
    )
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'display_name', 'description', 'role_level',
            'is_active', 'is_system_role', 'can_assign_roles', 'max_assignments',
            'permissions', 'permission_ids', 'users_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_users_count(self, obj):
        """Get count of active users with this role"""
        return obj.user_assignments.filter(is_active=True).count()
    
    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = super().create(validated_data)
        
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.set_permissions(permissions)
        
        return role
    
    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        instance = super().update(instance, validated_data)
        
        if permission_ids is not None:
            permissions = Permission.objects.filter(id__in=permission_ids)
            instance.set_permissions(permissions)
        
        return instance


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserRole model"""
    
    role_name = serializers.CharField(source='role.display_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.full_name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'role', 'role_name', 'is_active', 'assigned_by', 'assigned_by_name',
            'assigned_at', 'expires_at', 'assignment_reason', 'created_at'
        ]
        read_only_fields = ['assigned_at', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    roles = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of role IDs to assign to the user"
    )
    
    class Meta:
        model = User
        fields = [
            'login_id', 'email', 'password', 'password_confirm', 
            'mobile', 'user_type', 'employee_id', 'name', 'designation', 'department', 
            'salary', 'date_of_joining', 'address', 'contact_person_name', 'contact_person_phone',
            'district', 'thana', 'postal_code', 'remarks', 'roles'
        ]
    
    def validate_login_id(self, value):
        """Validate login_id format and uniqueness"""
        if User.objects.filter(login_id=value).exists():
            raise serializers.ValidationError("A user with this login ID already exists.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password and password confirmation do not match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        roles = validated_data.pop('roles', [])
        password = validated_data.pop('password')
        
        user = User.objects.create_user(password=password, **validated_data)
        
        # Assign roles
        if roles:
            role_objects = Role.objects.filter(id__in=roles, is_active=True)
            for role in role_objects:
                user.assign_role(role, assigned_by=self.context['request'].user)
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (read/update)"""
    
    full_name = serializers.ReadOnlyField()
    roles = UserRoleSerializer(source='user_roles', many=True, read_only=True)
    permissions = serializers.SerializerMethodField()
    district_info = DistrictSerializer(source='district', read_only=True)
    thana_info = ThanaSerializer(source='thana', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'login_id', 'email', 'first_name', 'last_name', 'full_name', 'name',
            'mobile', 'user_type', 'employee_id', 'designation', 'department',
            'salary', 'date_of_joining', 'address', 'contact_person_name', 'contact_person_phone',
            'district', 'district_info', 'thana', 'thana_info', 'postal_code', 'remarks',
            'is_active', 'is_staff', 'is_email_verified', 'is_phone_verified',
            'profile_photo', 'language_preference', 'timezone', 'roles', 'permissions',
            'last_login', 'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'login_id', 'last_login', 'date_joined', 'created_at', 'updated_at'
        ]
    
    def get_permissions(self, obj):
        """Get all user permissions"""
        return obj.get_all_permissions()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'name', 'mobile', 'employee_id', 'designation',
            'department', 'salary', 'date_of_joining', 'address', 'contact_person_name', 
            'contact_person_phone', 'district', 'thana', 'postal_code', 'remarks',
            'profile_photo', 'language_preference', 'timezone'
        ]
    
    def validate(self, attrs):
        """Validate thana belongs to selected district"""
        district = attrs.get('district')
        thana = attrs.get('thana')
        
        if thana and district and thana.district != district:
            raise serializers.ValidationError({
                'thana': 'Selected thana does not belong to the selected district.'
            })
        
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing user password"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New password and confirmation do not match.")
        return attrs
    
    def save(self):
        """Change user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class RoleAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning/revoking roles"""
    
    user_id = serializers.UUIDField()
    role_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=['assign', 'revoke'])
    reason = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate_user_id(self, value):
        """Validate user exists"""
        try:
            return User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
    
    def validate_role_id(self, value):
        """Validate role exists and is active"""
        try:
            role = Role.objects.get(id=value)
            if not role.is_active:
                raise serializers.ValidationError("Role is not active.")
            return role
        except Role.DoesNotExist:
            raise serializers.ValidationError("Role not found.")
    
    def save(self):
        """Perform role assignment/revocation"""
        user = self.validated_data['user_id']
        role = self.validated_data['role_id']
        action = self.validated_data['action']
        reason = self.validated_data.get('reason', '')
        expires_at = self.validated_data.get('expires_at')
        assigned_by = self.context['request'].user
        
        if action == 'assign':
            user_role, created = user.assign_role(
                role=role,
                assigned_by=assigned_by,
                assignment_reason=reason,
                expires_at=expires_at
            )
            return {'action': 'assigned', 'created': created, 'user_role': user_role}
        
        elif action == 'revoke':
            count = user.revoke_role(role=role, revoked_by=assigned_by, reason=reason)
            return {'action': 'revoked', 'count': count}


class PermissionCategorySerializer(serializers.ModelSerializer):
    """Serializer for Permission Category"""
    
    permissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PermissionCategory
        fields = [
            'id', 'name', 'display_name', 'description', 'icon', 'order',
            'permissions_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_permissions_count(self, obj):
        """Get count of custom permissions in this category"""
        return obj.custom_permissions.filter(is_active=True).count()


class CustomPermissionSerializer(serializers.ModelSerializer):
    """Serializer for Custom Permission"""
    
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    
    class Meta:
        model = CustomPermission
        fields = [
            'id', 'codename', 'name', 'description', 'category', 'category_name',
            'is_active', 'is_system_permission', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_codename(self, value):
        """Validate codename uniqueness"""
        if CustomPermission.objects.filter(codename=value).exists():
            raise serializers.ValidationError("A permission with this codename already exists.")
        return value
