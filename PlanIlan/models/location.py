from django.db import models

from PlanIlan.models import BaseModel


class Location(BaseModel):
    building_name = models.CharField(max_length=80)
    building_number = models.IntegerField(null=True, blank=True)
    class_number = models.IntegerField(null=True, blank=True)
    online = models.BooleanField(default=False)

    @classmethod
    def create_without_save(cls, building_name: str, building_number: int, class_number: int,
                            online: bool) -> 'Location':
        location, created = Location.objects.get_or_create(building_name=building_name, building_number=building_number,
                                                           class_number=class_number,
                                                           online=online)
        cls.log_created(cls.__name__, location.id, created)
        # todo add logging based on created
        return location
