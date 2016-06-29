# -*- coding:utf-8 -*-
from django.shortcuts import *
import time, urllib, re, json
from wechat_sdk import WechatBasic
from LYZ.settings import WECHAT_APPID, WECHAT_APPSECRET, WECHAT_TOKEN, WECHAT_URL
from bxservice.models import bxcarvin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from bxservice.common import *
from members.models import *
from LYZ.klb_class import *
from WechatCommon import *
from members.models import recommend_log
import random
import time
import datetime
from bxservice.models import bxzhpriceinfo

def Pricing(request, action="1"):
    Code = KLBCode()
    openid = request.REQUEST.get("openid", "")
    # ReWechat = _GetWechatInfo(req=request)

    # if ReWechat=="" or len(ReWechat)<1:
    #     return HttpResponsePermanentRedirect("http://web.kalaibao.com/wechat/WechatLogin/?action=Pricing&time=%s"%time.time())
    db = {"t": time.time()}
    KLBWechatBasic = WechatBasic(token=WECHAT_TOKEN, appid=WECHAT_APPID, appsecret=WECHAT_APPSECRET)

    JSURL = WECHAT_URL + request.get_full_path()
    JSTimestamp = int(time.time())
    JSnoncestr = random.randint(100000, 9999999)

    JScardSign = KLBWechatBasic.generate_jsapi_signature(JSTimestamp, JSnoncestr, JSURL, jsapi_ticket=None)

    JSCode = {

        "timestamp": JSTimestamp,
        "nonceStr": JSnoncestr,
        "signature": JScardSign

    }
    JSCode.update({"appId": WECHAT_APPID, "openid": openid})
    db.update(JSCode)
    # db.update(ReWechat)

    #判断是否能拿到openID
    try:
        openid = Code.decode(openid)
        WechatUserInfo = wechat.objects.get(openid=openid)
        RecommendURL = "%s/wechat/WechatLogin/?action=Recommend&toid=%s" % (WECHAT_URL, WechatUserInfo.id)
    except:
        RecommendURL = "%s/wechat/WechatLogin/?action=Pricing&toid=" % (WECHAT_URL)
    ID = ['9','16','41','53','60','76','17']
    try:
        i = random.randint(0,len(ID))
        CarIN = bxcarvin.objects.get(id=ID[i])
    except:
        CarIN = bxcarvin.objects.get(id=ID[0])
    db.update({"CarInfo":CarIN})
    db.update({"RecommendURL":RecommendURL})
    if action == "1":
        return render_to_response('wechat/pricing.html', db, context_instance=RequestContext(request))
    if action == "2":
        return render_to_response('wechat/CarInfo.html', db, context_instance=RequestContext(request))
    if action == "3":
        return render_to_response('wechat/showList.html', db, context_instance=RequestContext(request))
    if action == "4":
        return render_to_response('wechat/detail.html', db, context_instance=RequestContext(request))
    if action == "5":
        DBAction = BXDBAction()
        ENCODE = FengChaoCrypt()

        id = request.REQUEST.get("id", "")
        key = request.REQUEST.get("key", "")
        bxgs = request.REQUEST.get("bxgs", "")
        CarInfo = {}

        if id <> "" and id <> None:
            try:
                CarInfo = bxcarvin.objects.get(id=id)
            except:
                CarInfo = {}
        if key <> "" and key <> None:
            try:
                vin = ENCODE.AESdecrypt(key)
                CarInfo = bxcarvin.objects.get(vin=vin)
            except:
                vin = key
                CarInfo = bxcarvin.objects.get(vin=vin)
        PayInfo = DBAction.SelectPayInfo(vin=ENCODE.AESencrypt(CarInfo.vin))
        print(CarInfo.vin)
        db = {"CarInfo": CarInfo, "bxgs": bxgs, "PayInfo": PayInfo}
        return render_to_response('wechat/UserInfo.html', db, context_instance=RequestContext(request))

    if action == "6":
        return render_to_response('wechat/Bxgsweb.html', db, context_instance=RequestContext(request))
    if action == '7':
        DBAction = BXDBAction()
        ENCODE = FengChaoCrypt()

        id = request.REQUEST.get("id", "")
        key = request.REQUEST.get("key", "")
        bxgs = request.REQUEST.get("bxgs", "")
        CarInfo = {}

        if id <> "" and id <> None:
            try:
                CarInfo = bxcarvin.objects.get(id=id)
            except:
                CarInfo = {}
        if key <> "" and key <> None:
            try:
                vin = ENCODE.AESdecrypt(key)
                CarInfo = bxcarvin.objects.get(vin=vin)
            except:
                vin = key
                CarInfo = bxcarvin.objects.get(vin=vin)
        PayInfo = DBAction.SelectPayInfo(vin=ENCODE.AESencrypt(CarInfo.vin))
        db = {"CarInfo": CarInfo, "bxgs": bxgs, "PayInfo": PayInfo}
        return render_to_response("wechat/FuDongBiz.html",db,context_instance=RequestContext(request))
    if action == '8':
        DBAction = BXDBAction()
        ENCODE = FengChaoCrypt()

        id = request.REQUEST.get("id", "")
        key = request.REQUEST.get("key", "")
        bxgs = request.REQUEST.get("bxgs", "")
        CarInfo = {}

        if id <> "" and id <> None:
            try:
                CarInfo = bxcarvin.objects.get(id=id)
            except:
                CarInfo = {}
        if key <> "" and key <> None:
            try:
                vin = ENCODE.AESdecrypt(key)
                CarInfo = bxcarvin.objects.get(vin=vin)
            except:
                vin = key
                CarInfo = bxcarvin.objects.get(vin=vin)
        PayInfo = DBAction.SelectPayInfo(vin=ENCODE.AESencrypt(CarInfo.vin))
        db = {"CarInfo": CarInfo, "bxgs": bxgs, "PayInfo": PayInfo}
        return render_to_response("wechat/FuDongforce.html",db,context_instance=RequestContext(request))
    else:
        return render_to_response('wechat/pricing.html', db, context_instance=RequestContext(request))


