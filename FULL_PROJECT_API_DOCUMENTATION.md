# KTL ISP Billing - Complete API Documentation

## Base URL
```
http://localhost:8000/api/v1/
```

## Table of Contents
1. [Authentication APIs](#authentication-apis)
2. [User Management APIs](#user-management-apis)
3. [Role Management APIs](#role-management-apis)
4. [Permission Management APIs](#permission-management-apis)
5. [Group Management APIs](#group-management-apis)
6. [Organization Management APIs](#organization-management-apis)
7. [Location APIs](#location-apis)
8. [Dashboard APIs](#dashboard-apis)

---

## Authentication APIs

### 1. User Login
**Endpoint:** `POST /auth/login/`  
**Description:** Login with login_id/password for all user types and get JWT tokens

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "login_id": "admin001",
    "password": "password123",
    "remember_me": false
}
```

**Success Response (200):**
```json
{
    "success": true,
    "status": 200,
    "message": "Login successful",
    "data": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "login_id": "admin001",
            "email": "admin@example.com",
            "name": "Admin User",
            "mobile": "+8801712345678",
            "user_type": "admin",
            "employee_id": "EMP001",
            "designation": null,
            "department": null,
            "district_info": null,
            "thana_info": null,
            "is_active": true,
            "is_staff": true,
            "is_superuser": false,
            "is_email_verified": false,
            "is_phone_verified": false,
            "is_first_login": true,
            "profile_photo": null,
            "language_preference": "en",
            "timezone": "Asia/Dhaka",
            "roles": [
                {
                    "id": "role-uuid",
                    "role_name": "Administrator",
                    "is_active": true,
                    "assigned_by_name": "Super Admin",
                    "assigned_at": "2024-01-01T10:00:00Z"
                }
            ],
            "permissions": [
                "users.add_user",
                "users.change_user",
                "users.view_user"
            ],
            "last_login": "2024-01-01T10:00:00Z",
            "date_joined": "2024-01-01T00:00:00Z"
        },
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjQwOTk1MjAwLCJpYXQiOjE2NDA5OTE2MDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIn0.example_access_token",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY0MTU5NjQwMCwiaWF0IjoxNjQwOTkxNjAwLCJqdGkiOiIwOTg3NjU0MzIxIiwidXNlcl9pZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCJ9.example_refresh_token",
            "token_type": "Bearer"
        },
        "remember_me": false,
        "expires_at": "2024-01-01T11:00:00Z"
    }
}
```

**Error Response (400):**
```json
{
    "success": false,
    "status": 400,
    "message": "Login failed",
    "error": {
        "non_field_errors": ["Invalid login credentials."]
    }
}
```

### 2. Token Refresh
**Endpoint:** `POST /auth/refresh/`  
**Description:** Refresh access token using refresh token

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY0MTU5NjQwMCwiaWF0IjoxNjQwOTkxNjAwLCJqdGkiOiIwOTg3NjU0MzIxIiwidXNlcl9pZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCJ9.example_refresh_token"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "status": 200,
    "message": "Token refreshed successfully",
    "data": {
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.new_access_token",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.new_refresh_token",
            "token_type": "Bearer"
        },
        "expires_at": "2024-01-01T12:00:00Z"
    }
}
```

### 3. User Logout
**Endpoint:** `POST /auth/logout/`  
**Description:** Logout user and blacklist tokens

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.refresh_token",
    "logout_all_devices": false
}
```

**Success Response (200):**
```json
{
    "success": true,
    "status": 200,
    "message": "Logout successful",
    "data": []
}
```

### 4. Verify Token
**Endpoint:** `POST /auth/verify/`  
**Description:** Verify token validity and get user information

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body:** (Empty)
```json
{}
```

**Success Response (200):**
```json
{
    "success": true,
    "status": 200,
    "message": "Token is valid",
    "data": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "login_id": "admin001",
            "email": "admin@example.com",
            "name": "Admin User",
            "user_type": "admin"
        },
        "expires_at": "2024-01-01T12:00:00Z"
    }
}
```

---

## User Management APIs

### 1. Create User
**Endpoint:** `POST /users/`  
**Description:** Create a new user

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body:**
```json
{
    "login_id": "john_doe123",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "name": "John Doe",
    "mobile": "+8801712345678",
    "user_type": "admin",
    "employee_id": "EMP001",
    "designation": "System Administrator",
    "department": "IT",
    "roles": [1, 2]
}
```

**Success Response (201):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "login_id": "john_doe123",
    "email": "john@example.com",
    "name": "John Doe",
    "mobile": "+8801712345678",
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

### 2. List Users
**Endpoint:** `GET /users/`  
**Description:** List all users with filtering and search

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Query Parameters:**
- `user_type`: Filter by user type
- `role`: Filter by role name
- `search`: Search in login_id, email, first_name, last_name, employee_id
- `ordering`: Order by fields like login_id, email, date_joined

**Success Response (200):**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "login_id": "john_doe123",
            "email": "john@example.com",
            "name": "John Doe",
            "mobile": "+8801712345678",
            "user_type": "admin",
            "employee_id": "EMP001",
            "designation": "System Administrator",
            "department": "IT",
            "is_active": true,
            "is_staff": false,
            "roles": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440001",
                    "role": "550e8400-e29b-41d4-a716-446655440002",
                    "role_name": "Administrator",
                    "is_active": true,
                    "assigned_by": "550e8400-e29b-41d4-a716-446655440003",
                    "assigned_by_name": "Super Admin",
                    "assigned_at": "2024-01-15T10:30:00Z",
                    "expires_at": null,
                    "assignment_reason": "Initial role assignment"
                }
            ],
            "permissions": ["users.add_user", "users.change_user"],
            "last_login": "2024-01-15T10:30:00Z",
            "date_joined": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### 3. Get User Details
**Endpoint:** `GET /users/{user_id}/`  
**Description:** Get details of a specific user

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Success Response (200):** Same structure as list response but single object

### 4. Update User
**Endpoint:** `PUT/PATCH /users/{user_id}/`  
**Description:** Update user information

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body (PATCH example):**
```json
{
    "designation": "Senior Administrator",
    "department": "IT Operations"
}
```

**Success Response (200):** Same structure as create response

### 5. Delete User
**Endpoint:** `DELETE /users/{user_id}/`  
**Description:** Soft delete user (deactivate)

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Success Response (204):** No content

### 6. Get Current User Profile
**Endpoint:** `GET /users/profile/`  
**Description:** Get current authenticated user profile

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Success Response (200):**
```json
{
    "success": true,
    "status": 200,
    "message": "User profile retrieved successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "login_id": "admin001",
        "email": "admin@example.com",
        "name": "Admin User",
        "mobile": "+8801712345678",
        "user_type": "admin",
        "employee_id": "EMP001",
        "designation": null,
        "department": null,
        "salary": null,
        "date_of_joining": null,
        "address": null,
        "contact_person_name": null,
        "contact_person_phone": null,
        "district": null,
        "district_info": null,
        "thana": null,
        "thana_info": null,
        "postal_code": null,
        "remarks": null,
        "is_active": true,
        "is_staff": true,
        "is_email_verified": false,
        "is_phone_verified": false,
        "profile_photo": null,
        "language_preference": "en",
        "timezone": "Asia/Dhaka",
        "roles": [],
        "permissions": [],
        "last_login": "2024-01-01T10:00:00Z",
        "date_joined": "2024-01-01T00:00:00Z",
        "access_token": "current_access_token",
        "refresh_token": "current_refresh_token",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
    }
}
```

### 7. Change Password
**Endpoint:** `POST /users/change-password/`  
**Description:** Change password for current authenticated user

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body:**
```json
{
    "old_password": "current_password",
    "new_password": "new_password123",
    "new_password_confirm": "new_password123"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "status": 200,
    "message": "Password changed successfully",
    "data": []
}
```

### 8. Get User Permissions
**Endpoint:** `GET /users/permissions/`  
**Description:** Get all permissions for current authenticated user

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Success Response (200):**
```json
{
    "success": true,
    "status": 200,
    "message": "User permissions retrieved successfully",
    "data": {
        "user": "john_doe123",
        "permissions": [
            "users.add_user",
            "users.change_user",
            "users.view_user",
            "roles.add_role",
            "roles.change_role"
        ],
        "grouped_permissions": {
            "users": ["users.add_user", "users.change_user", "users.view_user"],
            "roles": ["roles.add_role", "roles.change_role"]
        },
        "roles": ["billing_manager", "support_staff"]
    }
}
```

---

## Role Management APIs

### 1. Create Role
**Endpoint:** `POST /roles/`  
**Description:** Create a new role

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body:**
```json
{
    "name": "billing_manager",
    "display_name": "Billing Manager",
    "description": "Manages billing operations and customer accounts",
    "role_level": 3,
    "can_assign_roles": false,
    "max_assignments": 10,
    "permission_ids": [1, 2, 3, 15, 16]
}
```

**Success Response (201):**
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
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### 2. List Roles
**Endpoint:** `GET /roles/`  
**Description:** List all roles

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Query Parameters:**
- `is_active`: Filter by active status
- `is_system_role`: Filter by system roles
- `role_level`: Filter by role level
- `search`: Search in name, display_name, description
- `ordering`: Order by role_level, display_name, created_at

**Success Response (200):**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
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
            "users_count": 5,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### 3. Get Role Details
**Endpoint:** `GET /roles/{role_id}/`  
**Description:** Get details of a specific role

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Success Response (200):** Same structure as list response but single object

### 4. Update Role
**Endpoint:** `PUT/PATCH /roles/{role_id}/`  
**Description:** Update role information

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body (PATCH example):**
```json
{
    "display_name": "Senior Billing Manager",
    "max_assignments": 15
}
```

**Success Response (200):** Same structure as create response

### 5. Delete Role
**Endpoint:** `DELETE /roles/{role_id}/`  
**Description:** Delete a role

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Success Response (204):** No content

### 6. Assign Role to User
**Endpoint:** `POST /roles/assign/`  
**Description:** Assign or revoke roles from users

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body:**
```json
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "role_id": "550e8400-e29b-41d4-a716-446655440001",
    "action": "assign",
    "reason": "Promoted to billing manager position",
    "expires_at": "2024-12-31T23:59:59Z"
}
```

**Success Response (200):**
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

### 7. Bulk Role Assignment
**Endpoint:** `POST /roles/bulk-assign/`  
**Description:** Bulk assign/revoke roles

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body:**
```json
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

