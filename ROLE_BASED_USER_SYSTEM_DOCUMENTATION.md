# Role-Based User System Documentation

## Overview

This documentation covers the comprehensive role-based user system implemented for the KTL ISP Billing system. The system integrates Django's built-in Groups and Permissions with a custom role management system.

## Features

- ✅ **LoginId Authentication**: Users login with custom loginId (alphanumeric + @, _, -)
- ✅ **Role-Based Access Control**: Integrated with Django's Groups and Permissions
- ✅ **Django Admin Integration**: Easy permission management through admin interface
- ✅ **RESTful API**: Complete CRUD operations for users, roles, and permissions
- ✅ **Validation**: LoginId uniqueness and format validation
- ✅ **Superadmin Control**: Superadmin can assign specific permissions to any role
- ✅ **Audit Trail**: Track role assignments and revocations

## Models Structure

### User Model
- **loginId**: Unique identifier for login (validates: alphanumeric + @, _, -)
- **email**: Email address (unique)
- **user_type**: Predefined user types (super_admin, admin, etc.)
- **Integration**: Works with Django's Groups and Permissions

### Role Model
- **Integrated with Django Groups**: Each role automatically creates a Django Group
- **Permission Management**: Assign Django permissions to roles
- **Metadata**: Role levels, system roles, assignment limits

### UserRole Model
- **Assignment Tracking**: Who assigned, when, why
- **Expiration**: Optional role expiration dates
- **Audit Trail**: Track revocations and reasons

## API Endpoints

### Authentication & User Management

#### 1. Create User
```http
POST /api/v1/users/
Content-Type: application/json

{
    "login_id": "john_doe123",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+8801712345678",
    "user_type": "admin",
    "employee_id": "EMP001",
    "designation": "System Administrator",
    "department": "IT",
    "roles": [1, 2]  // Optional: Assign roles during creation
}
```

**Response:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "login_id": "john_doe123",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+8801712345678",
    "user_type": "admin",
    "employee_id": "EMP001",
    "designation": "System Administrator",
    "department": "IT",
    "is_active": true,
    "is_staff": false,
    "roles": [],
    "permissions": [],
    "created_at": "2024-01-15T10:30:00Z"
}
```

#### 2. List Users
```http
GET /api/v1/users/
GET /api/v1/users/?user_type=admin
GET /api/v1/users/?role=administrator
GET /api/v1/users/?search=john
```

#### 3. Get User Details
```http
GET /api/v1/users/{user_id}/
```

#### 4. Update User
```http
PATCH /api/v1/users/{user_id}/
Content-Type: application/json

{
    "first_name": "John Updated",
    "designation": "Senior Administrator"
}
```

#### 5. Change Password
```http
POST /api/v1/users/change-password/
Content-Type: application/json

{
    "old_password": "OldPass123!",
    "new_password": "NewSecurePass123!",
    "new_password_confirm": "NewSecurePass123!"
}
```

### Role Management

#### 1. Create Role
```http
POST /api/v1/roles/
Content-Type: application/json

{
    "name": "billing_manager",
    "display_name": "Billing Manager",
    "description": "Manages billing operations and customer accounts",
    "role_level": 3,
    "can_assign_roles": false,
    "max_assignments": 10,
    "permission_ids": [1, 2, 3, 15, 16]  // Django permission IDs
}
```

**Response:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "billing_manager",
    "display_name": "Billing Manager",
    "description": "Manages billing operations and customer accounts",
    "role_level": 3,
    "is_active": true,
    "is_system_role": false,
    "can_assign_roles": false,
    "max_assignments": 10,
    "permissions": [
        {
            "id": 1,
            "name": "Can add user",
            "codename": "add_user",
            "content_type": 4
        }
    ],
    "users_count": 0,
    "created_at": "2024-01-15T10:30:00Z"
}
```

#### 2. List Roles
```http
GET /api/v1/roles/
GET /api/v1/roles/?is_active=true
GET /api/v1/roles/?role_level=1
```

#### 3. Assign Role to User
```http
POST /api/v1/roles/assign/
Content-Type: application/json

{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "role_id": "550e8400-e29b-41d4-a716-446655440001",
    "action": "assign",
    "reason": "Promoted to billing manager position",
    "expires_at": "2024-12-31T23:59:59Z"  // Optional
}
```

**Response:**
```json
{
    "action": "assigned",
    "created": true,
    "user_role": {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "role": "550e8400-e29b-41d4-a716-446655440001",
        "role_name": "Billing Manager",
        "is_active": true,
        "assigned_by": "550e8400-e29b-41d4-a716-446655440003",
        "assigned_by_name": "Super Admin",
        "assigned_at": "2024-01-15T10:30:00Z",
        "expires_at": "2024-12-31T23:59:59Z",
        "assignment_reason": "Promoted to billing manager position"
    }
}
```

#### 4. Revoke Role from User
```http
POST /api/v1/roles/assign/
Content-Type: application/json

{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "role_id": "550e8400-e29b-41d4-a716-446655440001",
    "action": "revoke",
    "reason": "Position changed"
}
```

#### 5. Bulk Role Assignment
```http
POST /api/v1/roles/bulk-assign/
Content-Type: application/json

{
    "user_ids": [
        "550e8400-e29b-41d4-a716-446655440000",
        "550e8400-e29b-41d4-a716-446655440004"
    ],
    "role_id": "550e8400-e29b-41d4-a716-446655440001",
    "action": "assign",
    "reason": "Department restructuring"
}
```

### Permission Management

#### 1. List All Permissions
```http
GET /api/v1/permissions/
GET /api/v1/permissions/?app_label=users
GET /api/v1/permissions/?search=add
```