# 验证信息
def Index(request):
    signature = request.REQUEST.get("signature", "")
    timestamp = request.REQUEST.get("timestamp", "")
    nonce = request.REQUEST.get("nonce", "")
    echostr = request.REQUEST.get("echostr", "")
    KLBWechatBasic = WechatBasic(token=WECHAT_TOKEN, appid=WECHAT_APPID, appsecret=WECHAT_APPSECRET)
    IsOK = KLBWechatBasic.check_signature(signature, timestamp, nonce)
    if IsOK:
        return HttpResponse(echostr)
    else:
        return HttpResponse("")


# 个人中心
def UserCenter(request):
    Code = KLBCode()
    openid = request.REQUEST.get("openid", "")
    try:
        openidIn = Code.decode(openid)
        WechatUserInfo = wechat.objects.get(openid=openidIn)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("%s/wechat/WechatLogin/" % WECHAT_URL)

    else:
        SignURL ="/wechat/UserCenter/?openid=" + openid
        JSSign = _GetSagin(SignURL)
        UserInfo = User.objects.get(id=WechatUserInfo.user_id)
        try:
            OrderInfo = user_order.objects.filter(userid=WechatUserInfo.user_id).all()
        except:
            OrderInfo ={}
        RecommendList = recommend_log.objects.filter(to_open_id=openidIn).order_by("-id")
        RecommendURL = "%s/wechat/WechatLogin/?action=Recommend&toid=%s" % (WECHAT_URL, WechatUserInfo.id)
        db = {"WechatUserInfo": WechatUserInfo, "openid": openid, "RecommendURL": RecommendURL, "sign": JSSign,
              "RecommendList": RecommendList, 'UserInfo': UserInfo,"OrderInfo":OrderInfo}
        return render_to_response('wechat/UserCenter.html', db, context_instance=RequestContext(request))


