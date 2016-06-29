# -*- coding:utf-8 -*-
from django.shortcuts import *
from LYZ.common import *
from webadmin.forms import UserForms, UserAuth,DefineCodeForms,AutoCreateUser
from webadmin.models import ebusiness_members
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from LYZ.klb_class import KLBCode
import time


def Index(request):
    Auth = UserAuth(request)
    if Auth.isLogin():
        return render_to_response('ebusiness/Member/admin-index.html', {}, context_instance=RequestContext(request))
    else:
        return HttpResponsePermanentRedirect("/webadmin/Login/")


def Login(request):
    import json
    TempData = {}
    if request.method == "POST":

        reqtime = request.session.get("reqtime", "")
        request.session['reqtime'] = time.time()
        xztime = time.time()
        try:
            TimeInterval = int(xztime - reqtime)
        except:
            TimeInterval = 0
        request.session['reqtime'] = time.time()
        if 0 < TimeInterval < 10:
            TempData.update({"accessGranted": "", "errors": "操作频繁，请%s秒后再试......" % str(TimeInterval)})
        else:
            forms = UserForms(request.POST)
            if forms.is_valid():
                username = request.REQUEST.get("username", "")
                UserMember = ebusiness_members.objects.filter(username=username).values()[0]
                request.session['ebusiness_username'] = username
                request.session['ebusiness_user_id'] = UserMember['id']
                request.session['ebusiness_code'] = UserMember['code']
                request.session['ebusiness_ischildren'] = UserMember['ischildren']
                TempData.update({"url": "/webadmin/", "accessGranted": "ok", })
            else:
                TempData.update({"accessGranted": "", "errors": forms.errors['username'].as_text()})

        TempJSON = json.dumps(TempData)
        return HttpResponse(TempJSON, content_type="application/json")
    else:
        forms = UserForms()
        TempData.update({"forms": forms})
        return render_to_response('ebusiness/Member/login-admin.html', TempData,
                                  context_instance=RequestContext(request))


def Analytics(request):
    TempData = dict(request.REQUEST.items())
    SessionData = dict(request.session.items())
    Auth = UserAuth(request)
    if Auth.isLogin():
        page_size = 20
        after_range_num = 5
        before_range_num = 6
        Action = TempData.get("action")
        Action = (Action == "") and "flow" or Action

        if Action == "flow":
            eUser = ebusiness_members.objects.get(id=SessionData.get("ebusiness_user_id"))
            eUser_Flow = eUser.flow_analytics_set.order_by('-endtime').all()
            paginator = Paginator(eUser_Flow, page_size)
        elif Action == "buy":
            paginator = Paginator([], page_size)
        else:
            paginator = Paginator([], page_size)
        try:
            try:
                page = int(TempData.get("page", ""))
                page = page < 1 and 1 or page
            except ValueError:
                page = 1
            try:
                DATA = paginator.page(page)
            except(EmptyPage, InvalidPage, PageNotAnInteger):
                DATA = paginator.page(1)
            if page >= after_range_num:
                page_range = paginator.page_range[page - after_range_num:page + before_range_num]
            else:
                page_range = paginator.page_range[0:int(page) + before_range_num]

            TempData.update({"DATA": DATA, "page_range": page_range})
            if Action == "flow":
                TEMP = 'ebusiness/Member/admin-analytics.html'
            if Action == 'buy':
                TEMP = 'ebusiness/Member/admin-buy.html'
            return render_to_response(TEMP, TempData, context_instance=RequestContext(request))
        except AttributeError:
            return HttpResponsePermanentRedirect("/webadmin/")
    else:
        return HttpResponsePermanentRedirect("/webadmin/Login/")


'''
推广中心
'''


def Share(request):
    Auth = UserAuth(request)
    if Auth.isLogin():
        TempData = dict(request.REQUEST.items())
        Action = TempData.get("action","")
        if request.method == "POST":
            CodeForms = DefineCodeForms(request.POST)
            if Action == "define_code" and CodeForms.is_valid():
                TempData.update({"DefineCodeStatus":"1"})
                request.session['ebusiness_code'] = TempData.get("code","")

        else:
            CodeForms = DefineCodeForms(initial={"code":request.session.get("ebusiness_code",""),"uid":request.session.get("ebusiness_user_id","")})


        GetUser = ebusiness_members.objects.get(id=request.session.get("ebusiness_user_id",""))
        TempData.update({"CodeForms":CodeForms,"user":GetUser})
        return render_to_response("ebusiness/Member/admin-share.html", TempData, context_instance=RequestContext(request))
    else:
        return HttpResponsePermanentRedirect("/webadmin/Login/")


def ShareChildren(request, code=None):
    KCode = KLBCode()
    TempData = dict(request.REQUEST.items())
    code = KCode.decode(code)
    if code <> "":

        if request.method == "POST":
            forms = AutoCreateUser(request.POST)
            if forms.is_valid():
                In,IsSet = forms.CheckAuthenticate(fcode=code)
                TempData.update({"isok":True,"forms":forms,"User":In})

        else:
            forms = AutoCreateUser()
        TempData.update({"forms":forms})
        return render_to_response("ebusiness/Member/admin-share-children.html", TempData,context_instance=RequestContext(request))
    else:
        html = '' \
               '<!DOCTYPE html>' \
               '<html lang="en">' \
               '<head>' \
               '<meta charset="UTF-8">' \
               '<title></title>' \
               '</head><body>' \
               '<body>' \
               '<script>' \
               'alert("链接错误!");' \
               'window.location.href="http://www.kalaibao.com/ebusiness/?ShowBanner=1";' \
               '</script>' \
               '</body>' \
               '</html>'

        return HttpResponse(html)

'''
用户退出登录
'''
def Logout(request):
    for k,v in request.session.items():
        del request.session[k]
    return HttpResponsePermanentRedirect("/webadmin/Login/")


