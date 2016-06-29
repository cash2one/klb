# -*- coding:utf-8 -*-

from django.conf.urls import patterns, include, url
from wechat.views import *

urlpatterns = patterns('',
                       url(r'^$', Index, name="index"),
                       url(r'^pricing/$', Pricing, name="Pricing"),
                       url(r'^pricing/(?P<action>\w+)/$', Pricing, name="Pricing"),
                       url(r'^UserCenter/$', UserCenter, name="UserCenter"),
                       url(r'^WechatLogin/$', WechatLogin, name="WechatLogin"),
                       url(r'^GetWechatInfo/$', GetWechatInfo, name="GetWechatInfo"),
                       url(r'^TestUserCenter/$', TestUserCenter, name="TestUserCenter"),
                       url(r'^Recommend/$', Recommend, name="Recommend"),
                       url(r'^GetRecommendList/$', GetRecommendList, name="GetRecommendList"),
                       url(r'^BindUserInfo/$', BindUserInfo, name="BindUserInfo"),
                       url(r'^Share/$', Share, name="Share"),
                       url(r'^CarHistory/$', CarHistory, name="CarHistory"),
                       url(r'^History/$', History, name="History"),
                       url(r'^CreateHistory/$', CreateHistory, name="CreateHistory"),
                       url(r'^CreateOrder/$', CreateOrder, name="CreateOrder"),
                       url(r'^OederDetail/$', OederDetail, name="OederDetail"),
                       )