# 微信登录
def WechatLogin(request):
    Action = request.REQUEST.get("action", "")
    toid = request.REQUEST.get("toid", "")

    ActionURL = ""
    if Action == "Pricing":
        ActionURL = WECHAT_URL + "/wechat/GetWechatInfo/?action=Pricing"
    elif Action == "Recommend":
        ActionURL = WECHAT_URL + "/wechat/GetWechatInfo/?action=Recommend&toid=%s" % toid
    elif Action == "ebusiness":
        EbItms = dict(request.REQUEST.items())
        EbItms.update({"action":"ebusiness"})
        EbItmsCode = urllib.urlencode(EbItms)
        ActionURL = WECHAT_URL + "/wechat/GetWechatInfo/?"+EbItmsCode
    else:
        ActionURL = WECHAT_URL + "/wechat/GetWechatInfo/?action=usercenter"
    LoginPam = urllib.urlencode({"redirect_uri": ActionURL})

    LoginURL = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&%s&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect" % (
        WECHAT_APPID, LoginPam)

    # LoginURL = "https://open.weixin.qq.com/connect/oauth2/authorize?%s#wechat_redirect"%LoginPam
    return HttpResponseRedirect(LoginURL)


def TestUserCenter(request):
    db = {}
    return render_to_response('wechat/UserCenter.html', db, context_instance=RequestContext(request))


def GetWechatInfo(req):
    WechatCode = req.REQUEST.get("code", "")
    WechatState = req.REQUEST.get("state", "")
    action = req.REQUEST.get("action", "")
    toid = req.REQUEST.get("toid", "")
    # "/ebusiness/editInfo/?car={{ id|ENcode }}&company={{ 'zh'|ENcode }}&style={{ style }}&sn={{ sn }}"
    OA = KLBOAuth()
    Code = KLBCode()
    '''
    渠道微信浏览器打开，登录
    '''
    EbItms = dict(req.REQUEST.items())
    EbItms.update({"action":"ebusiness"})
    EbItmsCode = urllib.urlencode(EbItms)

    if WechatCode == "" or WechatCode == None:
        if action == "Pricing":
            return HttpResponsePermanentRedirect("%s/wechat/pricing/1/?openid=" % WECHAT_URL)
        if action == "Recommend":
            return HttpResponsePermanentRedirect("%s/wechat/Recommend/?toid=%s&FromOpenId=" % (WECHAT_URL, toid))
        if action == "ebusiness":

            return HttpResponsePermanentRedirect("/ebusiness/editInfo/?"+EbItmsCode)
        if action == "usercenter":
            return HttpResponsePermanentRedirect(WECHAT_URL + "/wechat/UserCenter/?openid=")
        else:
            return HttpResponsePermanentRedirect(WECHAT_URL + "/wechat/UserCenter/?openid=")
    else:
        AccessTokenPam = urllib.urlencode({
            'appid': WECHAT_APPID,
            'secret': WECHAT_APPSECRET,
            "code": WechatCode,
            "grant_type": "authorization_code"

        })
        try:
            GetAccessTokenURL = "https://api.weixin.qq.com/sns/oauth2/access_token?%s" % AccessTokenPam
            AccessTokenJson = urllib.urlopen(GetAccessTokenURL).read()
            AccessTokenArray = json.loads(AccessTokenJson)
            access_token = AccessTokenArray['access_token']
            openid = AccessTokenArray['openid']

            Params = urllib.urlencode({'access_token': access_token, 'openid': openid})
            UserInfoUrl = "https://api.weixin.qq.com/sns/userinfo?%s" % (Params)
            UserInfoJson = urllib.urlopen(UserInfoUrl).read()
            UserInfoArray = json.loads(UserInfoJson)
        except:
            if action == "Pricing":
                return HttpResponsePermanentRedirect(WECHAT_URL + "/wechat/pricing/1/?openid=")
            if action == "usercenter":
                return HttpResponsePermanentRedirect(WECHAT_URL + "/wechat/UserCenter/?openid=")
            if action == "Recommend":
                return HttpResponsePermanentRedirect(WECHAT_URL + "/wechat/Recommend/?toid=%s&FromOpenId=" % toid)
            if action == "ebusiness":
                return HttpResponsePermanentRedirect("/ebusiness/editInfo/?"+EbItmsCode)
            else:
                return HttpResponsePermanentRedirect(WECHAT_URL + "/wechat/UserCenter/?openid=")

        try:
            GetUser = wechat.objects.get(openid=openid)
            UserID = GetUser.id


        except ObjectDoesNotExist:
            UserID = OA.CreateUser_Wechat(
                request=req,
                openid=openid,
                nickname=UserInfoArray['nickname'],
                sex=UserInfoArray['sex'],
                language=UserInfoArray['language'],
                city=UserInfoArray['city'],
                country=UserInfoArray['country'],
                province=UserInfoArray['province'],
                headimgurl=UserInfoArray['headimgurl'],
                unionid="",
                wechat=False,
                reopenid=True

            )
        opid = Code.encode(openid)
        fromid = UserID
        if action == "Pricing":
            return HttpResponsePermanentRedirect(
                WECHAT_URL + "/wechat/pricing/1/?openid=%s&t=%s" % (opid, str(time.time())))
        if action == "usercenter":
            return HttpResponsePermanentRedirect(
                WECHAT_URL + "/wechat/UserCenter/?openid=%s" % (opid))
        if action == "Recommend":
            return HttpResponsePermanentRedirect(
                WECHAT_URL + "/wechat/Recommend/?toid=%s&FromOpenId=%s&fromid=%s&t=%s" % (
                toid, opid, fromid, str(time.time())))
        if action == "ebusiness":
            GetUserOne = wechat.objects.get(id=UserID)
            UserInfo = User.objects.get(id=GetUserOne.user_id)
            user = authenticate(username=UserInfo.username,password="klb@weixin")
            login(req, user)
            return HttpResponsePermanentRedirect("/ebusiness/editInfo/?"+EbItmsCode)
        else:
            return HttpResponsePermanentRedirect(WECHAT_URL + "/wechat/UserCenter/?openid=%s" % (opid))


