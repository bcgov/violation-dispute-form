from django.contrib.postgres.fields import JSONField
from django.db import models

class Location(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(blank=True, max_length=255, unique=True)
    region = models.ForeignKey('Region', on_delete=models.SET_NULL, related_name='region_location', blank=True, null=True)