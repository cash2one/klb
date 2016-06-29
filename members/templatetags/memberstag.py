# -*- coding:utf-8 -*-
from django import template
from members.models import recomcode,photo,wechat
from django.contrib.auth.models import User
import time,urllib,json,sys,httplib,urllib2,random
from LYZ.klb_class import *
from django.core.exceptions import ObjectDoesNotExist
register = template.Library()

'''
读取网站基本信息
'''

@register.tag(name="TuiJianLink")
def TuiJianLink(uid, h):
    klb_code = KLBCode()
    try:
        Code = recomcode.objects.get(user_id=uid)
        Ncode = Code.code
        Nurl = Code.dwz
    except ObjectDoesNotExist:
        C = random.randint(100000,999999)
        In = recomcode(user_id=uid,code=C)
        In.save()

        Ncode = str(C)
        Nurl = In.dwz

    if  Nurl<>"" and Nurl<>None:
        return Nurl

    Curl = "http://" + h + "/members/reg/?u=" + klb_code.encode(Ncode)
    para = {
        "url": Curl,
    }
    postData = urllib.urlencode(para)
    req = urllib2.Request("http://dwz.cn/create.php", postData)
    resp = urllib2.urlopen(req).read()
    M = json.loads(resp)
    print(resp)
    Is = recomcode.objects.get(user_id=uid)
    if Is.dwz=="" or Is.dwz==None:
        Is.dwz = M['tinyurl']
        Is.save()
    return M['tinyurl']
register.filter(TuiJianLink)

'''
推荐码解密
'''
@register.tag(name="DeTuiJianCode")
def DeTuiJianCode(c):
    klb_code = KLBCode()
    if c=="":
        return ""
    else:
        try:
            return klb_code.decode(c)
        except:
            return ""

register.filter(DeTuiJianCode)
'''
显示推荐码
'''
@register.tag(name="GetTuijianCode")
def GetTuijianCode(uid):
    try:
        Code = recomcode.objects.get(user_id=uid)
        Ncode = Code.code
        return Ncode
    except ObjectDoesNotExist:
        C = random.randint(100000,999999)
        In = recomcode(user_id=uid,code=C)
        In.save()
        return C

register.filter(GetTuijianCode)

@register.tag(name="UserThumb")
def UserThumb(uid):
    try:
        wechatimg = wechat.objects.filter(user_id=uid)
        ImgObj = photo.objects.filter(user_id=uid,image_class=0)
        Is_Img = ImgObj.exists()
        if Is_Img:
            return "/media/"+ImgObj.order_by("-id").values()[0]['thumbnail']
        if wechatimg.exists():
            return wechatimg.values()[0]['headimgurl']
        else:
            return "/static/images/user_portrait.jpg"
    except ObjectDoesNotExist:
        return "/static/images/user_portrait.jpg"
register.filter(UserThumb)

