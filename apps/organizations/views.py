from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Organization
from .serializers import OrganizationSerializer
from apps.common.serializers import SuccessResponseSerializer, ErrorResponseSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsSuperAdminOrAdmin:
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.is_staff  # Assuming is_staff indicates admin

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

class OrganizationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all organizations or create a new one.",
        responses={
            200: openapi.Response('Success', SuccessResponseSerializer(many=True)),
            201: openapi.Response('Created', SuccessResponseSerializer),
            400: openapi.Response('Error', ErrorResponseSerializer),
            403: openapi.Response('Forbidden', ErrorResponseSerializer)
        },
        request_body=OrganizationSerializer,
      
    )
    def post(self, request):
        if not IsSuperAdminOrAdmin().has_permission(request, self):
            raise PermissionDenied(detail="Only superadmin or admin can create organizations.")
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            organization = serializer.save()
            response_data = {
                'success': True,
                'status': status.HTTP_201_CREATED,
                'message': 'Organization created successfully.',
                'data': OrganizationSerializer(organization).data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data = {
            'success': False,
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'Failed to create organization.',
            'error': serializer.errors
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retrieve a list of organizations.",
        responses={
            200: openapi.Response('Success', SuccessResponseSerializer(many=True)),
            403: openapi.Response('Forbidden', ErrorResponseSerializer)
        },
      
    )
    def get(self, request):
        if not request.user.is_authenticated:
            raise PermissionDenied(detail="Authentication required to view organizations.")
        organizations = Organization.objects.all()
        serializer = OrganizationSerializer(organizations, many=True)
        response_data = {
            'success': True,
            'status': status.HTTP_200_OK,
            'message': 'Organizations retrieved successfully.',
            'data': serializer.data
        }
        return Response(response_data)



class OrganizationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a specific organization by ID.",
        responses={
            200: openapi.Response('Success', SuccessResponseSerializer),
            404: openapi.Response('Error', ErrorResponseSerializer),
            403: openapi.Response('Forbidden', ErrorResponseSerializer)
        },
      
    )
    def get(self, request, pk):
        if not request.user.is_authenticated:
            raise PermissionDenied(detail="Authentication required to view organization.")
        try:
            organization = Organization.objects.get(pk=pk)
            serializer = OrganizationSerializer(organization)
            response_data = {
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'Organization retrieved successfully.',
                'data': serializer.data
            }
            return Response(response_data)
        except Organization.DoesNotExist:
            response_data = {
                'success': False,
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'Organization not found.',
                'error': {}
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)



    @swagger_auto_schema(
        operation_description="Update a specific organization by ID.",
        responses={
            200: openapi.Response('Success', SuccessResponseSerializer),
            400: openapi.Response('Error', ErrorResponseSerializer),
            404: openapi.Response('Error', ErrorResponseSerializer),
            403: openapi.Response('Forbidden', ErrorResponseSerializer)
        },
        request_body=OrganizationSerializer,
      
    )
    def put(self, request, pk):
        if not IsSuperAdminOrAdmin().has_permission(request, self):
            raise PermissionDenied(detail="Only superadmin or admin can update organizations.")
        try:
            organization = Organization.objects.get(pk=pk)
            serializer = OrganizationSerializer(organization, data=request.data, partial=True)
            if serializer.is_valid():
                updated_organization = serializer.save()
                response_data = {
                    'success': True,
                    'status': status.HTTP_200_OK,
                    'message': 'Organization updated successfully.',
                    'data': OrganizationSerializer(updated_organization).data
                }
                return Response(response_data)
            response_data = {
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Failed to update organization.',
                'error': serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Organization.DoesNotExist:
            response_data = {
                'success': False,
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'Organization not found.',
                'error': {}
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


    @swagger_auto_schema(
        operation_description="Delete a specific organization by ID.",
        responses={
            204: openapi.Response('Success', SuccessResponseSerializer),
            404: openapi.Response('Error', ErrorResponseSerializer),
            403: openapi.Response('Forbidden', ErrorResponseSerializer)
        },
      
    )

    def delete(self, request, pk):
        if not IsSuperAdminOrAdmin().has_permission(request, self):
            raise PermissionDenied(detail="Only superadmin or admin can delete organizations.")
        try:
            organization = Organization.objects.get(pk=pk)
            organization.delete()
            response_data = {
                'success': True,
                'status': status.HTTP_204_NO_CONTENT,
                'message': 'Organization deleted successfully.',
                'data': {}
            }
            return Response(response_data, status=status.HTTP_204_NO_CONTENT)
        except Organization.DoesNotExist:
            response_data = {
                'success': False,
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'Organization not found.',
                'error': {}
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
