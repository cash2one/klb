# -*- coding:utf-8 -*-
from django.shortcuts import *
from appclass import *
from members.models import *
from datetime import datetime
from LYZ.settings import *
import random
from django.contrib.auth.models import User
from django.contrib import auth
#token
from tokenapi.decorators import token_required
from tokenapi.http import JsonResponse, JsonError
from tokenapi.tokens import token_generator

#首页
@token_required
def Index(request):
    return HttpResponse("")
#用户登录
def Login(request):
    EchoJson = PrintJson()
    Check = AppCheck()
    if request.method == "GET" or request.method == "POST":
        UserName = request.REQUEST.get("username","")
        PassWord = request.REQUEST.get("password","")


        Is_User = False

        if Check.phonecheck(UserName):
            Is_User = "Mobile"
        elif Check.validateEmail(UserName):
            Is_User = "Email"
        elif Check.UserCheck(UserName):
            Is_User = "User"
        else:
            Is_User = False

        if Is_User==False:

            J = EchoJson.echo(msg="用户名格式不正确", error=1)
            return HttpResponse(J,content_type="application/json")
        if Check.PwdCheck(PassWord) == False:

            J = EchoJson.echo(msg="密码只能为6位至20位,并且不能包含空格", error=1)
            return HttpResponse(J,content_type="application/json")

        user = auth.authenticate(username=UserName, password=PassWord)
        if user:
            data = {
                'token': token_generator.make_token(user),
                'user': user.id,
            }
            J = EchoJson.echo(msg="登录成功", error=0,data=data)
            return HttpResponse(J,content_type="application/json")
        else:
            J = EchoJson.echo(msg="认证失败", error=1)
            return HttpResponse(J,content_type="application/json")



    else:
        J = EchoJson.echo(msg="", error=1)
        return HttpResponse(J,content_type="application/json")

#用户注册
def Register(request):
    Check = AppCheck()
    UK = UserKey()
    EchoJson = PrintJson()
    if request.method == 'GET' or request.method == 'POST':
        Mobile = request.REQUEST.get("Mobile", "")
        ValidatedCode = request.REQUEST.get("ValidatedCode", "")
        Password = request.REQUEST.get("Password", "")
        ConfirmPassword = request.REQUEST.get("ConfirmPassword", "")
        RecomCode = request.REQUEST.get("RecomCode", "")

        # 判断手机
        if Check.phonecheck(Mobile) == False:
            J = EchoJson.echo(msg="手机号不正确", error=1)
            return HttpResponse(J,content_type="application/json")
        if User.objects.filter(phone=Mobile).exists():
            J = EchoJson.echo(msg="该手机已经被注册,请不要重复注册", error=1)
            return HttpResponse(J,content_type="application/json")
        # 判断密码
        if Password == "" or len(Password) < 6 or Password <> ConfirmPassword:
            J = EchoJson.echo(msg="密码不能少于6位，且两次输入必须一致", error=1)
            return HttpResponse(J,content_type="application/json")
        # 检查验证码
        CKV = _CheckVcode(Mobile, ValidatedCode)
        if CKV == -1:
            J = EchoJson.echo(msg="验证码不正确", error=1)
            return HttpResponse(J,content_type="application/json")
        if CKV == -2:
            J = EchoJson.echo(msg="验证码过期", error=1)
            return HttpResponse(J,content_type="application/json")

        if CKV == 1:
            J = EchoJson.echo(msg="验证码已经被使用，请更换", error=1)
            return HttpResponse(J,content_type="application/json")
        # 检查推荐码
        if RecomCode <> "":
            Is_recomcode = recomcode.objects.filter(code=RecomCode).exists()
            if Is_recomcode == False:
                J = EchoJson.echo(msg="推荐码不存在", error=1)
                return HttpResponse(J,content_type="application/json")

        CreateUser = User.objects.create_user(username=Mobile,
                                              password=Password,
                                              phone=Mobile
                                              )
        CreateUser.save()
        sendsms.objects.filter(phone=Mobile,validated_code=ValidatedCode).update(is_active=1)
        user = auth.authenticate(username=Mobile, password=Password)
        data = {
            'token': token_generator.make_token(user),
            'user': user.pk,
        }
        J = EchoJson.echo(data=data,msg="注册成功", error=0)
        return HttpResponse(J,content_type="application/json")
    else:
        J = EchoJson.echo(msg="禁止访问", error=1)
        return HttpResponse(J,content_type="application/json")

