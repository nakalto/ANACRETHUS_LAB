from django.db import models
from django.contrib.auth.models import User
from repos.models import Repository 


# Create your models here.
#branch models to represent git branches 
class Branch(models.Model):
    #link branch to a repository 
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='branches')
    #branch name (e.g "main", "dev", feature-x)
    name = models.CharField(max_length=100)
    #owner of the branch(repository owner or contributer)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='branches')
    #Timestamp when branch was created 
    created_at = models.DateField(auto_now_add=True)

    #Ensure branch names are unique per repository 
    class Meta:
        unique_together = ('repo', 'name')

    #human-readable representation 
    def __str__(self):
        return f"{self.repo.name}:{self.name}"    