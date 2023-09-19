from django.contrib.auth.models import User
from django.db import models


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    description = models.TextField(max_length=256, null=True, blank=True)

    def __str__(self):
        return str(self.name)