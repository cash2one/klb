# -*- coding:utf-8 -*-

from django.conf.urls import patterns,include,url
from members.views import *

urlpatterns = patterns('',
                       url(r'^$',Index,name="index"),
                       url(r'^login/$',Login,name="login"),
                       url(r'login/wechat/$',WechatLogin,name="WechatLogin"),
                       url(r'^reg/$',Reg,name="reg"),
                       url(r'^logout/$',Logout_View,name="logout"),
                       url(r'^order_details/$',OrderDetails,name="order_details"),
                       url(r'^order_details/(?P<t>\w+)/$', OrderDetails),
                       url(r'^setting/$', Setting),
                       url(r'^setting/(?P<action>\w+)/$', Setting),
                       url(r'^help/$',Help,name="help"),
                       url(r'^getvcode/$',GetVcode,name="getvcode"),
                       url(r'^validcode/$',ValidCode,name="validcode"),
                       url(r'^qrcode/$', GenerateQrcode, name='qrcode'),
                       url(r'^imgupload/$', ImgUpload, name='ImgUpload'),
                       url(r'^updatetovip/$', UpDateToVip, name='UpDateToVip'),#升级VIP
                       url(r'^mycar/$', MyCar, name='MyCar'),#我的车
                       url(r'^recall/$', CarRecall, name='CarRecall'),#我的车
                       url(r'^tjcode/$', TuiJianMa, name='TuiJianMa'),
                       url(r'^pay/$', pay, name='pay'),#支付
                       url(r'^payResult/$', payResult, name='payResult'),#支付
                       url(r'^NotifyURL/$', NotifyURL, name='NotifyURL'),#支付
                       url(r'^GetPayMD5Info/$', GetPayMD5Info, name='GetPayMD5Info'),#返回md5加密
                       )