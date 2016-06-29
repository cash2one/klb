# -*- coding:utf-8 -*-
from django import template
from LYZ.klb_class import *
from bxservice.models import bxcarvin
from bxservice.models import bxcarinfo
import time
from LYZ.settings import WECHAT_APPID, WECHAT_APPSECRET, WECHAT_TOKEN,WECHAT_URL
from wechat_sdk import WechatBasic
import json
register = template.Library()

'''
字符串加密
'''
@register.tag(name="WechatStrCode")
def WechatStrCode(c):
    klb_code = KLBCode()
    if c == "":
        return ""
    else:
        try:
            return klb_code.encode(c)
        except:
            return ""


register.filter(WechatStrCode)

@register.tag(name="WechatStrDeCode")
def WechatStrDeCode(c):
    klb_code = KLBCode()
    if c == "":
        return ""
    else:
        try:
            return klb_code.decode(c)
        except:
            return ""


register.filter(WechatStrDeCode)


@register.tag(name="GetSagin")
def GetSagin(url):
    JSTimestamp = int(time.time())
    JSnoncestr = random.randint(100000, 9999999)
    EnURL = WECHAT_URL+url
    KLBWechatBasic = WechatBasic(token=WECHAT_TOKEN, appid=WECHAT_APPID, appsecret=WECHAT_APPSECRET)
    JScardSign = KLBWechatBasic.generate_jsapi_signature(JSTimestamp, JSnoncestr, EnURL, jsapi_ticket=None)

    JSCode = {
        "appid":WECHAT_APPID,
        "timestamp": JSTimestamp,
        "nonceStr": JSnoncestr,
        "signature": JScardSign

    }

    CodeJSON = json.dumps(JSCode)
    return CodeJSON

register.filter(GetSagin)

@register.tag(name="GetTimeStr")
def GetTimeStr(s):
    import time
    t = int(time.time())
    return t
register.filter(GetTimeStr)


@register.tag(name="GetCarLicenseno")
def GetCarLicenseno(id):
    GetCar = bxcarvin.objects.get(id=id)
    return GetCar.licenseno
register.filter(GetCarLicenseno)
@register.tag(name="GetCarValue")
def GetCarValue(id):
    GetCar = bxcarinfo.objects.get(id=id)
    value = GetCar.value[:4]+"....."
    return value
register.filter(GetCarValue)
@register.tag(name="GetCarownername")
def GetCarownername(id):
    GetCar = bxcarvin.objects.get(id=id)
    value = GetCar.ownername
    return value
register.filter(GetCarownername)
