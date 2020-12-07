from django.db import models


class Location(models.Model):
    building_name = models.CharField(max_length=80)
    building_number = models.IntegerField(null=True)
    class_number = models.IntegerField(null=True)
    online = models.BooleanField(default=False)