def Recommend(request):
    #
    Code = KLBCode()
    FromOpenId = request.REQUEST.get("FromOpenId", "")
    fromid = request.REQUEST.get("fromid", "")
    toid = request.REQUEST.get("toid", "")
    FromOpenIdIn = Code.decode(FromOpenId)
    IsSetRecom = recommend_log.objects.filter(from_open_id=FromOpenIdIn, fromopenid_id=fromid)
    if IsSetRecom.count() > 0:
        IsSetRecom.delete()

    ToUserInfo = wechat.objects.get(id=toid)
    ToUserInfo.recommend_log_set.get_or_create(from_open_id=FromOpenIdIn, to_open_id=ToUserInfo.openid,
                                               fromopenid_id=fromid)
    ToUserInfo.recommend_log_set.select_for_update()
    return HttpResponsePermanentRedirect(WECHAT_URL + "/wechat/Share/?openid=%s&toid=%s" % (FromOpenId, toid))


def GetRecommendList(request):
    openid = request.REQUEST.get("openid", "")
    RecommendList = recommend_log.objects.filter(to_open_id=openid).order_by("-id")
    if RecommendList.count() > 0:
        NewArr = []
        RecommendListArray = RecommendList.values()
        for i in range(len(RecommendListArray)):
            ForID = RecommendListArray[i]['fromopenid_id']
            ForUserInfo = wechat.objects.get(id=ForID)
            Ninfo = {
                "openid": ForUserInfo.id,
                "nickname": ForUserInfo.nickname,
                "headimgurl": ForUserInfo.headimgurl,
                "addtime": RecommendListArray[i]['addtime'].strftime("%Y-%m-%d %H:%I:%S")
            }
            NewArr.append(Ninfo)

        ToJSON = json.dumps(NewArr)
        return HttpResponse(ToJSON, content_type="application/json")
    else:
        return HttpResponse('{}', content_type="application/json")


def _GetSagin(url):
    JSTimestamp = int(time.time())
    JSnoncestr = random.randint(100000, 9999999)
    EnURL = WECHAT_URL + url
    KLBWechatBasic = WechatBasic(token=WECHAT_TOKEN, appid=WECHAT_APPID, appsecret=WECHAT_APPSECRET)
    JScardSign = KLBWechatBasic.generate_jsapi_signature(JSTimestamp, JSnoncestr, EnURL, jsapi_ticket=None)

    JSCode = {
        "appid": WECHAT_APPID,
        "timestamp": JSTimestamp,
        "nonceStr": JSnoncestr,
        "signature": JScardSign

    }
    return JSCode


