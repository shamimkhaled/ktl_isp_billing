from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.conf import settings
from rest_framework.filters import SearchFilter, OrderingFilter 

from .models import Organizations, BillingSettings, SyncSettings
from .serializers import (
    OrganizationSerializer, 
    BillingSettingsSerializer,
    SyncSettingsSerializer,
    OrganizationUpdateResponseSerializer
)

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from django_filters import rest_framework as filters
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class IsOrganizationAdmin(permissions.BasePermission):
    """
    Custom permission to only allow organization admins to access
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to organization admins
        return request.user.is_superuser or request.user.is_staff
    


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page_size,
            'results': data
        })


class OrganizationFilter(filters.FilterSet):
    created_at = filters.DateTimeFromToRangeFilter()
    organization_type = filters.CharFilter(lookup_expr='exact')
    is_active = filters.BooleanFilter()
    country = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Organizations
        fields = {
            'company_name': ['exact', 'icontains'],
            'company_code': ['exact', 'icontains'],
            'contact_email': ['exact', 'icontains'],
            'created_at': ['gte', 'lte', 'year', 'month'],
            'organization_type': ['exact'],
            'is_active': ['exact'],
            'country': ['exact', 'icontains']
        }

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for organizations with caching and optimized queries
    """
    queryset = Organizations.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrganizationFilter
    search_fields = ['company_name', 'company_code', 'contact_email']
    ordering_fields = ['created_at', 'company_name', 'organization_type']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Optimize queryset with select_related and prefetch_related
        """
        queryset = Organizations.objects.select_related(
            'billing_settings',
            'sync_settings'
        ).prefetch_related(
            Prefetch('billing_settings'),
            Prefetch('sync_settings')
        )
        
        # Cache expensive queries
        cache_key = f'org_queryset_{self.action}'
        cached_queryset = cache.get(cache_key)
        
        if cached_queryset is None:
            cached_queryset = queryset
            cache.set(cache_key, cached_queryset, timeout=300)  # 5 minutes cache
            
        return cached_queryset


    @swagger_auto_schema(
        operation_summary="List organizations",
        operation_description="Get a list of all organizations with pagination and filtering",
        manual_parameters=[
            openapi.Parameter(
                'page', openapi.IN_QUERY, 
                description="Page number", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size', openapi.IN_QUERY,
                description="Number of results per page", type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: OrganizationSerializer(many=True),
            401: "Unauthorized",
            403: "Forbidden"
        },
        tags=['Organizations']
    )
    @method_decorator(cache_page(60*5))  # Cache for 5 minutes
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        """
        Cached list view with pagination
        """
        return super().list(request, *args, **kwargs)


    @swagger_auto_schema(
        operation_description="Create new organization",
        request_body=OrganizationSerializer,
        responses={
            201: openapi.Response(
                description="Created",
                schema=OrganizationSerializer
            ),
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Create organization with nested settings
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Clear relevant caches
        cache.delete('org_queryset_list')  # For list view
        cache.delete('org_queryset_retrieve')  # For detail view    

        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )

    
    
    @swagger_auto_schema(
        operation_description="Update organization",
        request_body=OrganizationSerializer,
        responses={
            200: openapi.Response(
                description="Success",
                schema=OrganizationSerializer
            ),
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found"
        }
    )
    def update(self, request, *args, **kwargs):
        """
        Update organization with cache invalidation
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        
        # Clear relevant caches
        cache.delete('org_queryset_list')
        cache.delete(f'org_queryset_retrieve_{instance.pk}')
    

        
        self.perform_update(serializer)
        return Response(serializer.data)


    @swagger_auto_schema(
        operation_description="Partially update organization",
        request_body=OrganizationSerializer(partial=True),
        responses={
            200: openapi.Response(
                description="Success",
                schema=OrganizationUpdateResponseSerializer
            ),
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found"
        }
    )
    def patch(self, request, *args, **kwargs):
        """
        Partial update with cache invalidation and error handling
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                # Save with transaction to ensure data integrity
                with transaction.atomic():
                    self.perform_update(serializer)

                    # Clear relevant caches
                    cache.delete('org_queryset_list')
                    cache.delete(f'org_queryset_retrieve_{instance.pk}')
                    cache.delete(f'organization_representation_{instance.pk}')
                    cache.delete(f'org_settings_{instance.pk}')


                return Response({
                    'success': True,
                    'status': status.HTTP_200_OK,
                    'message': 'Organization updated successfully',
                    'data': serializer.data
                })
            
            return Response({
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid update data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Organizations.DoesNotExist:
            return Response({
                'success': False,
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'Organization not found',
                'errors': {'detail': 'Organization does not exist'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Error updating organization',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @swagger_auto_schema(
        operation_description="Get organization settings",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'billing_settings': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, read_only=True),
                                'max_manual_grace_days': openapi.Schema(type=openapi.TYPE_INTEGER, default=9),
                                'disable_expiry': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                'default_grace_days': openapi.Schema(type=openapi.TYPE_INTEGER, default=1),
                                'jump_billing': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                                'default_grace_hours': openapi.Schema(type=openapi.TYPE_INTEGER, default=14),
                                'max_inactive_days': openapi.Schema(type=openapi.TYPE_INTEGER, default=3),
                                'delete_permanent_disable_secret_from_mikrotik': openapi.Schema(type=openapi.TYPE_INTEGER, default=1),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, read_only=True),
                                'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, read_only=True),
                            }
                        ),
                        'sync_settings': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, read_only=True),
                                'sync_area_to_mikrotik': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                'sync_address_to_mikrotik': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                'sync_customer_mobile_to_mikrotik': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                'last_sync_status_display': openapi.Schema(type=openapi.TYPE_STRING, read_only=True),
                                'sync_frequency_display': openapi.Schema(type=openapi.TYPE_STRING, read_only=True),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, read_only=True),
                                'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, read_only=True),
                            }
                        ),
                    }
                )
            ),
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['get'])
    @method_decorator(cache_page(60*5))
    def get_settings(self, request, pk=None):
        """
        Get organization settings with caching
        """
        organization = self.get_object()
        cache_key = f'org_settings_{organization.pk}'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            billing_settings = BillingSettingsSerializer(
                organization.billing_settings
            ).data if hasattr(organization, 'billing_settings') else None
            
            sync_settings = SyncSettingsSerializer(
                organization.sync_settings
            ).data if hasattr(organization, 'sync_settings') else None
            
            cached_data = {
                'billing_settings': billing_settings,
                'sync_settings': sync_settings
            }
            cache.set(cache_key, cached_data, timeout=300)
            
        return Response(cached_data)

    def perform_destroy(self, instance):
        """
        Soft delete with cache cleanup
        """
        instance.is_active = False
        instance.save()
        
        # Clear specific cache keys
        cache.delete('org_queryset_list')
        cache.delete(f'org_queryset_retrieve_{instance.pk}')
        cache.delete(f'organization_representation_{instance.pk}')
        cache.delete(f'org_settings_{instance.pk}')