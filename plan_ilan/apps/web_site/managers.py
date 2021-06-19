from django.db import models


class CounterManger(models.Manager):
    def __init__(self, counted_field: str):
        self.counted_field = counted_field
        super().__init__()

    @property
    def with_count(self):
        count_field_name = f'{self.counted_field}_count'
        return self.annotate(**{count_field_name: models.Count(self.counted_field)})
