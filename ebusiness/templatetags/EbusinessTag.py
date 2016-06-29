# -*- coding:utf-8 -*-
from django import template
from LYZ.klb_class import KLBCode
from bxservice.models import *
from user_agents import parse
from webadmin.models import ebusiness_members, flow_analytics
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()
host = "http://192.168.1.222:8000"

'''
切换样式
'''


@register.tag(name="ShowStyle")
def ShowStyle(str):
    if str == "1":
        return "boxed-container"
    else:
        return ""


register.filter(ShowStyle)


@register.tag(name="ENcode")
def ENcode(s, t=0):
    K = KLBCode()
    try:
        if t == 0:
            return K.encode(str(s))
        else:
            return K.decode(str(s))
    except:
        return ""


register.filter(ENcode)


@register.tag(name="GetBrowser")
def GetBrowser(Agent):
    import re
    user_agent = parse(Agent)
    os = user_agent.os.family
    is_wechat = re.search("MicroMessenger", str(Agent), re.IGNORECASE)

    if is_wechat:
        redata = "wechat"
    elif os == "iOS" or os == "Android":
        redata = os
    else:
        redata = "pc"
    return redata
register.filter(GetBrowser)


@register.tag(name="ReCompany")
def ReCompany(enstr):
    K = KLBCode()
    restr = K.decode(enstr)
    bxgs = ""
    if restr == "zh":
        bxgs = "中华保险"
    if restr == "as":
        bxgs = "安盛保险"
    if restr == "yg":
        bxgs = "阳光保险"
    return bxgs


register.filter(ReCompany)


@register.tag(name="ReLicenseno")
def ReLicenseno(id):
    K = KLBCode()
    Carid = K.decode(id)
    CarInfo = bxcarvin.objects.get(id=Carid)
    return CarInfo.licenseno


register.filter(ReLicenseno)

'''
获取用户二维码
'''


@register.tag(name="GetQrcode")
def GetQrcode(uid):
    from webadmin.models import ebusiness_members
    from django.core.exceptions import ObjectDoesNotExist
    Code = KLBCode()

    if uid:
        try:
            GetUser = ebusiness_members.objects.get(id=uid)
            Url = "%s/ebusiness/initVehicleBaseInfo/?style=1&ShowBanner=1&sn=%s" % (host,str(GetUser.code))
            EnUrl = Code.encode(Url)
            Qrcode = "%s/members/qrcode/?s=%s&a=encode" % (host,str(EnUrl))
            return Qrcode
        except ObjectDoesNotExist:
            return ''

    else:
        return ''


register.filter(GetQrcode)


@register.tag(name="Retime")
def Retime(t):
    import time
    try:
        x = time.localtime(t)
        return time.strftime('%Y-%m-%d %H:%M:%S', x)
    except:
        return ''


register.filter(Retime)

'''
流量统计
'''
@register.tag(name="Analytics")
def Analytics(REQ):
    from datetime import datetime
    user_agent = parse(REQ.META.get('HTTP_USER_AGENT'))
    Code = REQ.GET.get("sn","")
    inurl = REQ.get_full_path()
    os = user_agent.os.family
    browser = user_agent.browser.family
    ip = REQ.META.get('HTTP_X_FORWARDED_FORMETA') and REQ.META.get('HTTP_X_FORWARDED_FORMETA') or REQ.META.get('REMOTE_ADDR')
    indata = {'ip': ip, 'browser': browser, 'os': os}
    try:
        ebusiness = ebusiness_members.objects.get(code=Code)
        isIn = ebusiness.flow_analytics_set.filter(**indata).order_by('-intime')
        ebusiness_flow = ebusiness.flow_analytics_set
    except ObjectDoesNotExist:
        isIn = flow_analytics.objects.filter(**indata).filter(ebusiness=None).order_by('-intime')
        ebusiness_flow = flow_analytics.objects

    if isIn.count() < 1:
        indata.update({"inurl":inurl,"endurl":inurl})
        CreateIn = ebusiness_flow.create(**indata)
        CreateIn.save()
    else:
        oldTime = isIn.values()[0]['intime'].strftime('%Y%m%d')
        newTime = datetime.now().strftime('%Y%m%d')
        if newTime == oldTime:
            oldID = isIn.values()[0]['id']
            UpdataIn = ebusiness_flow.get(id=oldID)
            UpdataIn.num = UpdataIn.num + 1
            UpdataIn.endurl = inurl
            UpdataIn.save()
        else:
            indata.update({"inurl":inurl,"endurl":inurl})
            CreateIn = ebusiness_flow.create(**indata)
            CreateIn.save()
    return ''


register.filter(Analytics)

'''
生成渠道下线推广
'''
@register.tag(name="CreateShareChildren")
def CreateShareChildren(uid,t='link'):
    Code = KLBCode()
    from webadmin.models import ebusiness_members
    try:
        GetUser = ebusiness_members.objects.get(id=uid)
        code = GetUser.code
    except ObjectDoesNotExist:
        code = ""

    if t == "Blink":
        HTTP = '%s/ebusiness/?ShowBanner=1&sn=%s'%(host,code)
        return HTTP

    if t == "link":
        try:
            NewCode = Code.encode(code)
            HTTP = "%s/webadmin/ShareChildren/%s/?HideWizard=1&ShowBanner=1"%(host,NewCode)
        except ValueError:
            HTTP = '%s/ebusiness/?ShowBanner=1'%host
        return HTTP

    if t == 'qrcode':
        try:
            NewCode = Code.encode(code)
            HTTP = "%s/webadmin/ShareChildren/%s/?HideWizard=1&ShowBanner=1"%(host,NewCode)
            EnUrl = Code.encode(HTTP)
            Qrcode = "%s/members/qrcode/?s=%s&a=encode" % (host,str(EnUrl))
            return Qrcode
        except ValueError:
            EnUrl = Code.encode("%s/ebusiness/?ShowBanner=1"%host)
            Qrcode = "%s/members/qrcode/?s=%s&a=encode" % (host,str(EnUrl))
            return Qrcode
register.filter(CreateShareChildren)

'''
生成渠道下线推广
'''
@register.tag(name="EbusinessLink")
def EbusinessLink(uid):
    from webadmin.models import ebusiness_members
    try:
        GetUser = ebusiness_members.objects.get(id=uid)
        Url = "%s/ebusiness/initVehicleBaseInfo/?style=2&sn=%s" % (host,str(GetUser.code))
    except ObjectDoesNotExist:
        Url = "%s/ebusiness/?ShowBanner=1"%host
    return Url
register.filter(EbusinessLink)


'''
判断是否有权限
'''
@register.tag(name="IsAutho")
def IsAutho(uid,t=None):
    try:
        GetUser = ebusiness_members.objects.get(id=uid)
        D = 1
        if t=="ischildren":
            D = GetUser.ischildren
        return D
    except:
        return 1
register.filter(IsAutho)