**Success Response (200):**
```json
{
    "results": [
        {
            "user": "john_doe123",
            "action": "assigned",
            "created": true
        },
        {
            "user": "jane_smith456",
            "action": "assigned",
            "created": true
        }
    ]
}
```

### 8. List User Role Assignments
**Endpoint:** `GET /user-roles/`  
**Description:** List all role assignments

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Query Parameters:**
- `is_active`: Filter by active status
- `user`: Filter by user ID
- `role`: Filter by role ID
- `search`: Search in user login_id, email, role name
- `ordering`: Order by assigned_at, expires_at

**Success Response (200):**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "role": "550e8400-e29b-41d4-a716-446655440001",
            "role_name": "Billing Manager",
            "is_active": true,
            "assigned_by": "550e8400-e29b-41d4-a716-446655440003",
            "assigned_by_name": "Super Admin",
            "assigned_at": "2024-01-15T10:30:00Z",
            "expires_at": "2024-12-31T23:59:59Z",
            "assignment_reason": "Promoted to billing manager position",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

---

## Permission Management APIs

### 1. List All Permissions
**Endpoint:** `GET /permissions/`  
**Description:** List all Django permissions

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Query Parameters:**
- `content_type`: Filter by content type ID
- `app_label`: Filter by app label
- `search`: Search in name, codename

