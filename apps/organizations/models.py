import uuid
from django.db import models
from django.utils import timezone
from apps.common.models import TimestampedModel
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.cache import cache

class OrganizationManager(models.Manager):
    """Custom manager for Organization model with performance optimizations"""
    
    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related(
            'billing_settings', 'sync_settings'
        )
    
    def active(self):
        """Get active organizations"""
        return self.filter(is_active=True)
    
    def with_settings(self):
        """Get organizations with their settings"""
        return self.select_related('billing_settings', 'sync_settings')

class Organizations(TimestampedModel):
    company_name = models.CharField(max_length=255, default='Kloud Technologies Ltd')
    company_code = models.CharField(max_length=20, unique=True, default='KTL', db_index=True)

    business_license = models.CharField(max_length=100, blank=True, null=True)
    vat_registration = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)

    website = models.CharField(max_length=255, blank=True, null=True)

   

    # Media Files
    logo_img = models.ImageField(
        upload_to='organization_logos/', 
        blank=True, 
        null=True,
        help_text='Main organization logo'
    )
    dark_logo_img = models.ImageField(
        upload_to='organization_logos/', 
        blank=True, 
        null=True,
        help_text='Dark theme logo'
    )
    lite_logo_img = models.ImageField(
        upload_to='organization_logos/', 
        blank=True, 
        null=True,
        help_text='Light theme logo'
    )
    banner_img = models.ImageField(
        upload_to='organization_banners/', 
        blank=True, 
        null=True,
        help_text='Banner image for portal'
    )
    og_image = models.ImageField(
        upload_to='organization_og_images/', 
        blank=True, 
        null=True,
        help_text='Open Graph image for social sharing'
    )
    favicon = models.ImageField(
        upload_to='organization_favicons/', 
        blank=True, 
        null=True,
        help_text='Website favicon'
    )
    
    # SEO fields for dynamic configuration
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    # Payment and document fields
    organization_type = models.CharField(max_length=50, default='ISP')  # e.g., ISP, Banking, etc.
    nid_document = models.FileField(upload_to='organization_documents/', blank=True, null=True)
    payment_report = models.FileField(upload_to='organization_documents/', blank=True, null=True)
    invoice_signature = models.ImageField(upload_to='organization_signatures/', blank=True, null=True)
    card_logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    
    # Geographic Information
    country = models.CharField(max_length=100, default='Bangladesh', db_index=True)
    org_timezone = models.CharField(max_length=50, default='Asia/Dhaka')
    currency = models.CharField(max_length=10, default='BDT')

    # Revenue Sharing Configuration
    revenue_sharing_enabled = models.BooleanField(default=True)
    default_reseller_share = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    default_sub_reseller_share = models.DecimalField(max_digits=5, decimal_places=2, default=45.00)
    default_ktl_share_with_sub = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    default_reseller_share_with_sub = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    
    # API Version Handling (dynamic per organization)
    api_version = models.CharField(max_length=10, default='v1.0', help_text='Dynamic API version for this organization')
    
    # Customer Management Settings
    auto_approval_enabled = models.BooleanField(
        default=False,
        help_text='Auto-approve new customer registrations'
    )
    customer_id_prefix = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Custom prefix for customer IDs (default: company_code)'
    )


    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Default tax rate percentage'
    )
    vat_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='VAT rate percentage'
    )


    # Notification Settings
    email_notifications_enabled = models.BooleanField(default=True)
    sms_notifications_enabled = models.BooleanField(default=True)
    push_notifications_enabled = models.BooleanField(default=False)

    is_active = models.BooleanField(
        default=True, 
        db_index=True,
        help_text='Organization active status'
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    objects = OrganizationManager()
    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        indexes = [
            models.Index(fields=['company_code', 'is_active']),
            models.Index(fields=['organization_type', 'is_active']),
            models.Index(fields=['created_at', 'is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(default_reseller_share__gte=0) & models.Q(default_reseller_share__lte=100),
                name='valid_reseller_share'
            ),
            # models.CheckConstraint(
            #     check=models.Q(max_users__gt=0),
            #     name='positive_max_users'
            # )
        ]

    def __str__(self):
        return f"{self.company_name} ({self.company_code})"
    
    def save(self, *args, **kwargs):
        """Override save to handle slug generation and cache invalidation"""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.company_name)
        
        super().save(*args, **kwargs)
        
        # Invalidate related caches
        cache.delete(f'org_settings_{self.id}')
        cache.delete(f'org_config_{self.company_code}')
    
    @property
    def customer_id_prefix_code(self):
        """Get the prefix code for customer ID generation"""
        return self.customer_id_prefix or self.company_code
    
    def calculate_commission_split(self, amount, customer_type, has_sub_reseller=False):
        """Calculate commission split based on customer type"""
        if customer_type == 'ktl_direct':
            return {'organization': amount}
        
        elif customer_type == 'reseller':
            if has_sub_reseller:
                org_share = amount * (self.default_ktl_share_with_sub / 100)
                reseller_share = amount * (self.default_reseller_share_with_sub / 100)
                sub_reseller_share = amount - org_share - reseller_share
                return {
                    'organization': org_share,
                    'reseller': reseller_share,
                    'sub_reseller': sub_reseller_share
                }
            else:
                reseller_share = amount * (self.default_reseller_share / 100)
                org_share = amount - reseller_share
                return {
                    'organization': org_share,
                    'reseller': reseller_share
                }
        
        # elif customer_type == 'corporate':
        #     commission = amount * (self.corporate_commission_rate / 100)
        #     org_share = amount - commission
        #     return {
        #         'organization': org_share,
        #         'commission': commission
        #     }
        
        return {'organization': amount}
    
    



class BillingSettings(TimestampedModel):
    organization = models.OneToOneField(Organizations, on_delete=models.CASCADE, related_name='billing_settings')
    # Grace Period Configuration
    max_manual_grace_days = models.IntegerField(
        default=9,
        help_text='Maximum manual grace days allowed'
    )
    disable_expiry = models.BooleanField(
        default=False,
        help_text='Disable automatic account expiry'
    )

    default_grace_days = models.IntegerField(
        default=1,
        help_text='Default grace period in days'
    )
    jump_billing = models.BooleanField(
        default=True,
        help_text='Enable jump billing for overdue accounts'
    )
   
    default_grace_hours = models.IntegerField(
        default=14,
        help_text='Default grace period in hours for hourly plans'
    )
    max_inactive_days = models.IntegerField(
        default=3,
        help_text='Maximum inactive days before account is disabled')
    
    delete_permanent_disable_secret_from_mikrotik = models.IntegerField(
        default=1,
        help_text='Days before permanent disable is triggered'
    )  # 0 for immediate delete

    class Meta:
        verbose_name = 'Billing Settings'
        verbose_name_plural = 'Billing Settings'
        db_table = 'billing_settings'
        # db_index = ['id']

    def __str__(self):
        return f"Billing Settings for {self.organization.company_name}"

class SyncSettings(TimestampedModel):
    organization = models.OneToOneField(Organizations, on_delete=models.CASCADE, related_name='sync_settings')
    
    # MikroTik Sync Settings
    sync_area_to_mikrotik = models.BooleanField(
        default=False,
        help_text='Sync area information to MikroTik'
    )
    sync_address_to_mikrotik = models.BooleanField(
        default=False,
        help_text='Sync customer address to MikroTik'
    )
    sync_customer_mobile_to_mikrotik = models.BooleanField(
        default=False,
        help_text='Sync customer mobile number to MikroTik'
    )
    # telegram_bot_token = models.CharField(max_length=255, blank=True, null=True)
    SYNC_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    )

    SYNC_FREQUENCY_CHOICES = (
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    )

    last_sync_status = models.CharField(
        max_length=20,
        choices=SYNC_STATUS_CHOICES,
        default='pending'
    )
    sync_frequency = models.CharField(
        max_length=20,
        choices=SYNC_FREQUENCY_CHOICES,
        default='daily'
    )
    class Meta:
        verbose_name = 'Sync Settings'
        verbose_name_plural = 'Sync Settings'
        db_table = 'sync_settings'
        # db_index = ['id']

    def __str__(self):
        return f"Sync Settings for {self.organization.company_name}"
    

    