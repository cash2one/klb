# -*- coding:utf-8 -*-

from django.conf.urls import patterns, include, url
from webadmin.views import *

urlpatterns = patterns('',
                       url(r'^$', Index, name="index"),
                       url(r'^Login/$',Login,name="Login"),
                       url(r'^Logout/$',Logout,name="Logout"),
                       url(r'^Analytics/$',Analytics,name="Analytics"),
                       url(r'^Share/$',Share,name="Share"),
                       url(r'^ShareChildren/(?P<code>\w+)/$',ShareChildren,name="ShareChildren"),
                       url(r'^ShareChildren/$',ShareChildren,name="ShareChildren"),
                       )
