# -*- coding:utf-8 -*-

from django.conf.urls import patterns, include, url
from ClientAdmin.views import *

urlpatterns = patterns('',
                       url(r'^$', Index, name="index"),
                       url(r'^Index/$', Index, name="index"),
                       url(r'^AddUser/$', AddUser, name="AddUser"),
                       url(r'^Logout/$', Logout, name="Logout"),
                       )
