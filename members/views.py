# -*- coding:utf-8 -*-
from django.shortcuts import *
from LYZ.settings import *
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from LYZ.common import *
from LYZ.klb_class import *
from klbapp.appclass import *
from models import *
import random, datetime, time
from DjangoCaptcha import Captcha
import qrcode
import hashlib
from cStringIO import StringIO

import urllib, urllib2, json


def Default_Index(request):
    return HttpResponse("☀")


'''
@用户中心首页
'''


def Index(request):
    # m = make_password("haha",None,"unsalted_md5")
    # print(m)
    # print(check_password("haha",m))
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/members/login/")
    return render_to_response('members/member_index.html', {}, context_instance=RequestContext(request))


'''
@用户登录
'''


def Login(request):
    Next = request.REQUEST.get("next", "")
    print(Next)
    if request.user.is_authenticated():
        return HttpResponseRedirect("/members/")
    if request.method == 'POST':
        UserName = request.REQUEST.get("username", "")
        Password = request.REQUEST.get("password", "")

        user = authenticate(username=UserName, password=Password)
        if user is not None:

            login(request, user)
            if validateEmail(UserName):
                UserName = UserName.split("@")[0]
            request.session['klb_username'] = UserName
            print(request.user.id)
            print(Next)
            J = Json_Code(data='', msg="登录成功", error=0, url=Next)
            return HttpResponse(J)
        else:
            J = Json_Code(data='', msg="登录失败，请检查输入是否有误", error=1)
            return HttpResponse(J)
    else:
        return render_to_response('members/member_login.html', {}, context_instance=RequestContext(request))


'''
@用户注册
'''