def BindUserInfo(request):
    username = request.REQUEST.get("username", "")
    nickname = request.REQUEST.get("nickname", "")
    sex = request.REQUEST.get("sex", "")
    email = request.REQUEST.get("email", "")
    password = request.REQUEST.get("password", "")
    phone = request.REQUEST.get("phone", "")
    addr = request.REQUEST.get("addr", "")
    idcard = request.REQUEST.get("idcard", "")
    userid = request.REQUEST.get("userid", "")
    try:
        userid = int(userid)
    except:
        J = {"error": "1", "msg": "未找到该用户，设置失败!"}
        J_JSON = json.dumps(J)
        return HttpResponse(J_JSON, content_type="application/json")
    try:
        UserInfo = User.objects.get(id=userid)
        UserInfo.real_name = username
        UserInfo.nick_name = nickname
        UserInfo.sex = sex
        UserInfo.idcard = idcard
        UserInfo.addr = addr
        UserInfo.email = email
        UserInfo.phone = phone
        # UserInfo.set_password(password)
        UserInfo.save()
        J = {"error": "0", "msg": "绑定成功!"}
        J_JSON = json.dumps(J)
    except ObjectDoesNotExist:
        J = {"error": "1", "msg": "未找到该用户，设置失败!"}
        J_JSON = json.dumps(J)
    return HttpResponse(J_JSON, content_type="application/json")


def Share(request):
    openid = request.REQUEST.get("openid", "")
    toid = request.REQUEST.get("toid", "")
    Dict = {"action_name": "QR_LIMIT_STR_SCENE", "action_info": {"scene": {"scene_str": "123"}}}
    KLBWechatBasic = WechatBasic(token=WECHAT_TOKEN, appid=WECHAT_APPID, appsecret=WECHAT_APPSECRET)
    MyQrcode = KLBWechatBasic.create_qrcode(Dict)
    QrecodeURL = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s"%(MyQrcode['ticket'])
    db={"QrecodeURL":QrecodeURL,"openid":openid,"toid":toid}
    return render_to_response('wechat/share.html', db, context_instance=RequestContext(request))


def History(request):
    hisid = request.REQUEST.get('hisid','')
    PricingHistory = pricing_history.objects.filter(history_id=hisid).all()
    db = {'PricingHistory':PricingHistory}
    return render_to_response('wechat/pricing_history.html', db, context_instance=RequestContext(request))


def CarHistory(request):
    openid = request.REQUEST.get('openid','')
    Code = KLBCode()
    OpenidDecode = Code.decode(openid)
    WechatUserInfo = wechat.objects.get(openid=OpenidDecode)
    carinfo = WechatUserInfo.user.car_history_set.all()
    db={"carinfo":carinfo}
    return render_to_response('wechat/UserCenter_car_history.html', db, context_instance=RequestContext(request))


# 建立报价历史

