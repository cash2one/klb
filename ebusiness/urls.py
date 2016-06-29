# -*- coding:utf-8 -*-

from django.conf.urls import patterns, include, url
from ebusiness.views import *

urlpatterns = patterns('',
                       url(r'^$', initVehicleBaseInfo, name="index"),
                       url(r'^initVehicleBaseInfo/$', initVehicleBaseInfo, name="initVehicleBaseInfo"),
                       url(r'^selectCerList/$', selectCerList, name="selectCerList"),
                       url(r'^initQuotation/$', initQuotation, name="initQuotation"),
                       url(r'^editInfo/$', editInfo, name="editInfo"),
                       url(r'^ConfirmInsure/$', ConfirmInsure, name="ConfirmInsure"),
                       url(r'^auto/$', auto, name="auto"),
                       url(r'^GetVIN/$', GetVIN, name="GetVIN"),
                       url(r'^UserCenter/$', UserCenter, name="UserCenter"),
                       )