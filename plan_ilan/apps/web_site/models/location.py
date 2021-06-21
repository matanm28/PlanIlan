from threading import Lock

from django.db import models

from plan_ilan.utils.decorators import static_vars
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
        location, created = Location.objects.get_or_create(building_name=building_name,
                                                           building_number=building_number,
                                                           class_number=class_number,
                                                           online=online)
        cls.log_created(location, created)
        return location

    @classmethod
    @static_vars(mutex=Lock())
    def create_thread_safe(cls, building_name: str, building_number: int, class_number: int,
                           online: bool) -> 'Location':
        try:
            cls.create_thread_safe.mutex.acquire()
            return cls.create(building_name, building_number, class_number, online)
        finally:
            cls.create_thread_safe.mutex.release()

    def __str__(self) -> str:
        return f'{self.building_name}, בניין {self.building_number}, כיתה {self.class_number}' if not self.is_zoom_class else "אונליין"

    @property
    def is_zoom_class(self):
        return self.online or self.building_name in ['במודל', 'זום', 'נלמד בזום'] or self.building_number is None
