from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    #link each profile to a single user account 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Optional display name to show UI
    display_name = models.CharField(max_length=120, blank=True)

    #short bio field for user description
    bio = models.TextField(blank=True)


    def __str__(self):
        #display name if set, else fallback to username
        return self.display_name or self.user.username
    