def CreateHistory(request):
    JSON = PrintJson()
    Code = KLBCode()
    openid = request.REQUEST.get("openid", "")
    licenseno = request.REQUEST.get("licenseno", "")
    bxgs = request.REQUEST.get("bxgs", "")
    sanzhe = request.REQUEST.get('SanZhe','')
    chesun = request.REQUEST.get("VehicleLoss", "")
    daoqiang = request.REQUEST.get("DaoQiang", "")
    siji = request.REQUEST.get("ZeRenSJ", "")
    chengke = request.REQUEST.get("ZeRenCK", "")
    boli = request.REQUEST.get("BoLiPS", "")
    huahen = request.REQUEST.get("HuaHen", "")
    ziran = request.REQUEST.get("ZiRan", "")
    fadongji = request.REQUEST.get("SheShui", "")
    chesun_bj = request.REQUEST.get("BUJiCS", "")
    sanzhe_bj = request.REQUEST.get("BuJiSZ", "")
    daoqiang_bj = request.REQUEST.get("BuJiDQ", "")
    siji_bj = request.REQUEST.get("BuJiSJ", "")
    chengke_bj = request.REQUEST.get("BuJiCK", "")
    jiaoqiang = request.REQUEST.get("forcePre", "")
    chechuan = request.REQUEST.get("VehTaxPremium", "")
    zongji = request.REQUEST.get("TotalPremium", "")
    ID = request.REQUEST.get("CarId","")
    # 获取carid
    CarId = False
    try:
        Car = bxcarvin.objects.get(id=ID)
        CarId = Car.id
    except ObjectDoesNotExist:
        CarId = False
    if not CarId:
        J = JSON.echo(msg="没有查询到车辆信息", error=1)
        return HttpResponse(J, content_type="application/json")
    # 获取用户id
    try:
        OpenidDecode = Code.decode(openid)
        WechatUser = wechat.objects.get(openid=OpenidDecode)
        userID = WechatUser.user_id
    except:
        userID = False
    if not userID:
        J = JSON.echo(msg="没有找到该用户", error=1)
        return HttpResponse(J, content_type="application/json")
    CarList = car_history.objects.filter(user_id=userID, car_id=CarId)
    if CarList.count() < 1:
        CrerteCarHistory = car_history.objects.create(user_id=userID, car_id=CarId)
        CrerteCarHistory.save()
        CreatIn = CrerteCarHistory.pricing_history_set.create(
            car_id=CarId,
            user_id=userID,
            bxgs=bxgs,
            sanzhe=sanzhe,
            chesun=chesun,
            daoqiang=daoqiang,
            siji=siji,
            chengke=chengke,
            boli=boli,
            huahen=huahen,
            ziran=ziran,
            fadongji=fadongji,
            chesun_bj=chesun_bj,
            sanzhe_bj=sanzhe_bj,
            daoqiang_bj=daoqiang_bj,
            siji_bj=siji_bj,
            chengke_bj=chengke_bj,
            jiaoqiang=jiaoqiang,
            chechuan=chechuan,
            zongji=zongji
        )

        CreatIn.save()
    else:
        HisID = CarList.values()[0]['id']
        
        CrerteCarHistoryArr = pricing_history.objects.filter(user_id=userID, car_id=CarId,bxgs=bxgs)
        if CrerteCarHistoryArr.count()>0:
            CrerteCarHistoryArr.update(
                # car_id=CarId,
                # user_id=userID,
                bxgs=bxgs,
                chesun=chesun,
                daoqiang=daoqiang,
                siji=siji,
                sanzhe=sanzhe,
                chengke=chengke,
                boli=boli,
                huahen=huahen,
                ziran=ziran,
                fadongji=fadongji,
                chesun_bj=chesun_bj,
                sanzhe_bj=sanzhe_bj,
                daoqiang_bj=daoqiang_bj,
                siji_bj=siji_bj,
                chengke_bj=chengke_bj,
                jiaoqiang=jiaoqiang,
                chechuan=chechuan,
                zongji=zongji
                )
        else:
            CreatInfo = pricing_history.objects.create(
                                                        history_id=HisID,
                                                        car_id = CarId,
                                                        user_id = userID,
                                                        bxgs = bxgs,
                                                        chesun = chesun,
                                                        sanzhe=sanzhe,
                                                        daoqiang = daoqiang,
                                                        siji = siji,
                                                        chengke = chengke,
                                                        boli = boli,
                                                        huahen = huahen,
                                                        ziran = ziran,
                                                        fadongji = fadongji,
                                                        chesun_bj = chesun_bj,
                                                        sanzhe_bj = sanzhe_bj,
                                                        daoqiang_bj = daoqiang_bj,
                                                        siji_bj = siji_bj,
                                                        chengke_bj = chengke_bj,
                                                        jiaoqiang = jiaoqiang,
                                                        chechuan = chechuan,
                                                        zongji = zongji
                                                        )
            CreatInfo.save()
    J = JSON.echo(msg="操作成功")
    return HttpResponse(J, content_type="application/json")
