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
9. [Common Information](#common-information)

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

**Request Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.refresh_token"
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
            "access": "new_access_token",
            "refresh": "new_refresh_token",
            "token_type": "Bearer"
        },
        "expires_at": "2024-01-01T12:00:00Z"
    }
}
```

### 3. User Logout
**Endpoint:** `POST /auth/logout/`  
**Description:** Logout user and blacklist tokens

**Request Body:**
```json
{
    "refresh_token": "refresh_token",
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
**Description:** Verify token validity

**Success Response (200):**
```json
{
    "success": true,
    "status": 200,
    "message": "Token is valid",
    "data": {
        "user": {
            "id": "user_id",
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

### 2. List Users
**Endpoint:** `GET /users/`

**Query Parameters:**
- `user_type`, `role`, `search`, `ordering`

### 3. Get User Details
**Endpoint:** `GET /users/{user_id}/`

### 4. Update User
**Endpoint:** `PATCH /users/{user_id}/`

### 5. Delete User
**Endpoint:** `DELETE /users/{user_id}/`

### 6. Get Current User Profile
**Endpoint:** `GET /users/profile/`

### 7. Change Password
**Endpoint:** `POST /users/change-password/`

**Request Body:**
```json
{
    "old_password": "current_password",
    "new_password": "new_password123",
    "new_password_confirm": "new_password123"
}
```

### 8. Get User Permissions
**Endpoint:** `GET /users/permissions/`

---

## Role Management APIs

### 1. Create Role
**Endpoint:** `POST /roles/`

**Request Body:**
```json
{
    "name": "billing_manager",
    "display_name": "Billing Manager",
    "description": "Manages billing operations",
    "role_level": 3,
    "can_assign_roles": false,
    "max_assignments": 10,
    "permission_ids": [1, 2, 3]
}
```

### 2. List Roles
**Endpoint:** `GET /roles/`

### 3. Assign Role to User
**Endpoint:** `POST /roles/assign/`

**Request Body:**
```json
{
    "user_id": "user_id",
    "role_id": "role_id",
    "action": "assign",
    "reason": "Promotion",
    "expires_at": "2024-12-31T23:59:59Z"
}
```

### 4. Bulk Role Assignment
**Endpoint:** `POST /roles/bulk-assign/`

### 5. List User Role Assignments
**Endpoint:** `GET /user-roles/`

---

## Permission Management APIs

### 1. List All Permissions
**Endpoint:** `GET /permissions/`

### 2. Create Permission Category
**Endpoint:** `POST /permission-categories/`

### 3. List Permission Categories
**Endpoint:** `GET /permission-categories/`

### 4. Create Custom Permission
**Endpoint:** `POST /custom-permissions/`

### 5. List Custom Permissions
**Endpoint:** `GET /custom-permissions/`

---

## Group Management APIs

### 1. Create Group
**Endpoint:** `POST /groups/`

**Request Body:**
```json
{
    "name": "Billing Team",
    "permission_ids": [1, 2, 3]
}
```

### 2. List Groups
**Endpoint:** `GET /groups/`

### 3. Get Group Details
**Endpoint:** `GET /groups/{group_id}/`

### 4. Update Group
**Endpoint:** `PUT/PATCH /groups/{group_id}/`

### 5. Delete Group
**Endpoint:** `DELETE /groups/{group_id}/`

---

## Organization Management APIs

### 1. Create Organization
**Endpoint:** `POST /organizations/`

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

### 2. List Organizations
**Endpoint:** `GET /organizations/`

### 3. Get Organization Details
**Endpoint:** `GET /organizations/{id}/`

### 4. Update Organization
**Endpoint:** `PUT/PATCH /organizations/{id}/`

### 5. Delete Organization
**Endpoint:** `DELETE /organizations/{id}/`

---

## Location APIs

### 1. List Districts
**Endpoint:** `GET /locations/districts/`

**Query Parameters:**
- `search`, `ordering`

### 2. List Thanas
**Endpoint:** `GET /locations/thanas/`

**Query Parameters:**
- `district`, `search`, `ordering`

### 3. Get District Thanas
**Endpoint:** `GET /locations/districts/{district_id}/thanas/`

### 4. Get Locations Summary
**Endpoint:** `GET /locations/summary/`

---

## Dashboard APIs

### 1. Get Dashboard Statistics
**Endpoint:** `GET /dashboard/stats/`

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

---

## Common Information

### User Types Supported
- **super_admin** - Super Administrator
- **admin** - Administrator
- **billing_manager** - Billing Manager
- **noc_manager** - NOC Manager
- **support_staff** - Support Staff
- **reseller_admin** - Reseller Administrator
- **sub_reseller_admin** - Sub-Reseller Administrator
- **field_staff** - Field Staff

### Authentication Flow
1. Login → Get JWT tokens
2. Use access token in Authorization header
3. Refresh token when expired
4. Logout to blacklist tokens

### Common Error Responses
```json
// 401 Unauthorized
{
    "success": false,
    "status": 401,
    "message": "Authentication credentials were not provided.",
    "error": []
}

// 403 Forbidden
{
    "success": false,
    "status": 403,
    "message": "You do not have permission to perform this action.",
    "error": []
}

// 400 Bad Request
{
    "success": false,
    "status": 400,
    "message": "Bad Request",
    "error": {
        "field_name": ["Error message"]
    }
}
```

### Rate Limiting
- Login attempts: 5 per 15 minutes
- API requests: 1000 per hour per user
- Password reset: 3 per hour per user

### Data Formats
- **DateTime:** ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- **UUID:** Standard UUID v4 format
- **Pagination:** Standard Django REST framework pagination

---

*This documentation provides comprehensive API specifications for the KTL ISP Billing system. All endpoints require proper authentication except login, refresh, and verify.*
