from django.contrib.postgres.fields import JSONField
from django.db import models

class Region(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(blank=True, max_length=255)