def CreateOrder(request):
    JSON = PrintJson()
    Code = KLBCode()
    openid = request.REQUEST.get("openid", "")
    order_id = request.REQUEST.get("order_id","")
    bxgs = request.REQUEST.get("bxgs","")
    flag = request.REQUEST.get("flag","")
    ownername = request.REQUEST.get("ownername","")
    try:
        OpenidDecode = Code.decode(openid)
        WechatUser = wechat.objects.get(openid=OpenidDecode)
        userID = WechatUser.user_id
    except:
        userID = False
    if not userID:
        J = JSON.echo(msg="没有找到该用户", error=1)
        return HttpResponse(J, content_type="application/json")
    if flag == "1":
        pass
    else:
        CresteInfo = user_order.objects.create(
            userid = userID,
            orderno = order_id,
            bxgs = bxgs
        )
    CresteInfo.save()
    J = JSON.echo(msg="操作成功")
    return HttpResponse(J, content_type="application/json")
#查询订单详情
def OederDetail(request):
    DBAction = BXDBAction()
    order = request.REQUEST.get("order",'')
    bxgs = request.REQUEST.get("bxgs","")
    db={"bxgs":'',
        'status':'',
        'price':'',
        "orderid":'',
        "bizno":"",
        "forcno":"",
        "app_name":'',
        "app_tel":"",
        "app_no":"",
        "insured_name":'',
        "insured_tel":'',
        "insured_no":"",
        "addressee_name":'',
        "addressee_tel":"",
        "addressee_details":""}
    if bxgs == '' or bxgs == None:
        return render_to_response('wechat/UserCenter.html')
    if order == '' or order == None:
        return render_to_response('wechat/UserCenter.html')
    OrderInfo = DBAction.GetHeBaoInfo(order=order,bxgs=bxgs)
    if bxgs == "zh":
        db = {"bxgs": 'zh',
              'status': OrderInfo.status,
              'price': '2342.12',
              "orderid": OrderInfo.order_id,
              "bizno": OrderInfo.c_proposal_no_biz,
              "forcno": OrderInfo.c_proposal_no_force,
              "app_name": OrderInfo.app_name,
              "app_tel": OrderInfo.app_tel,
              "app_no": OrderInfo.app_ident_no,
              "insured_name": OrderInfo.insrnt_name,
              "insured_tel": OrderInfo.insrnt_tel,
              "insured_no": OrderInfo.insrnt_ident_no,
              "addressee_name": OrderInfo.contact_name,
              "addressee_tel": OrderInfo.contact_tel,
              "addressee_details": OrderInfo.address}
    if bxgs == 'as':
        db = {"bxgs": 'as',
              'status': OrderInfo.status,
              'price': '2342.12',
              "orderid": OrderInfo.tborder_id,
              "bizno": OrderInfo.proposalno_biz,
              "forcno": OrderInfo.proposalno_force,
              "app_name": OrderInfo.applicantname,
              "app_tel": OrderInfo.applicantmobile,
              "app_no": OrderInfo.applicantidno,
              "insured_name": OrderInfo.insuredname,
              "insured_tel": OrderInfo.insuredmobile,
              "insured_no": OrderInfo.insuredidno,
              "addressee_name": OrderInfo.addresseename,
              "addressee_tel": OrderInfo.addresseemobile,
              "addressee_details": OrderInfo.addresseedetails}
    if bxgs == 'yg':
        db = {"bxgs": 'yg',
              'status': OrderInfo.status,
              'price': '2342.12',
              "orderid": OrderInfo.tborder_id,
              "bizno": OrderInfo.proposalno_biz,
              "forcno": OrderInfo.proposalno_force,
              "app_name": OrderInfo.applicantname,
              "app_tel": OrderInfo.applicantmobile,
              "app_no": OrderInfo.applicantidno,
              "insured_name": OrderInfo.insuredname,
              "insured_tel": OrderInfo.insuredmobile,
              "insured_no": OrderInfo.insuredidno,
              "addressee_name": OrderInfo.addresseename,
              "addressee_tel": OrderInfo.addresseemobile,
              "addressee_details": OrderInfo.addresseedetails}
    return render_to_response('wechat/OrderList.html',db,context_instance=RequestContext(request))
