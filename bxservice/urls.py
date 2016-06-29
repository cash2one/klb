# -*- coding:utf-8 -*-

from django.conf.urls import patterns,include,url
from bxservice.ZhongHuaViews import *
from bxservice.views import *
urlpatterns = patterns('',
                       url(r'^PriceList/$',PriceList,name="PriceList"),
                       url(r'^zh/$',ZhongHuaIndex,name="ZhongHuaIndex"),
                       url(r'^getvin/$',GetVIN,name="GetVIN"),
                       url(r'^createvin/$',CerateCarVin,name="CerateCarVin"),
                       url('^VINIsSet/$',VINIsSet,name="VINIsSet"),
                       url('^ConfirmTouBao/$',ConfirmTouBao,name="ConfirmTouBao"),
                       url('^IsReadCallback/$',IsReadCallback,name="IsReadCallback"),
                       url('^GetRead/$',GetRead,name="GetRead"),
                       url('^GetCallBack/$',GetCallBack,name="GetCallBack"),
                       url('^ConfirmFeiLv/$',ConfirmFeiLv,name="ConfirmFeiLv"),

                       )