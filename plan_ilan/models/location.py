from django.db import models


class Location(models.Model):
    building_name = models.CharField(max_length=80)
    building_number = models.IntegerField(null=True)
    class_number = models.IntegerField(null=True)
    online = models.BooleanField(default=False)

    @classmethod
    def create(cls, building_name: str, building_number: int, class_number: int, online: bool):
        if len(building_name) < 80:
            location = Location(building_name=building_name, building_number=building_number,
                                class_number=class_number, online=online)
            location.save()
