from django.db import models

# Create your models here.
class BusStops(models.Model):
    stop_name = models.CharField(max_length=200)
    latitude = models.CharField(max_length=25)
    longitude = models.CharField(max_length=25)

    def __str__(self):
        return str(self.stop_name)
