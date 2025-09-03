import uuid
from django.db import models
from django.utils import timezone
from apps.common.models import TimestampedModel

class Organization(TimestampedModel):
    company_name = models.CharField(max_length=255, default='Kloud Technologies Ltd')
    company_code = models.CharField(max_length=20, unique=True, default='KTL')
    business_license = models.CharField(max_length=100, blank=True, null=True)
    vat_registration = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    logo_img = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    dark_logo_img = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    lite_logo_img = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    banner_img = models.ImageField(upload_to='organization_banners/', blank=True, null=True)
    og_image = models.ImageField(upload_to='organization_og_images/', blank=True, null=True)
    
    # SEO fields for dynamic configuration
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)
    
    # Payment and document fields
    organization_type = models.CharField(max_length=50, default='Banking')
    nid_document = models.FileField(upload_to='organization_documents/', blank=True, null=True)
    payment_report = models.FileField(upload_to='organization_documents/', blank=True, null=True)
    invoice_signature = models.ImageField(upload_to='organization_signatures/', blank=True, null=True)
    card_logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    
    # Revenue Sharing Configuration
    revenue_sharing_enabled = models.BooleanField(default=True)
    default_reseller_share = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    default_sub_reseller_share = models.DecimalField(max_digits=5, decimal_places=2, default=45.00)
    default_ktl_share_with_sub = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    default_reseller_share_with_sub = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    
    # API Version Handling (dynamic per organization)
    api_version = models.CharField(max_length=10, default='v1.0', help_text='Dynamic API version for this organization')
    
    auto_approval_enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    def __str__(self):
        return f"{self.company_name} ({self.company_code})"

class BillingSettings(TimestampedModel):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='billing_settings')
    max_manual_grace_days = models.IntegerField(default=9)
    disable_expiry = models.BooleanField(default=False)
    default_grace_days = models.IntegerField(default=1)
    jump_billing = models.BooleanField(default=True)
    default_grace_hours = models.IntegerField(default=14)
    max_inactive_days = models.IntegerField(default=3)
    delete_permanent_disable_secret_from_mikrotik = models.IntegerField(default=1)  # 0 for immediate delete

    class Meta:
        verbose_name = 'Billing Settings'
        verbose_name_plural = 'Billing Settings'

    def __str__(self):
        return f"Billing Settings for {self.organization.company_name}"

class SyncSettings(TimestampedModel):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='sync_settings')
    sync_area_to_mikrotik = models.BooleanField(default=False)
    sync_address_to_mikrotik = models.BooleanField(default=False)
    sync_customer_mobile_to_mikrotik = models.BooleanField(default=False)
    # telegram_bot_token = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Sync Settings'
        verbose_name_plural = 'Sync Settings'

    def __str__(self):
        return f"Sync Settings for {self.organization.company_name}"
    

    