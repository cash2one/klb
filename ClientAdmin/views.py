# -*- coding:utf-8 -*-
from django.shortcuts import *
from ClientAdmin.forms import AddUserForms
from django.contrib.auth.hashers import make_password, check_password
def Index(request):
    return render_to_response('ClientAdmin/Index.html', {}, context_instance=RequestContext(request))
def Login(request):
    return HttpResponse("")

def Logout(request):
    return HttpResponse("")

def AddUser(request):
    TempData = {}
    if request.method == "POST":

        forms = AddUserForms(request.POST)
        if forms.is_valid():
            In,IsSet = forms.CheckAuthenticate()
            TempData.update({"isok":True,"forms":forms,"User":In})
        else:
            TempData.update({"forms":forms,"isok":False})
    else:
        forms = AddUserForms()
        TempData.update({"forms":forms})
    return render_to_response('ClientAdmin/AddUser.html', TempData, context_instance=RequestContext(request))
