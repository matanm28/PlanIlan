from django.db import models

from . import BaseModel


class Location(BaseModel):
    building_name = models.CharField(max_length=80)
    building_number = models.IntegerField(null=True, blank=True)
    class_number = models.IntegerField(null=True, blank=True)
    online = models.BooleanField(default=False)

    class Meta:
        ordering = ['pk']
        unique_together = ['building_name', 'building_number', 'class_number', 'online']
        db_table = 'locations'

    @classmethod
    def create(cls, building_name: str, building_number: int, class_number: int,
               online: bool) -> 'Location':
        location, created = Location.objects.get_or_create(building_name=building_name, building_number=building_number,
                                                           class_number=class_number,
                                                           online=online)
        cls.log_created(location, created)
        return location

    def __str__(self) -> str:
        return f'{self.building_name}, בניין{self.building_number}, כיתה {self.class_number}' if not self.is_zoom_class else "אונליין"

    @property
    def is_zoom_class(self):
        return self.online or self.building_name in ['במודל', 'זום', 'נלמד בזום'] or self.building_number is None