**Success Response (200):**
```json
{
    "count": 45,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Can add user",
            "codename": "add_user",
            "content_type": 4
        },
        {
            "id": 2,
            "name": "Can change user",
            "codename": "change_user",
            "content_type": 4
        }
    ]
}
```

### 2. Create Permission Category
**Endpoint:** `POST /permission-categories/`  
**Description:** Create a new permission category

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body:**
```json
{
    "name": "user_management",
    "display_name": "User Management",
    "description": "Permissions related to user management",
    "icon": "fas fa-users",
    "order": 1
}
```

**Success Response (201):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440005",
    "name": "user_management",
    "display_name": "User Management",
    "description": "Permissions related to user management",
    "icon": "fas fa-users",
    "order": 1,
    "permissions_count": 0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. List Permission Categories
**Endpoint:** `GET /permission-categories/`  
**Description:** List all permission categories

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Success Response (200):**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440005",
            "name": "user_management",
            "display_name": "User Management",
            "description": "Permissions related to user management",
            "icon": "fas fa-users",
            "order": 1,
            "permissions_count": 5,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### 4. Create Custom Permission
**Endpoint:** `POST /custom-permissions/`  
**Description:** Create a new custom permission

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body:**
```json
{
    "codename": "view_reports",
    "name": "Can view reports",
    "description": "Permission to view system reports",
    "category": "550e8400-e29b-41d4-a716-446655440005",
    "is_active": true,
    "is_system_permission": false
}
```

