from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Repository(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repositories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_private = models.BooleanField(default=False)
    default_branch = models.CharField(max_length=50, default='main')
    created_at = models.DateTimeField(auto_now_add=True)


    #ensure owner/name pair is unique to prevent duplicates
    class Meta:
        unique_together = ('owner', 'name') 

    def __str__(self):
        return f"{self.owner.username}/{self.name}"    

