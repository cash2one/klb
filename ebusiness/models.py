# -*- coding:utf-8 -*-
from django.db import models

class vin_as_car_yg(models.Model):
    vehicleFgwCode = models.CharField(max_length=255,default="",blank=True,null="")
    value = models.CharField(max_length=255,default="",blank=True,null="")
    key = models.CharField(max_length=255,default="",blank=True,null="")
    vin = models.CharField(max_length=255,default="",blank=True,null="")


class code(models.Model):
    pass
