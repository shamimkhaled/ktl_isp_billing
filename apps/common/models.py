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

        