from django.db import models
import uuid
from django.utils import timezone

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=255, default='Kloud Technologies Ltd')
    company_code = models.CharField(max_length=20, unique=True, default='KTL')
    business_license = models.CharField(max_length=100, blank=True, null=True)
    vat_registration = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    logo_img = models.CharField(max_length=500, blank=True, null=True)
    revenue_sharing_enabled = models.BooleanField(default=True)
    default_reseller_share = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    default_sub_reseller_share = models.DecimalField(max_digits=5, decimal_places=2, default=45.00)
    auto_approval_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        # db_table = 'Organization'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    def __str__(self):
        return f"{self.company_name} ({self.company_code})"
      

   