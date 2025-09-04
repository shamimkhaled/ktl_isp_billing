from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

urlpatterns = [
    # User Management
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/profile/', views.user_profile, name='user-profile'),
    path('users/permissions/', views.user_permissions, name='user-permissions'),
    path('users/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Role Management
    path('roles/', views.RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<uuid:pk>/', views.RoleDetailView.as_view(), name='role-detail'),
    path('roles/assign/', views.RoleAssignmentView.as_view(), name='role-assignment'),
    path('roles/bulk-assign/', views.bulk_role_assignment, name='bulk-role-assignment'),
    
    # User Role Assignments
    path('user-roles/', views.UserRoleListView.as_view(), name='user-role-list'),
    
    # Permissions
    path('permissions/', views.PermissionListView.as_view(), name='permission-list'),
    
    # Groups (Django Groups)
    path('groups/', views.GroupListCreateView.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', views.GroupDetailView.as_view(), name='group-detail'),
    
    # Permission Categories
    path('permission-categories/', views.PermissionCategoryListCreateView.as_view(), name='permission-category-list-create'),
    path('permission-categories/<uuid:pk>/', views.PermissionCategoryDetailView.as_view(), name='permission-category-detail'),
    
    # Custom Permissions
    path('custom-permissions/', views.CustomPermissionListCreateView.as_view(), name='custom-permission-list-create'),
    path('custom-permissions/<uuid:pk>/', views.CustomPermissionDetailView.as_view(), name='custom-permission-detail'),
    
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
]
