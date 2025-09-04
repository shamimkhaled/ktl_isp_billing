from rest_framework import serializers
from .models import District, Thana


class SuccessResponseSerializer(serializers.Serializer):
    """Serializer for standard success response"""
    
    success = serializers.BooleanField(default=True)
    status = serializers.CharField()
    message = serializers.CharField()
    data = serializers.JSONField(required=False, allow_null=True)
class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for standard error response"""
    
    success = serializers.BooleanField(default=False)
    status = serializers.CharField()
    message = serializers.CharField()
    error = serializers.JSONField(required=False, allow_null=True)


class DistrictSerializer(serializers.ModelSerializer):
    """Serializer for District model"""
    
    thanas_count = serializers.SerializerMethodField()
    
    class Meta:
        model = District
        fields = ['id', 'name', 'name_bn', 'code', 'is_active', 'thanas_count']
        read_only_fields = ['id']
    
    def get_thanas_count(self, obj):
        """Get count of active thanas in this district"""
        return obj.thanas.filter(is_active=True).count()


class ThanaSerializer(serializers.ModelSerializer):
    """Serializer for Thana model"""
    
    district_name = serializers.CharField(source='district.name', read_only=True)
    district_code = serializers.CharField(source='district.code', read_only=True)
    
    class Meta:
        model = Thana
        fields = ['id', 'name', 'name_bn', 'code', 'district', 'district_name', 'district_code', 'is_active']
        read_only_fields = ['id', 'district_name', 'district_code']


class ThanaListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Thana listing"""
    
    class Meta:
        model = Thana
        fields = ['id', 'name', 'name_bn', 'code']
