from django.db import models


class Region(models.Model):
    def __str__(self):
        return self.name

    id = models.AutoField(
        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
    )
    name = models.CharField(blank=True, max_length=255)
