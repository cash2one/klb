# -*- coding:utf-8 -*-
from django.shortcuts import *
from LYZ.common import *
from LYZ.klb_class import *
from klbapp.appclass import *
from bxservice.models import *
from bxservice.common import *

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from urllib import unquote
import urllib, urllib2


# 网站首页
def WebIndex(request):
    return render_to_response('web/index-1.html', {}, context_instance=RequestContext(request))


# 汽车召回
def ReCall(request):
    db = {}
    MC = MyCarClass()
    if request.user.is_authenticated():
        Log = MC.ReCallLog(uid=request.user.id)
    else:
        Log = ""

    if request.method == "POST":

        if not request.user.is_authenticated():
            return HttpResponseRedirect("/members/login/?next=/web/recall/")
        vin = request.REQUEST.get("vin", "")
        year = request.REQUEST.get("year", "")
        if vin == "" or year == "":
            db.update({"Error": "VIN和发动机号不能为空"})
        else:
            ReCall = MC.ReCall(vin=vin, year=year, uid=request.user.id)
            db.update({"ReCall": ReCall})
    print(Log)
    db.update({"Log": Log})
    return render_to_response('web/recall.html', db, context_instance=RequestContext(request))


def gift(request, s=None):
    if s == "recommend":
        return render_to_response('web/recommend.html', {}, context_instance=RequestContext(request))

    else:
        return render_to_response('web/gift.html', {}, context_instance=RequestContext(request))


def GetGift(request, user):
    return render_to_response('web/h5_gift.html', {}, context_instance=RequestContext(request))


# 投保有礼
def insureGift(request):
    return render_to_response('web/insureGift.html', {}, context_instance=RequestContext(request))


# 保单验证
def checkinsure(request):
    return render_to_response('web/checkinsure.html', {}, context_instance=RequestContext(request))


# 保险比价
def Pricing(request, a="1"):
    if a == "1":
        return render_to_response('web/pricing.html', {}, context_instance=RequestContext(request))
    elif a == "2":
        return render_to_response('web/step2.html', {}, context_instance=RequestContext(request))
    elif a == "3":
        return render_to_response('web/step3.html', {}, context_instance=RequestContext(request))
    elif a == "4":
        # 初始化加密解密类
        db = {}
        ENCODE = FengChaoCrypt()
        DBAction = BXDBAction()
        id = request.REQUEST.get("id", "")
        if id == "" or id == None:
            # 车牌号
            licenseNo = ENCODE.AESdecrypt(request.REQUEST.get("licenseno", ""))
            # 车主姓名
            ownerName = ENCODE.AESdecrypt(str(request.REQUEST.get("ownername", "")))
            # 手机号码
            mobilePhone = request.REQUEST.get("mobilephone", "")
            # 城市
            cityCode = ENCODE.AESdecrypt(request.REQUEST.get("citycode", ""))
            vin = request.REQUEST.get("vin", "")
            # 发动机号
            engine = request.REQUEST.get("engine", "")
            # 如果用户直接通过系统获取到VIN和发动机号，action＝"a"用户手动输入action则为b
            action = request.REQUEST.get("a", "")
            # 这三个是用户选择的阳光的车型信息
            key = unquote(request.REQUEST.get("key", ""))
            vehicleFgwCode = unquote(request.REQUEST.get("vehiclefgwcode", ""))
            carvalue = unquote(request.REQUEST.get("value", ""))

            user_id = request.user.is_authenticated() and request.user.id or False

            if action == "a":
                vin = ENCODE.AESdecrypt(vin)
                engine = ENCODE.AESdecrypt(engine)
            '''
            将信息保存数据库
            包括车牌号车主姓名，发动机号什么的，反正是投保需要的东东
            '''
            if bxcarvin.objects.filter(vin=vin, engine=engine).count() < 1:
                kwargs = {
                    "licenseno": licenseNo,
                    "ownername": ownerName,
                    "citycode": cityCode,
                    "vin": vin,
                    "engine": engine,
                    "user_id": user_id
                }

                CarID = DBAction.CreateCarVin(**kwargs)
                '''
                将阳光返回的车型存入数据库
                '''
                kwargs = {
                    'user_id': user_id,
                    "car_id": CarID,
                    "key": key,
                    "vehiclefgwcode": vehicleFgwCode,
                    "value": carvalue,
                    "bxtype": "sinosig",
                }

                InfoID = DBAction.CreateCarInfo(**kwargs)



        else:
            CarIn = DBAction.IsSet(id=id)
            CarCon = DBAction.ReCarInfo(cid=id)
            licenseNo = CarIn.licenseno
            ownerName = CarIn.ownername
            vin = CarIn.vin
        db = {"vin": ENCODE.AESencrypt(vin), "licenseNo": ENCODE.AESencrypt(licenseNo.encode("utf-8")),
              "ownerName": ENCODE.AESencrypt(ownerName.encode("utf-8"))}
        return render_to_response('web/step4.html', db, context_instance=RequestContext(request))
    elif a == "5":
        bxgs = request.REQUEST.get("bx", "")
        vinEncode = request.REQUEST.get("key", "")
        DBAction = BXDBAction()
        PayInfo = DBAction.SelectPayInfo(vin=vinEncode)
        ENCODE = FengChaoCrypt()
        revin = ENCODE.AESdecrypt(vinEncode)
        db = {"PayInfo": PayInfo}
        if bxgs == "zh":
            db.update({"bxgs":"zh","openwin": "1","orderNo":PayInfo['order_id'],"businessCode":PayInfo['businesscode'],"vin":revin})

        else:
            db.update({"bxgs":"as","openwin": "","vin":revin})


        return render_to_response('web/pay.html', db, context_instance=RequestContext(request))

    else:
        return render_to_response('web/pricing.html', {}, context_instance=RequestContext(request))


def PayLoading(request):

    orderNo =request.REQUEST.get("orderNo","")
    if orderNo=="" or orderNo ==None:
        return HttpResponseRedirect("/web/pricing/1/")
    if request.method=="POST":
        DBAction = BXDBAction()
        KLBJSON = PrintJson()
        GetOrder = DBAction.OrderIDStatus(orderid=orderNo)
        print(GetOrder)
        if GetOrder:
            if GetOrder == "1":
                url="http://220.171.28.152:9080/nsp/payment/payment.do?orderNo="+orderNo

                J = KLBJSON.echo(msg="数据返回", error=0, url=url,data={})
            else:
                J = KLBJSON.echo(msg="数据返回", error=0, url="",data={})
        else:
            J = KLBJSON.echo(msg="没有找到订单", error=1, url="",data={})
        return HttpResponse(J, content_type="application/json")

    else:
        db = {"orderNo":orderNo}
        print(db)
        return render_to_response('web/payloading.html', db, context_instance=RequestContext(request))

