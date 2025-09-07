from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import District, Thana
from .serializers import DistrictSerializer, ThanaSerializer, ThanaListSerializer


class DistrictListView(generics.ListAPIView):
    """
    List all districts
    
    GET /api/locations/districts/ - List all districts
    """
    queryset = District.objects.filter(is_active=True)
    serializer_class = DistrictSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'name_bn', 'code']
    ordering_fields = ['name', 'code']
    ordering = ['name']


class ThanaListView(generics.ListAPIView):
    """
    List all thanas with optional district filtering
    
    GET /api/locations/thanas/ - List all thanas
    GET /api/locations/thanas/?district={district_id} - List thanas for specific district
    """
    serializer_class = ThanaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['district']
    search_fields = ['name', 'name_bn', 'code', 'district__name']
    ordering_fields = ['name', 'district__name']
    ordering = ['district__name', 'name']
    
    def get_queryset(self):
        queryset = Thana.objects.filter(is_active=True).select_related('district')
        
        # Filter by district if provided
        district_id = self.request.query_params.get('district')
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        
        return queryset


@api_view(['GET'])
def district_thanas(request, district_id):
    """
    Get all thanas for a specific district
    
    GET /api/locations/districts/{district_id}/thanas/ - Get thanas for district
    """
    try:
        district = District.objects.get(id=district_id, is_active=True)
        thanas = district.thanas.filter(is_active=True)
        serializer = ThanaListSerializer(thanas, many=True)
        
        return Response({
            'district': {
                'id': district.id,
                'name': district.name,
                'name_bn': district.name_bn,
                'code': district.code
            },
            'thanas': serializer.data
        })
    
    except District.DoesNotExist:
        return Response(
            {'error': 'District not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def locations_summary(request):
    """
    Get summary of all locations
    
    GET /api/locations/summary/ - Get districts and thanas count
    """
    districts_count = District.objects.filter(is_active=True).count()
    thanas_count = Thana.objects.filter(is_active=True).count()
    
    return Response({
        'districts_count': districts_count,
        'thanas_count': thanas_count,
        'total_locations': districts_count + thanas_count
    })