#获取短信
def SendMsg(request):
    print(request.META)
    Check = AppCheck()
    EchoJson = PrintJson()
    MobileNum = request.REQUEST.get("mobile","")
    if Check.phonecheck(MobileNum) == False:
        J = EchoJson.echo(msg="手机号码错误",error=1)
        return HttpResponse(J,content_type="application/json")
    else:

        Code = random.randint(1000,9999)
        Is_set = sendsms.objects.filter(phone=int(MobileNum)).exists()

        if Is_set:

            Ycode = sendsms.objects.filter(phone=MobileNum)
            if Ycode.values()[0]["is_active"] == 1:
                J = EchoJson.echo(msg="该手机已经注册,请更换手机号！",error=1)
                return HttpResponse(J,content_type="application/json")
            # if Ycode.values()[0]["sendnum"] >5:
            #     J = EchoJson.echo(msg="该手机号已经超过发送次数,请联系管理员",error=1)
            #     return HttpResponse(J,content_type="application/json")
            Xtime = datetime.now()
            Ytime = Ycode.values()[0]["addtime"]
            Stime = (Xtime-Ytime).seconds
            if Stime<180:
                Msg = "请%s秒后重试"%(180-Stime)
                J = EchoJson.echo(msg=Msg,error=1)
                return HttpResponse(J,content_type="application/json")
            else:
                N = sendsms.objects.get(id=Ycode.values()[0]["id"])
                N.validated_code = Code
                N.sendnum = N.sendnum+1
                N.save()

        else:
            CodeCreate = sendsms.objects.create(phone=int(MobileNum),validated_code=Code,sys=SYS_MOBILE)
            CodeCreate.save()
        Sms = SendMessage()
        Sms.send(MobileNum,Code)
        J = EchoJson.echo(msg="验证码发送成功")
        return HttpResponse(J,content_type="application/json")


def _CheckVcode(p, c):
    CH = sendsms.objects.filter(phone=p, validated_code=c).exists()
    if CH:
        CHDATA = sendsms.objects.filter(phone=p, validated_code=c).values()
        Xtime = datetime.now()
        Ytime = CHDATA[0]["addtime"]
        Stime = (Xtime - Ytime).seconds
        if Stime > 180:
            return -2
        else:
            Code = CHDATA[0]['is_active']
            return Code

    else:
        return -1

#头像上传
@token_required
def ImgUpload(request):
    EchoJson = PrintJson()
    if request.method == 'POST':
        img = request.FILES.get("img", "")
        uid = request.REQUEST.get("user", "")
        if img == None or img == "":
            J = EchoJson.echo(msg="服务器未接收到文件", error=1)
            return HttpResponse(J,content_type="application/json")

        ImgType = ("image/png", "image/jpeg", "image/gif", "image/jpg")
        try:
            print(img.content_type)
            if img.content_type not in ImgType:
                J = EchoJson.echo(msg="文件类型不正确,只能是jpg,gif,png", error=1)
                return HttpResponse(J,content_type="application/json")
        except:
            J = EchoJson.echo(msg="服务器未接收到文件", error=1)
            return HttpResponse(J,content_type="application/json")
        if img.size > 2048000:
            J = EchoJson.echo(msg="图片不能大于2M", error=1)
            return HttpResponse(J,content_type="application/json")

        upimg = photo(user_id=uid, image=img)
        upimg.save()

        data = {
            "image": "http://" + request.get_host() + "/media/" + str(upimg.image),
            "thumbnail": "http://" + request.get_host() + "/media/" + str(upimg.thumbnail)
        }
        J = EchoJson.echo(data=data, msg="上传成功", error=0)
        return HttpResponse(J,content_type="application/json")
    else:
        J = EchoJson.echo(msg="拒绝访问", error=1)
        return HttpResponse(J,content_type="application/json")


@token_required
def test(request):
    return render_to_response('members/test.html',{},context_instance=RequestContext(request))

def Error_404(request):
    EchoJson = PrintJson()
    J = EchoJson.echo(msg="请求地址不存在",error=1)
    return HttpResponse(J,content_type="application/json")

def Error_500(request):
    EchoJson = PrintJson()
    J = EchoJson.echo(msg="服务器内部错误",error=1)
    return HttpResponse(J,content_type="application/json")