#### 2. Get User Permissions
```http
GET /api/v1/users/permissions/
```

**Response:**
```json
{
    "user": "john_doe123",
    "permissions": [
        "add_user",
        "change_user",
        "view_user",
        "add_role",
        "change_role"
    ],
    "grouped_permissions": {
        "users": ["add_user", "change_user", "view_user"],
        "auth": ["add_role", "change_role"]
    },
    "roles": ["billing_manager", "support_staff"]
}
```

### Dashboard & Statistics

#### 1. Dashboard Statistics
```http
GET /api/v1/dashboard/stats/
```

**Response:**
```json
{
    "total_users": 150,
    "active_users": 142,
    "total_roles": 8,
    "active_roles": 7,
    "total_permissions": 45,
    "custom_permissions": 12,
    "user_types": {
        "super_admin": 2,
        "admin": 5,
        "billing_manager": 8,
        "noc_manager": 3,
        "support_staff": 25,
        "reseller_admin": 15,
        "sub_reseller_admin": 30,
        "field_staff": 62
    }
}
```

## Django Admin Usage

### 1. Accessing Admin Interface
1. Navigate to `/admin/`
2. Login with superuser credentials
3. Access user and role management sections

### 2. Managing Users
- **Users Section**: Create, edit, and manage users
- **Role Assignment**: Assign roles directly from user edit page
- **Permission Overview**: View all user permissions and roles

### 3. Managing Roles
- **Roles Section**: Create and manage custom roles
- **Permission Assignment**: Assign Django permissions to roles
- **Group Integration**: Automatically synced with Django Groups

### 4. Permission Management
- **Groups**: Manage Django Groups (auto-created from Roles)
- **Permissions**: View and manage all Django permissions
- **Custom Permissions**: Create application-specific permissions

## Usage Approach

### 1. Initial Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Enter loginId, email, and password when prompted
```

### 2. Creating Roles (via Admin or API)
1. **Via Admin**: Go to Admin → Roles → Add Role
2. **Via API**: Use POST /api/v1/roles/ endpoint
3. **Assign Permissions**: Select Django permissions for the role

### 3. Creating Users
1. **Via Admin**: Go to Admin → Users → Add User
2. **Via API**: Use POST /api/v1/users/ endpoint
3. **Assign Roles**: Assign roles during creation or later

### 4. Permission Checking in Code
```python
# Check if user has specific permission
if request.user.has_perm('users.add_user'):
    # User can add users
    pass

# Check if user has specific role
if request.user.has_role('billing_manager'):
    # User has billing manager role
    pass

# Get all user permissions
permissions = request.user.get_all_permissions()
```

### 5. Role-Based View Protection
```python
from django.contrib.auth.decorators import permission_required
from rest_framework.permissions import IsAuthenticated

# Function-based view
@permission_required('users.add_user')
def create_user_view(request):
    pass

# Class-based view
class UserCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        if not self.request.user.has_perm('users.add_user'):
            raise PermissionDenied("You don't have permission to create users")
        serializer.save()
```

## LoginId Validation Rules

### Format Requirements
- **Allowed Characters**: Letters (a-z, A-Z), Numbers (0-9), @, _, -
- **Examples of Valid LoginIds**:
  - `john_doe123`
  - `admin@ktl`
  - `user-001`
  - `billing_manager_2024`

### Validation Implementation
```python
# Custom validator in models.py
def validate_login_id(value):
    if not re.match(r'^[a-zA-Z0-9@_-]+$', value):
        raise ValidationError(
            'LoginId can only contain letters, numbers, @, _, and - characters.'
        )

# Usage in serializer
def validate_login_id(self, value):
    if User.objects.filter(login_id=value).exists():
        raise serializers.ValidationError("A user with this login ID already exists.")
    return value
```

## Superadmin Capabilities

### 1. Full Permission Control
- Create and manage all roles
- Assign any permission to any role
- Override role assignment limits
- Manage system roles

### 2. User Management
- Create users with any role
- Modify user roles and permissions
- Access all user data
- Bulk operations

### 3. System Configuration
- Create custom permissions
- Manage permission categories
- Configure role hierarchies
- System-wide settings

## Security Features

### 1. Permission Inheritance
- Users inherit permissions from assigned roles
- Roles inherit permissions from Django Groups
- Direct user permissions override role permissions

### 2. Audit Trail
- Track all role assignments and revocations
- Record who made changes and when
- Maintain assignment reasons and history

### 3. Validation & Security
- LoginId format validation
- Password strength requirements
- Unique constraint enforcement
- Permission-based access control

## Error Handling

### Common API Errors
```json
// Invalid loginId format
{
    "login_id": ["LoginId can only contain letters, numbers, @, _, and - characters."]
}

// Duplicate loginId
{
    "login_id": ["A user with this login ID already exists."]
}

// Permission denied
{
    "detail": "You do not have permission to perform this action."
}

// Role not found
{
    "error": "Role not found"
}
```

## Best Practices

### 1. Role Design
- Keep roles focused and specific
- Use descriptive role names
- Set appropriate role levels
- Limit role assignments when needed

### 2. Permission Management
- Group related permissions together
- Use Django's built-in permissions when possible
- Create custom permissions for specific business logic
- Regularly audit permission assignments

### 3. User Management
- Use meaningful loginIds
- Enforce strong password policies
- Regular role reviews and updates
- Monitor user activity and permissions

This comprehensive role-based user system provides a robust foundation for managing users, roles, and permissions in your KTL ISP Billing system while leveraging Django's built-in security features.
