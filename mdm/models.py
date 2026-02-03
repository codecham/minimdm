import uuid
from django.db import models
from django.contrib.auth.models import User


class Fleet(models.Model):
    """
    A Fleet groups Devices together.
    
    Each Fleet belongs to a single User (owner) and has a unique name
    per owner (two Fleets owned by the same User cannot have the same name).
    """
    
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='fleets'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'owner'],
                name='unique_fleet_name_per_owner'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

    
class Device(models.Model):
    """
    A Device belongs to a Fleet and is identified by its serial number.
    
    Devices can optionally have an OS version.
    """
    
    serial_number = models.UUIDField(default=uuid.uuid4, unique=True)
    fleet = models.ForeignKey(
        Fleet,
        on_delete=models.CASCADE,
        related_name='devices'
    )
    os_version = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.serial_number)