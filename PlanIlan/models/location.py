from django.db import models

from PlanIlan.models import BaseModel


class Location(BaseModel):
    building_name = models.CharField(max_length=80)
    building_number = models.IntegerField(null=True)
    class_number = models.IntegerField(null=True)
    online = models.BooleanField(default=False)

    @classmethod
    def create(cls, building_name: str, building_number: int, class_number: int, online: bool = False) -> 'Location':
        if building_name == 'נלמד בזום':
            online = True
            class_number = None
        return Location(building_name=building_name, building_number=building_number, class_number=class_number,
                        online=online)
