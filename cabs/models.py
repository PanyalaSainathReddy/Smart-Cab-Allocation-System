from django.db import models
from registration.models import User

class Cab(models.Model):
    number_plate = models.CharField(max_length=20)
    cab_latitude = models.CharField(max_length=100, default=0)
    cab_longitude = models.CharField(max_length=100, default=0)


class Driver(models.Model):
    name = models.CharField(max_length=100)
    cab = models.OneToOneField(Cab, on_delete=models.CASCADE)


class Ride(models.Model):
    cab = models.ForeignKey(Cab, on_delete=models.CASCADE)
    rider = models.ForeignKey(User, on_delete=models.CASCADE)
    start_latitude = models.CharField(max_length=100, default=0)
    start_longitude = models.CharField(max_length=100, default=0)
    end_latitude = models.CharField(max_length=100, default=0)
    end_longitude = models.CharField(max_length=100, default=0)
