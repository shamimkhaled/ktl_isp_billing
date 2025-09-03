from rest_framework import serializers
from .models import Organization, BillingSettings, SyncSettings

class BillingSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingSettings
        fields = '__all__'
        read_only_fields = ('id', 'organization', 'created_at', 'updated_at')

class SyncSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncSettings
        fields = '__all__'
        read_only_fields = ('id', 'organization', 'created_at', 'updated_at')

class OrganizationSerializer(serializers.ModelSerializer):
    billing_settings = BillingSettingsSerializer()
    sync_settings = SyncSettingsSerializer()

    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        billing_data = validated_data.pop('billing_settings', {})
        sync_data = validated_data.pop('sync_settings', {})
        organization = Organization.objects.create(**validated_data)
        BillingSettings.objects.create(organization=organization, **billing_data)
        SyncSettings.objects.create(organization=organization, **sync_data)
        return organization

    def update(self, instance, validated_data):
        billing_data = validated_data.pop('billing_settings', {})
        sync_data = validated_data.pop('sync_settings', {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        billing = instance.billing_settings
        for attr, value in billing_data.items():
            setattr(billing, attr, value)
        billing.save()

        sync = instance.sync_settings
        for attr, value in sync_data.items():
            setattr(sync, attr, value)
        sync.save()

        return instance

