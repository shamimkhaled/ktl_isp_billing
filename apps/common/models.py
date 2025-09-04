import uuid
from django.db import models
from django.utils import timezone

class TimestampedModel(models.Model):
    """Base model with created_at and updated_at timestamps."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class District(TimestampedModel):
    """District model for Bangladesh administrative divisions."""
    
    name = models.CharField(max_length=100, unique=True)
    name_bn = models.CharField(max_length=100, blank=True, null=True, help_text="Bengali name")
    code = models.CharField(max_length=10, unique=True, help_text="District code")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'districts'
        verbose_name = 'District'
        verbose_name_plural = 'Districts'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Thana(TimestampedModel):
    """Thana/Upazila model for Bangladesh administrative sub-divisions."""
    
    name = models.CharField(max_length=100)
    name_bn = models.CharField(max_length=100, blank=True, null=True, help_text="Bengali name")
    code = models.CharField(max_length=10, help_text="Thana code")
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='thanas')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'thanas'
        verbose_name = 'Thana'
        verbose_name_plural = 'Thanas'
        unique_together = ['name', 'district']
        ordering = ['district__name', 'name']
    
    def __str__(self):
        return f"{self.name}, {self.district.name}"

        