from rest_framework import serializers
from django.core.cache import cache
from .models import Organizations, BillingSettings, SyncSettings



class BillingSettingsSerializer(serializers.ModelSerializer):
    """Serializer for billing settings with caching"""
    
    class Meta:
        model = BillingSettings
        exclude = ['organization']
        read_only_fields = ['id']
    
    def validate(self, attrs):
        """Validate billing settings with early returns"""
        default_grace = attrs.get('default_grace_days', 1)
        max_grace = attrs.get('max_manual_grace_days', 9)
        
        if default_grace > max_grace:
            raise serializers.ValidationError({
                "default_grace_days": "Cannot exceed maximum manual grace days"
            })
        return attrs


class SyncSettingsSerializer(serializers.ModelSerializer):
    """Serializer for sync settings with optimized field loading"""
    
    last_sync_status_display = serializers.SerializerMethodField()
    sync_frequency_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SyncSettings
        # exclude = ['organization']
        fields = [
            'id', 'sync_area_to_mikrotik', 'sync_address_to_mikrotik',
            'sync_customer_mobile_to_mikrotik', 'last_sync_status_display',
            'sync_frequency_display']
        read_only_fields = [
            'id', 
            # 'last_sync_at', 'last_sync_status', 'last_sync_message'
        ]
    
    def get_last_sync_status_display(self, obj):
        """Cached method for sync status display"""
        cache_key = f'sync_status_display_{obj.pk}'
        cached_value = cache.get(cache_key)
        if cached_value is None:
            cached_value = obj.get_last_sync_status_display()
            cache.set(cache_key, cached_value, timeout=3600)
        return cached_value

    def get_sync_frequency_display(self, obj):
        """Cached method for frequency display"""
        cache_key = f'sync_frequency_display_{obj.pk}'
        cached_value = cache.get(cache_key)
        if cached_value is None:
            cached_value = obj.get_sync_frequency_display()
            cache.set(cache_key, cached_value, timeout=3600)
        return cached_value


class OrganizationSerializer(serializers.ModelSerializer):
    """Optimized serializer for Organizations with selective loading"""
    
    billing_settings = BillingSettingsSerializer(required=False)
    sync_settings = SyncSettingsSerializer(required=False)
    
    class Meta:
        model = Organizations
        fields = [
            'id', 'company_name', 'company_code', 'business_license',
            'vat_registration', 'address', 'contact_email', 'contact_phone',
            'website', 'logo_img', 'dark_logo_img', 'lite_logo_img',
            'banner_img', 'og_image', 'favicon', 'seo_title',
            'seo_description', 'seo_keywords', 'meta_description', 'slug',
            'organization_type', 'nid_document', 'payment_report',
            'invoice_signature', 'card_logo', 'country', 'org_timezone',
            'currency', 'revenue_sharing_enabled', 'default_reseller_share',
            'default_sub_reseller_share', 'default_ktl_share_with_sub',
            'default_reseller_share_with_sub', 'api_version',
            'auto_approval_enabled', 'customer_id_prefix', 'tax_rate',
            'vat_rate', 'email_notifications_enabled',
            'sms_notifications_enabled', 'push_notifications_enabled',
            'is_active', 'created_at', 'updated_at',
            'billing_settings', 'sync_settings'
            
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        """Optimized validation with early returns"""
        if not attrs.get('revenue_sharing_enabled'):
            return attrs

        shares = {
            'reseller': attrs.get('default_reseller_share', 0),
            'sub_reseller': attrs.get('default_sub_reseller_share', 0),
            'ktl': attrs.get('default_ktl_share_with_sub', 0),
            'reseller_with_sub': attrs.get('default_reseller_share_with_sub', 0)
        }

        if not (0 <= shares['reseller'] <= 100):
            raise serializers.ValidationError({
                "default_reseller_share": "Must be between 0 and 100"
            })

        total_share = shares['ktl'] + shares['reseller_with_sub'] + shares['sub_reseller']
        if total_share != 100:
            raise serializers.ValidationError({
                "share_distribution": "Total shares must equal 100%"
            })

        return attrs

    def create(self, validated_data):
        """Optimized bulk creation with transaction"""
        from django.db import transaction
        
        billing_data = validated_data.pop('billing_settings', None)
        sync_data = validated_data.pop('sync_settings', None)
        
        with transaction.atomic():
            organization = Organizations.objects.create(**validated_data)
            
            if billing_data:
                BillingSettings.objects.create(
                    organization=organization, 
                    **billing_data
                )
            
            if sync_data:
                SyncSettings.objects.create(
                    organization=organization, 
                    **sync_data
                )
            
        return organization

    def update(self, instance, validated_data):
        """Optimized bulk update with transaction and cache invalidation"""
        from django.db import transaction
        
        billing_data = validated_data.pop('billing_settings', None)
        sync_data = validated_data.pop('sync_settings', None)
        
        with transaction.atomic():
            # Update main instance
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Bulk update related settings
            if billing_data and instance.billing_settings:
                BillingSettings.objects.filter(organization=instance).update(**billing_data)
            
            if sync_data and instance.sync_settings:
                SyncSettings.objects.filter(organization=instance).update(**sync_data)
                # Invalidate related caches
                cache.delete_many([
                    f'sync_status_display_{instance.sync_settings.pk}',
                    f'sync_frequency_display_{instance.sync_settings.pk}'
                ])
        
        return instance

    def to_representation(self, instance):
        """Cached representation with select_related optimization"""
        cache_key = f'organization_representation_{instance.pk}'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            # Optimize query with select_related
            instance = Organizations.objects.select_related(
                'billing_settings', 
                'sync_settings'
            ).get(pk=instance.pk)
            
            data = super().to_representation(instance)
            data['customer_id_prefix_code'] = instance.customer_id_prefix_code
            
            cache.set(cache_key, data, timeout=3600)
            return data
            
        return cached_data



class OrganizationUpdateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    status = serializers.IntegerField()
    message = serializers.CharField()
    data = OrganizationSerializer()


