# -*- coding:utf-8 -*-

from django.conf.urls import patterns,include,url
from web.views import *

urlpatterns = patterns('',
                       url(r'^$',WebIndex,name="WebIndex"),
                       url(r'pricing/$',Pricing,name="Pricing"),
                       url(r'pricing/(?P<a>\w+)/$',Pricing,name="Pricing"),
                       url(r'^recall/$',ReCall,name="ReCall"),
                       url(r'^gift/$',gift,name="gift"),
                       url(r'^gift/(?P<s>\w+)/$',gift,name="gift"),
                       url(r'^insureGift/$',insureGift,name="insureGift"),
                       url(r'^checkinsure/$',checkinsure,name="checkinsure"),
                       url(r'^GetGift/(?P<user>\w+)/$',GetGift,name="GetGift"),
                       url(r'^PayLoading/$',PayLoading,name="PayLoading"),
                       url(r'^tzh/$',"bxservice.views.TestZhongHua",name="TestZhongHua")
                       )