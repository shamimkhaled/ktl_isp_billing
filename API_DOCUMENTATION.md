# KTL ISP Billing - Authentication API Documentation

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication APIs

### 1. User Login
**Endpoint:** `POST /auth/login/`
**Description:** Login with login_id/password for all user types (user/admin/staff) and get JWT tokens

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

**Error Response (400) - Account Locked:**
```json
{
    "success": false,
    "status": 400,
    "message": "Login failed",
    "error": {
        "non_field_errors": ["Account is locked until 2024-01-01 10:30:00."]
    }
}
```

---

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

**Error Response (400):**
```json
{
    "success": false,
    "status": 400,
    "message": "Token refresh failed",
    "error": {
        "non_field_errors": ["Invalid or expired refresh token."]
    }
}
```

---

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

---

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

**Error Response (401):**
```json
{
    "success": false,
    "status": 401,
    "message": "Token is invalid or expired",
    "error": []
}
```

---

## User Management APIs

### 5. Get Current User Profile
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

---

### 6. Change Password
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

**Error Response (400):**
```json
{
    "success": false,
    "status": 400,
    "message": "Password change failed",
    "error": {
        "old_password": ["Old password is incorrect."],
        "new_password": ["This password is too common."]
    }
}
```

---

### 7. Get User Permissions
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
        "user": "admin001",
        "permissions": [
            "users.add_user",
            "users.change_user",
            "users.delete_user",
            "users.view_user",
            "roles.add_role",
            "roles.change_role"
        ],
        "grouped_permissions": {
            "users": [
                "users.add_user",
                "users.change_user",
                "users.delete_user",
                "users.view_user"
            ],
            "roles": [
                "roles.add_role",
                "roles.change_role"
            ]
        },
        "roles": [
            "Administrator",
            "User Manager"
        ]
    }
}
```

---

## User Types Supported

The system supports the following user types:

1. **super_admin** - Super Administrator
2. **admin** - Administrator  
3. **billing_manager** - Billing Manager
4. **noc_manager** - NOC Manager
5. **support_staff** - Support Staff
6. **reseller_admin** - Reseller Administrator
7. **sub_reseller_admin** - Sub-Reseller Administrator
8. **field_staff** - Field Staff

---

## Authentication Flow

1. **Login:** Use `/auth/login/` with login_id and password
2. **Access Protected Resources:** Use the access token in Authorization header
3. **Refresh Token:** When access token expires, use `/auth/refresh/` 
4. **Logout:** Use `/auth/logout/` to invalidate tokens

---

## Error Codes

- **400** - Bad Request (validation errors)
- **401** - Unauthorized (invalid/expired token)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found
- **500** - Internal Server Error

---

## Postman Collection Setup

### Environment Variables
```
base_url: http://localhost:8000/api/v1
access_token: {{access_token}}
refresh_token: {{refresh_token}}
```

### Pre-request Script for Login
```javascript
// No pre-request script needed for login
```

### Test Script for Login
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set("access_token", response.tokens.access);
    pm.environment.set("refresh_token", response.tokens.refresh);
}
```

### Authorization Header for Protected Routes
```
Type: Bearer Token
Token: {{access_token}}
