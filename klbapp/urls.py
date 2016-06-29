# -*- coding:utf-8 -*-

from django.conf.urls import patterns,include,url
from klbapp.views import *


urlpatterns = patterns('',
                       url(r'^$',Index,name="index"),
                       url(r'^sendmsg/$',SendMsg,name="sendmsg"),
                       url(r'^register/$',Register,name="Register"),
                       url(r'^login/$',Login,name="Login"),
                       url(r'^imgupload/$',ImgUpload,name='ImgUpload'),
                       url(r'^test/$',test),
                       )