def Reg(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/members/")
    if request.method == 'POST':
        Action = request.REQUEST.get("action", "")

        # 手机注册
        if Action == "mobile":
            Mobile = request.REQUEST.get("Mobile", "")
            ValidatedCode = request.REQUEST.get("ValidatedCode", "")
            Password = request.REQUEST.get("Password", "")
            InputConfirmPassword = request.REQUEST.get("InputConfirmPassword", "")
            RecomCode = request.REQUEST.get("u", "")
            # 判断手机
            if phonecheck(Mobile) == False:
                J = Json_Code(data='', msg="手机号不能为空", error=1)
                return HttpResponse(J)
            # 判断密码
            if Password == "" or len(Password) < 6 or Password <> InputConfirmPassword:
                J = Json_Code(data='', msg="密码不能少于6位，且两次输入必须一致", error=1)
                return HttpResponse(J)
            # 检查验证码
            if _CheckVcode(Mobile, ValidatedCode) == -1:
                J = Json_Code(data='', msg="验证码不正确", error=1)
                return HttpResponse(J)
            else:
                MCode = _CheckVcode(Mobile, ValidatedCode)
                if MCode == 1:
                    J = Json_Code(data='', msg="验证码已经使用过", error=1)
                    return HttpResponse(J)
            # 检查推荐码
            if RecomCode <> "":
                Is_recomcode = recomcode.objects.filter(code=RecomCode).exists()
                if Is_recomcode == False:
                    J = Json_Code(data='', msg="推荐码不存在", error=1)
                    return HttpResponse(J)
            if User.objects.filter(phone=Mobile).exists():
                J = Json_Code(data='', msg="该手机已经被注册,请不要重复注册", error=1)
                return HttpResponse(J)
            CreateUser = User.objects.create_user(username=Mobile,
                                                  password=Password,
                                                  phone=Mobile,
                                                  nick_name=Mobile,
                                                  )
            CreateUser.save()
            request.session['klb_username'] = Mobile
            user = authenticate(username=Mobile, password=Password)
            login(request, user)
            _InSetRecomCode(CreateUser.id)
            J = Json_Code(data='', msg="注册成功", error=0)

            return HttpResponse(J)
        # 邮箱注册
        if Action == "email":
            Email = request.REQUEST.get("Email", "")
            Password = request.REQUEST.get("Password", "")
            InputConfirmPassword = request.REQUEST.get("InputConfirmPassword", "")
            RecomCode = request.REQUEST.get("RecomCode", "")
            ValidCode = request.REQUEST.get("ValidCode", "")

            if validateEmail(Email) == False:
                J = Json_Code(data='', msg="邮件地址不正确", error=1)
                return HttpResponse(J)

            IS_EmailSet = User.objects.filter(email=Email).exists()
            if IS_EmailSet:
                J = Json_Code(data='', msg="该邮件地址已经存在,请更换邮件地址", error=1)
                return HttpResponse(J)
            if len(Password) < 6 or len(Password) > 50:
                J = Json_Code(data='', msg="密码长度不能少于6位", error=1)
                return HttpResponse(J)
            if Password <> InputConfirmPassword:
                J = Json_Code(data='', msg="两次密码输入不一致", error=1)
                return HttpResponse(J)
            if RecomCode <> "":
                Is_recomcode = recomcode.objects.filter(code=RecomCode).exists()
                if Is_recomcode == False:
                    J = Json_Code(data='', msg="推荐码不存在", error=1)
                    return HttpResponse(J)

            CreateUser = User.objects.create_user(username=Email,
                                                  password=Password,
                                                  email=Email,
                                                  nick_name=Email,
                                                  )
            CreateUser.save()
            user = authenticate(username=Email, password=Password)
            login(request, user)
            if validateEmail(Email):
                Email = Email.split("@")[0]
            request.session['klb_username'] = Email
            _InSetRecomCode(CreateUser.id)
            J = Json_Code(data='', msg="注册成功", error=0)
            return HttpResponse(J)

    else:
        return render_to_response('members/member_reg.html', {}, context_instance=RequestContext(request))


'''
@用户退出
'''


def Logout_View(request):
    logout(request)
    request.session["klb_username"] = ""
    return HttpResponseRedirect("/members/login/")


'''
@订单详情
'''


def OrderDetails(request, t=''):
    if t == 'paid':
        return render_to_response('members/member_orderdetails.html', {}, context_instance=RequestContext(request))
    elif t == 'non_payment':
        return render_to_response('members/member_orderdetails.html', {}, context_instance=RequestContext(request))
    else:
        return render_to_response('members/member_orderdetails.html', {}, context_instance=RequestContext(request))


'''
@用户帮助
'''


def Help(request):
    return HttpResponse("help")


'''
@用户基本资料设置
'''


@login_required
def Setting(request, action=''):
    UClass = UserClass()
    db = {}
    if action == 'info':
        ErrorMsg = {}
        if request.method == "POST":
            uid = request.user.id
            username = request.REQUEST.get("username", "")
            real_name = request.REQUEST.get("real_name", "")
            sex = request.REQUEST.get("sex", "")
            email = request.REQUEST.get("email", "")
            idcard = request.REQUEST.get("idcard", "")
            phone = request.REQUEST.get("phone", "")
            ver_code = request.REQUEST.get("ver_code", "")
            addr = request.REQUEST.get("addr", "")
            if phone <> "" and ver_code <> "":

                CV = _CheckVcode(phone, ver_code)
                if CV == -1:
                    ErrorMsg = {"phone": "手机验证码不正确"}
                elif CV == 1:
                    ErrorMsg = {"phone": "手机验证码已经使用"}

            elif email <> "":
                pass
            else:
                UClass.SetUser(
                    uid=uid,
                    username=username,
                    real_name=real_name,
                    sex=sex,
                    email=email,
                    phone=phone,
                    idcard=idcard,
                    addr=addr
                )
        db.update(ErrorMsg)
        return render_to_response('members/member_setting_info.html', {}, context_instance=RequestContext(request))
    elif action == 'security':
        return render_to_response('members/member_setting_security.html', {}, context_instance=RequestContext(request))
    elif action == 'message':
        return render_to_response('members/member_setting_message.html', {}, context_instance=RequestContext(request))
    else:
        return render_to_response('members/member_setting_info.html', {}, context_instance=RequestContext(request))


'''
@用户推广中心
'''


def DiffuseCente(request):
    pass


'''

'''


def TuiJianMa(request):
    action = request.REQUEST.get("a", "")
    if not request.user.is_authenticated():
        J = Json_Code(data='', msg="没有权限", error=1)
        return HttpResponse(J)
    else:
        if action <> "set":
            try:
                # 推荐码存在
                Rcode = recomcode.objects.get(user_id=request.user.id)
                C = Rcode.code
            except ObjectDoesNotExist:
                # 推荐码不存在
                C = random.randint(100000, 999999)
                In = recomcode(user_id=request.user.id, code=C)
                In.save()
            J = Json_Code(data={"code": C}, msg="推荐码", error=0)
            return HttpResponse(J)

        else:
            time.sleep(1)
            NewCode = request.REQUEST.get("code", "")
            if len(NewCode) < 6 or len(NewCode) > 60:
                J = Json_Code(data='', msg="推荐码不能少于6位,大于20位", error=1)
                return HttpResponse(J)
            elif recomcode.objects.filter(code=NewCode).exists():

                J = Json_Code(data='', msg="推荐码已经被使用", error=1)
                return HttpResponse(J)
            else:

                print(NewCode)
                In = recomcode.objects.get(user_id=request.user.id)
                In.code = NewCode
                In.save()
                # 更新短网址
                klbcode = KLBCode()
                Curl = "http://" + request.get_host() + "/members/reg/?u=" + klbcode.encode(NewCode)
                print(Curl)
                para = {
                    "url": Curl,
                    "alias": "klb_" + NewCode
                }

                postData = urllib.urlencode(para)
                req = urllib2.Request("http://dwz.cn/create.php", postData)
                resp = urllib2.urlopen(req).read()
                M = json.loads(resp)
                if M['status'] <> 0:
                    J = Json_Code(data='', msg=M["err_msg"], error=1)
                    return HttpResponse(J)
                else:
                    In = recomcode.objects.get(user_id=request.user.id)
                    In.dwz = M['tinyurl']
                    In.save()
                    J = Json_Code(data={"code": NewCode, "url": M['tinyurl']}, msg="设置成功", error=0)
                    return HttpResponse(J)


'''
我的车
'''


@login_required
def MyCar(request):
    EchoJson = PrintJson()
    MC = MyCarClass()
    uid = request.user.id
    if request.method == 'POST':
        # 判断执行动作是否为绑定
        action = request.REQUEST.get("a", "")

        if action == "bind":
            chepai = request.REQUEST.get("chepai", "")
            carusername = request.REQUEST.get("carusername", "")
            vin = request.REQUEST.get("vin", "")
            fadongji = request.REQUEST.get("fadongji", "")

            if chepai == "" or carusername == "" or vin == "" or fadongji == "":
                J = EchoJson.echo(msg="请输入完整的信息", error=1)
                return HttpResponse(J)
            if MC.CarIsSet(c=chepai, vin=vin):
                J = EchoJson.echo(msg="该车已经绑定", error=1)
                return HttpResponse(J)

            NewId = MC.CreateCar(
                uid=uid,
                chepai=chepai,
                carusername=carusername,
                vin=vin,
                fadongji=fadongji,

            )
            if NewId == False:
                J = EchoJson.echo(msg="VIN号码解析错误", error=1)
                return HttpResponse(J)
            else:
                J = EchoJson.echo(msg="添加成功", error=0, data={"id": NewId})
                return HttpResponse(J)
        else:
            J = EchoJson.echo(msg="参数不正确", error=1)
            return HttpResponse(J)

    else:
        C = MC.GetCar(uid=uid)
        db = {"car": C}
        return render_to_response('members/member_mycar.html', db, context_instance=RequestContext(request))


'''
汽车召回
'''


@login_required
def CarRecall(request):
    EchoJson = PrintJson()
    MC = MyCarClass()
    Log = MC.ReCallLog(uid=request.user.id)
    db = {"Log": Log}
    if request.method == "POST":
        vin = request.REQUEST.get("vin", "")
        year = request.REQUEST.get("year", "")
        if vin == "" or year == "":
            pass
        else:
            ReCall = MC.ReCall(vin=vin, year=year, uid=request.user.id)
            db.update({"ReCall": ReCall})

    GetMycar = {"MyCar": MC.GetCar(uid=request.user.id)}
    db.update(GetMycar)
    return render_to_response('members/member_recall.html', db, context_instance=RequestContext(request))


'''
@会员升级
'''


def UpDateToVip(request):
    return render_to_response('members/member_updatetovip.html', {}, context_instance=RequestContext(request))


'''
@头像上传
'''


def ImgUpload(request):
    if not request.user.is_authenticated():
        J = Json_Code(data='', msg="没有权限", error=1)
        return HttpResponse(J)
    else:
        if request.method == 'POST':

            img = request.FILES.get("img", "")
            print(img.size)
            uid = request.user.id
            print(uid)
            upimg = photo(user_id=uid, image=img)
            upimg.save()
            print(upimg.image)
            print(upimg.thumbnail)
            print("http://" + request.get_host() + "/media/" + str(upimg.image))
            data = {"image": str(upimg.image), "thumbnail": str(upimg.thumbnail)}
            J = Json_Code(data=data, msg="上传成功", error=0)
            return HttpResponse(J)
        else:
            return render_to_response('members/member_upload.html', {}, context_instance=RequestContext(request))


'''
@获取验证码
'''


def GetVcode(request):
    phone = request.REQUEST.get("phone", "")
    IP = _getIP(request)
    if phonecheck(phone) == False:
        J = Json_Code(data='', msg="手机号码错误", error=1)
        return HttpResponse(J)
    else:

        Code = random.randint(1000, 9999)
        Is_set = sendsms.objects.filter(phone=phone).exists()

        if Is_set:

            Ycode = sendsms.objects.filter(phone=phone)
            if Ycode.values()[0]["is_active"] == 1:
                J = Json_Code(data='', msg="该手机已经注册,请更换手机号！", error=1)
                return HttpResponse(J)
            if Ycode.values()[0]["sendnum"] > 5:
                J = Json_Code(data='', msg="该手机号已经超过发送次数,请联系管理员", error=1)
                return HttpResponse(J)
            Xtime = datetime.datetime.now()
            Ytime = Ycode.values()[0]["addtime"]
            Stime = (Xtime - Ytime).seconds
            if Stime < 180:
                Msg = "请%s秒后重试" % (180 - Stime)
                J = Json_Code(data='', msg=Msg, error=1)
                return HttpResponse(J)
            else:
                N = sendsms.objects.get(id=Ycode.values()[0]["id"])
                N.validated_code = Code
                N.sendnum = N.sendnum + 1
                N.save()

        else:
            CodeCreate = sendsms(phone=phone, validated_code=Code, sendip=IP)
            CodeCreate.save()
        sms(phone, Code)
        J = Json_Code(data='', msg="验证码发送成功", error=0)
        return HttpResponse(J)


'''

'''


def ValidCode(request):
    mod = request.REQUEST.get("a", "")
    if mod <> "check":
        ca = Captcha(request)
        # ca.words = ['hello','world','helloworld']
        ca.type = 'number'
        # ca.type = 'word'
        ca.img_width = 140
        ca.img_height = 30
        return ca.display()
    else:
        _code = request.GET.get('code')
        ca = Captcha(request)
        if ca.check(_code):
            J = Json_Code(data='', msg="验证成功", error=0)
        else:
            J = Json_Code(data='', msg="验证失败", error=1)
        return HttpResponse(J)


'''
@获取IP
'''


def _getIP(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


'''
@检查验证码
'''


def _CheckVcode(p, c):
    CH = sendsms.objects.filter(phone=p, validated_code=c).exists()
    if CH:
        CHDATA = sendsms.objects.filter(phone=p, validated_code=c).values()
        Code = CHDATA[0]['is_active']
        return Code

    else:
        return -1


def _InSetRecomCode(uid):
    C = random.randint(100000, 999999)
    if recomcode.objects.filter(user_id=uid, code=C).exists():
        C = _InSetRecomCode(uid)
    else:
        In = recomcode(user_id=uid, code=C)
        In.save()
    return C


def GenerateQrcode(request):
    a = request.REQUEST.get("a","")
    d = request.REQUEST.get("d","")
    data = request.REQUEST.get("s", "")
    if a == "encode":
        if data <>"":
            try:
                Code = KLBCode()
                data = Code.decode(data)
            except:
                pass
    img = qrcode.make(data)
    buf = StringIO()
    img.save(buf)
    image_stream = buf.getvalue()
    if d=="download":
        response = HttpResponse(image_stream,mimetype='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=%s' %str(int(time.time()))+'.png'
    else:
        response = HttpResponse(image_stream, content_type="image/png")
    return response


# 微信登录

def WechatLogin(request):
    OA = KLBOAuth()
    code = request.REQUEST.get("code", "")
    a = request.REQUEST.get("a","")
    KCode = KLBCode()
    Action = KCode.decode(a)
    if code == "" or code == None:
        #如果没有code，判断
        if Action=="ebusiness":
            return HttpResponse("<script>alert('操作错误!');history.back();</script>")
        else:
            return render_to_response('members/member_login.html', {}, context_instance=RequestContext(request))

    params = urllib.urlencode(
        {'appid': OPEN_WECHAT_APPID, 'secret': OPEN_WECHAT_APPSECRET, "code": code, "grant_type": "authorization_code"})
    Req_Url = "https://api.weixin.qq.com/sns/oauth2/access_token?%s" % params
    wechat_json = urllib.urlopen(Req_Url).read()
    wechat_array = json.loads(wechat_json)
    access_token = wechat_array['access_token']
    openid = wechat_array['openid']
    params = urllib.urlencode({'access_token': access_token, 'openid': openid})
    UserInfoUrl = "https://api.weixin.qq.com/sns/userinfo?%s" % (params)
    wechat_json = urllib.urlopen(UserInfoUrl).read()
    wechat_array = json.loads(wechat_json)

    try:
        GetUser = wechat.objects.get(openid=openid)
        UserInfo = User.objects.get(id=GetUser.user_id)
        user = authenticate(username=UserInfo.username,password="klb@weixin")
        login(request, user)


    except ObjectDoesNotExist:
        OA.CreateUser_Wechat(
            request=request,
            openid=openid,
            nickname=wechat_array['nickname'],
            sex=wechat_array['sex'],
            language=wechat_array['language'],
            city=wechat_array['city'],
            country=wechat_array['country'],
            province=wechat_array['province'],
            headimgurl=wechat_array['headimgurl'],
            unionid=wechat_array['unionid'],
            wechat=True,
            reopenid=False

        )
    if Action=="ebusiness":
        ReURL= dict(request.REQUEST.items())
        ReGo = "/ebusiness/editInfo/?"+urllib.urlencode(ReURL)
        return HttpResponsePermanentRedirect(ReGo)
    else:
        return HttpResponsePermanentRedirect("/members/")

@login_required
def pay(request):
    BANK = (
    "ABC", "BCCB", "BCM", "BOCSH", "BOS", "BRCB", "CCB", "CEB", "CIB", "CMB", "CMBC", "CNCB", "GDB", "HXB", "HZB", "NBCB",
    "PAB", "PSBC", "SPBD", "SRCB", "OTHER")
    uid = request.user.id
    MerNo = "183871"  # 商户ID
    MD5KEY = "_zxtVhUK"
    ReturnURL = "http://www.kalaibao.com/members/payResult/"
    NotifyURL = "http://www.kalaibao.com/members/NotifyURL/"
    BillNo = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))  # 订单号


    db = {
        "bank": BANK,
        "MerNo":MerNo,
        "MD5KEY":MD5KEY,
        "ReturnURL":ReturnURL,
        "BillNo":BillNo,
        "NotifyURL":NotifyURL
    }
    return render_to_response('members/member_pay.html', db, context_instance=RequestContext(request))
@login_required
def GetPayMD5Info(request):
    uid = request.user.id
    Amount = request.REQUEST.get("Amount", "")  #支付金额
    BillNo = request.REQUEST.get("BillNo","")# 订单号
    Amount = Amount if True else "100"
    MerNo = "183871"  # 商户ID
    MD5KEY = "_zxtVhUK"
    ReturnURL = "http://www.kalaibao.com/members/payResult/"
    print(hashlib.new("md5", "BYAABD0057").hexdigest())
    MD5KEY_MD5 = hashlib.new("md5", MD5KEY).hexdigest().upper()
    MStr = "Amount=%s&BillNo=%s&MerNo=%s&ReturnURL=%s&%s"%(Amount,BillNo,MerNo,ReturnURL,MD5KEY_MD5)

    MD5info = hashlib.new("md5", MStr).hexdigest().upper()
    issetpay = order_pay.objects.filter(order_number=BillNo)
    if not issetpay.exists():
        createpay = order_pay.objects.create(user_id=uid,order_number=BillNo,order_sum=Amount)
        createpay.save()

    db = {"MD5info":MD5info}
    J = Json_Code(data=db, msg="ok", error=0)
    return HttpResponse(J,content_type="application/json")

def payResult(request):
    Ret = dict(request.REQUEST.items())
    J = Json_Code(data=Ret,msg="ok", error=0)
    return HttpResponse(J,content_type="application/json")

def NotifyURL(request):
    Ret = dict(request.REQUEST.items())
    J = Json_Code(data=Ret,msg="ok", error=0)
    return HttpResponse(J,content_type="application/json")
