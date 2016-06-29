# -*- coding:utf-8 -*-
from django.shortcuts import *
from bxservice.zhonghua import *
from bxservice.ansheng import *
from bxservice.yangguang import *
import dicttoxml

def ZhongHuaIndex(request):
    YGServ = YangGuang()
    Z = YGServ.Send()
    return HttpResponse(Z)
