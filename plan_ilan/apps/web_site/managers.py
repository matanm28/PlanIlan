from django.db import models


class CounterManger(models.Manager):
    def __init__(self, counted_field: str = None):
        super().__init__()
        self.counted_field = counted_field

    @property
    def with_count(self):
        assert self.counted_field is not None, "To access 'with_count' property a counted field must be defined " \
                                               "when initializing this Manger object"
        count_field_name = f'{self.counted_field}_count'
        return self.annotate(**{count_field_name: models.Count(self.counted_field)})