**Success Response (201):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440006",
    "codename": "view_reports",
    "name": "Can view reports",
    "description": "Permission to view system reports",
    "category": "550e8400-e29b-41d4-a716-446655440005",
    "category_name": "User Management",
    "is_active": true,
    "is_system_permission": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### 5. List Custom Permissions
**Endpoint:** `GET /custom-permissions/`  
**Description:** List all custom permissions

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Query Parameters:**
- `is_active`: Filter by active status
- `is_system_permission`: Filter by system permissions
- `category`: Filter by category ID
- `search`: Search in name, codename, description

**Success Response (200):**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440006",
            "codename": "view_reports",
            "name": "Can view reports",
            "description": "Permission to view system reports",
            "category": "550e8400-e29b-41d4-a716-446655440005",
            "category_name": "User Management",
            "is_active": true,
            "is_system_permission": false,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

---

## Group Management APIs

### 1. Create Group
**Endpoint:** `POST /groups/`  
**Description:** Create a new Django group

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body:**
```json
{
    "name": "Billing Team",
    "permission_ids": [1, 2, 3]
}
```

**Success Response (201):**
```json
{
    "id": 1,
    "name": "Billing Team",
    "permissions": [
        {
            "id": 1,
            "name": "Can add user",
            "codename": "add_user",
            "content_type": 4
        }
    ]
}
```

### 2. List Groups
**Endpoint:** `GET /groups/`  
**Description:** List all Django groups

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Query Parameters:**
- `search`: Search in group name

**Success Response (200):**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Billing Team",
            "permissions": [
                {
                    "id": 1,
                    "name": "Can add user",
                    "codename": "add_user",
                    "content_type": 4
                }
            ]
        }
    ]
}
```

### 3. Get Group Details
**Endpoint:** `GET /groups/{group_id}/`  
**Description:** Get details of a specific group

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Success Response (200):** Same structure as list response but single object

### 4. Update Group
**Endpoint:** `PUT/PATCH /groups/{group_id}/`  
**Description:** Update group information

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body (PATCH example):**
```json
{
    "name": "Updated Billing Team",
    "permission_ids": [1, 2, 4]
}
```

**Success Response (200):** Same structure as create response

### 5. Delete Group
**Endpoint:** `DELETE /groups/{group_id}/`  
**Description:** Delete a group

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Success Response (204):** No content

---

## Organization Management APIs

### 1. Create Organization
**Endpoint:** `POST /organizations/`  
**Description:** Create a new organization

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.access_token
```

**Request Body:**
```json
{
    "company_name": "Kloud Technologies Ltd",
    "company_code": "KTL",
    "business_license": "BL123456",
    "vat_registration": "VAT789012",
    "address": "123 Tech Street, Dhaka",
    "contact_email": "info@kloudtech.com",
    "contact_phone": "+8801712345678",
    "website": "https://kloudtech.com",
    "organization_type": "Banking",
    "revenue_sharing_enabled": true,
    "default_reseller_share": 50.00,
    "default_sub_reseller_share": 45.00,
    "default_ktl_share_with_sub": 50.00,
    "default_reseller_share_with_sub": 5.00,
    "billing_settings": {
        "max_manual_grace_days": 9,
        "disable_expiry": false,
        "default_grace_days": 1,
        "jump_billing": true,
        "default_grace_hours": 14,
        "max_inactive_days": 3,
        "delete_permanent_disable_secret_from_mikrotik": 1
    },
    "sync_settings": {
        "sync_area_to_mikrotik": false,
        "sync_address_to_mikrotik": false,
        "sync_customer_mobile_to_mikrotik": false
    }
}
```

**Success Response (201):**
```json
{
    "success": true,
    "status": 201,
    "message": "Organization created successfully.",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "company_name": "Kloud Technologies Ltd",
        "company_code": "KTL",
        "business_license": "BL123456",
        "vat_registration": "VAT789012",
        "address": "123 Tech Street, Dhaka",
        "contact_email": "info@kloudtech.com",
        "contact_phone": "+8801712345678",
        "website": "https://kloudtech.com",
        "organization_type": "Banking",
        "revenue_sharing_enabled": true,
        "default_reseller_share": 50.00,
        "default_sub_reseller_share": 45.00,
        "default_ktl_share_with_sub": 50.00,
        "default_reseller_share_with_sub": 5.00,
        "billing_settings": {
            "id": 1,
            "organization": "550e8400-e29b-41d4-a716-446655440000",
            "max_manual_grace_days": 9,
            "disable_expiry": false,
            "default_grace_days": 1,
            "jump_billing": true,
            "default_grace_hours": 14,
            "max_inactive_days":
