from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, Role, UserRole, PermissionCategory, CustomPermission
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    RoleSerializer, UserRoleSerializer, PasswordChangeSerializer,
    RoleAssignmentSerializer, PermissionSerializer, GroupSerializer,
    PermissionCategorySerializer, CustomPermissionSerializer,
    LoginSerializer, TokenRefreshSerializer, LogoutSerializer, UserLoginResponseSerializer
)


class UserListCreateView(generics.ListCreateAPIView):
    """
    List all users or create a new user
    
    GET /api/users/ - List users with filtering and search
    POST /api/users/ - Create new user
    """
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_type', 'is_active', 'is_staff']
    search_fields = ['login_id', 'email', 'first_name', 'last_name', 'employee_id']
    ordering_fields = ['login_id', 'email', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Add role filtering
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(user_roles__role__name=role, user_roles__is_active=True)
        return queryset.prefetch_related('user_roles__role', 'groups__permissions')


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user
    
    GET /api/users/{id}/ - Get user details
    PUT /api/users/{id}/ - Update user
    PATCH /api/users/{id}/ - Partial update user
    DELETE /api/users/{id}/ - Deactivate user (soft delete)
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
    
    def perform_destroy(self, instance):
        # Soft delete - deactivate user instead of deleting
        instance.is_active = False
        instance.save()


class ChangePasswordView(APIView):
    """
    Change user password
    
    POST /api/users/change-password/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'status': 200,
                'message': 'Password changed successfully',
                'data': []
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'status': 400,
            'message': 'Password change failed',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class RoleListCreateView(generics.ListCreateAPIView):
    """
    List all roles or create a new role
    
    GET /api/roles/ - List roles
    POST /api/roles/ - Create new role
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_system_role', 'role_level']
    search_fields = ['name', 'display_name', 'description']
    ordering_fields = ['role_level', 'display_name', 'created_at']
    ordering = ['role_level', 'display_name']


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a role
    
    GET /api/roles/{id}/ - Get role details
    PUT /api/roles/{id}/ - Update role
    PATCH /api/roles/{id}/ - Partial update role
    DELETE /api/roles/{id}/ - Delete role
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    
    def perform_destroy(self, instance):
        # Check if role has active assignments
        if instance.user_assignments.filter(is_active=True).exists():
            return Response(
                {'error': 'Cannot delete role with active user assignments'},
                status=status.HTTP_400_BAD_REQUEST
            )
        super().perform_destroy(instance)


class RoleAssignmentView(APIView):
    """
    Assign or revoke roles from users
    
    POST /api/roles/assign/ - Assign/revoke role
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = RoleAssignmentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRoleListView(generics.ListAPIView):
    """
    List user role assignments
    
    GET /api/user-roles/ - List all role assignments
    GET /api/user-roles/?user={user_id} - List roles for specific user
    GET /api/user-roles/?role={role_id} - List users with specific role
    """
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'user', 'role']
    search_fields = ['user__login_id', 'user__email', 'role__name']
    ordering_fields = ['assigned_at', 'expires_at']
    ordering = ['-assigned_at']


class PermissionListView(generics.ListAPIView):
    """
    List all Django permissions
    
    GET /api/permissions/ - List permissions with filtering
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['content_type']
    search_fields = ['name', 'codename']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by app label
        app_label = self.request.query_params.get('app_label')
        if app_label:
            queryset = queryset.filter(content_type__app_label=app_label)
        return queryset.select_related('content_type')


class GroupListCreateView(generics.ListCreateAPIView):
    """
    List all groups or create a new group
    
    GET /api/groups/ - List groups
    POST /api/groups/ - Create new group
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a group
    
    GET /api/groups/{id}/ - Get group details
    PUT /api/groups/{id}/ - Update group
    DELETE /api/groups/{id}/ - Delete group
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PermissionCategoryListCreateView(generics.ListCreateAPIView):
    """
    List all permission categories or create a new one
    
    GET /api/permission-categories/ - List categories
    POST /api/permission-categories/ - Create new category
    """
    queryset = PermissionCategory.objects.all()
    serializer_class = PermissionCategorySerializer
    ordering = ['order', 'name']


class PermissionCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a permission category
    """
    queryset = PermissionCategory.objects.all()
    serializer_class = PermissionCategorySerializer


class CustomPermissionListCreateView(generics.ListCreateAPIView):
    """
    List all custom permissions or create a new one
    
    GET /api/custom-permissions/ - List custom permissions
    POST /api/custom-permissions/ - Create new custom permission
    """
    queryset = CustomPermission.objects.all()
    serializer_class = CustomPermissionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_active', 'is_system_permission', 'category']
    search_fields = ['name', 'codename', 'description']


class CustomPermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a custom permission
    """
    queryset = CustomPermission.objects.all()
    serializer_class = CustomPermissionSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """
    Get current user profile
    
    GET /api/users/profile/ - Get current user details
    """
    serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'status': 200,
        'message': 'User profile retrieved successfully',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_permissions(request):
    """
    Get current user permissions
    
    GET /api/users/permissions/ - Get all permissions for current user
    """
    user = request.user
    permissions = user.get_all_permissions()
    
    # Group permissions by category/app
    grouped_permissions = {}
    for perm in permissions:
        app_label = perm.split('.')[0] if '.' in perm else 'general'
        if app_label not in grouped_permissions:
            grouped_permissions[app_label] = []
        grouped_permissions[app_label].append(perm)
    
    return Response({
        'success': True,
        'status': 200,
        'message': 'User permissions retrieved successfully',
        'data': {
            'user': user.login_id,
            'permissions': permissions,
            'grouped_permissions': grouped_permissions,
            'roles': [ur.role.name for ur in user.user_roles.filter(is_active=True)]
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics
    
    GET /api/dashboard/stats/ - Get user and role statistics
    """
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_roles': Role.objects.count(),
        'active_roles': Role.objects.filter(is_active=True).count(),
        'total_permissions': Permission.objects.count(),
        'custom_permissions': CustomPermission.objects.filter(is_active=True).count(),
        'user_types': {
            choice[0]: User.objects.filter(user_type=choice[0]).count()
            for choice in User.USER_TYPES
        }
    }
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_role_assignment(request):
    """
    Bulk assign/revoke roles
    
    POST /api/roles/bulk-assign/
    Body: {
        "user_ids": ["uuid1", "uuid2"],
        "role_id": "role_uuid",
        "action": "assign|revoke",
        "reason": "optional reason"
    }
    """
    user_ids = request.data.get('user_ids', [])
    role_id = request.data.get('role_id')
    action = request.data.get('action')
    reason = request.data.get('reason', '')
    
    if not user_ids or not role_id or not action:
        return Response(
            {'error': 'user_ids, role_id, and action are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        role = Role.objects.get(id=role_id, is_active=True)
        users = User.objects.filter(id__in=user_ids, is_active=True)
        
        results = []
        for user in users:
            if action == 'assign':
                user_role, created = user.assign_role(
                    role=role,
                    assigned_by=request.user,
                    assignment_reason=reason
                )
                results.append({
                    'user': user.login_id,
                    'action': 'assigned',
                    'created': created
                })
            elif action == 'revoke':
                count = user.revoke_role(role=role, revoked_by=request.user, reason=reason)
                results.append({
                    'user': user.login_id,
                    'action': 'revoked',
                    'count': count
                })
        
        return Response({'results': results}, status=status.HTTP_200_OK)
    
    except Role.DoesNotExist:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Authentication Views

class LoginView(APIView):
    """
    User login with JWT token generation for all user types (user/admin/staff)
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Login with login_id/password and get JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['login_id', 'password'],
            properties={
                'login_id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User login ID or email'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User password'
                ),
                'remember_me': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='Enable lifetime login (extends refresh token)',
                    default=False
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "message": "Login successful",
                        "user": {
                            "id": "uuid",
                            "login_id": "admin001",
                            "email": "admin@example.com",
                            "name": "Admin User",
                            "user_type": "admin",
                            "roles": [],
                            "permissions": []
                        },
                        "tokens": {
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "token_type": "Bearer"
                        },
                        "remember_me": False,
                        "expires_at": "2024-01-01T12:00:00Z"
                    }
                }
            ),
            400: openapi.Response(
                description="Login failed",
                examples={
                    "application/json": {
                        "message": "Login failed",
                        "errors": {
                            "non_field_errors": ["Invalid login credentials."]
                        }
                    }
                }
            )
        },
        tags=['Authentication']
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            access_token = serializer.validated_data['access_token']
            refresh_token = serializer.validated_data['refresh_token']
            
            # Serialize user data
            user_serializer = UserLoginResponseSerializer(user)
            
            return Response({
                'success': True,
                'status': 200,
                'message': 'Login successful',
                'data': {
                    'user': user_serializer.data,
                    'tokens': {
                        'access': access_token,
                        'refresh': refresh_token,
                        'token_type': 'Bearer'
                    },
                    'remember_me': user.remember_me,
                    'expires_at': user.token_expires_at.isoformat() if user.token_expires_at else None
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'status': 400,
            'message': 'Login failed',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    """
    Refresh JWT access token using refresh token
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Refresh access token using refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh_token'],
            properties={
                'refresh_token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Valid refresh token'
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description="Token refreshed successfully",
                examples={
                    "application/json": {
                        "message": "Token refreshed successfully",
                        "tokens": {
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "token_type": "Bearer"
                        },
                        "expires_at": "2024-01-01T12:00:00Z"
                    }
                }
            ),
            400: openapi.Response(
                description="Token refresh failed",
                examples={
                    "application/json": {
                        "message": "Token refresh failed",
                        "errors": {
                            "non_field_errors": ["Invalid or expired refresh token."]
                        }
                    }
                }
            )
        },
        tags=['Authentication']
    )
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            access_token = serializer.validated_data['access_token']
            refresh_token = serializer.validated_data['refresh_token']
            
            return Response({
                'success': True,
                'status': 200,
                'message': 'Token refreshed successfully',
                'data': {
                    'tokens': {
                        'access': access_token,
                        'refresh': refresh_token,
                        'token_type': 'Bearer'
                    },
                    'expires_at': user.token_expires_at.isoformat() if user.token_expires_at else None
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'status': 400,
            'message': 'Token refresh failed',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    User logout with token blacklisting
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Logout user and blacklist tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Refresh token to blacklist (optional)'
                ),
                'logout_all_devices': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='Logout from all devices',
                    default=False
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description="Logout successful",
                examples={
                    "application/json": {
                        "message": "Logout successful"
                    }
                }
            )
        },
        tags=['Authentication']
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            return Response({
                'success': True,
                'status': 200,
                'message': 'Logout successful',
                'data': []
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'status': 400,
            'message': 'Logout failed',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class VerifyTokenView(APIView):
    """
    Verify JWT token validity and get user info
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Verify token validity and get user information",
        responses={
            200: openapi.Response(
                description="Token is valid",
                examples={
                    "application/json": {
                        "message": "Token is valid",
                        "user": {
                            "id": "uuid",
                            "login_id": "admin001",
                            "email": "admin@example.com",
                            "name": "Admin User",
                            "user_type": "admin"
                        },
                        "expires_at": "2024-01-01T12:00:00Z"
                    }
                }
            ),
            401: openapi.Response(
                description="Token is invalid or expired",
                examples={
                    "application/json": {
                        "message": "Token is invalid or expired"
                    }
                }
            )
        },
        tags=['Authentication']
    )
    def post(self, request):
        user = request.user
        
        # Check if user's stored token is still valid
        if user.is_token_valid():
            user_serializer = UserLoginResponseSerializer(user)
            return Response({
                'success': True,
                'status': 200,
                'message': 'Token is valid',
                'data': {
                    'user': user_serializer.data,
                    'expires_at': user.token_expires_at.isoformat() if user.token_expires_at else None
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'status': 401,
                'message': 'Token is invalid or expired',
                'error': []
            }, status=status.HTTP_401_UNAUTHORIZED)

        
