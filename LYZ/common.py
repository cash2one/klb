# -*- coding:utf-8 -*-

import time,urllib,json,sys,httplib,urllib2
from LYZ.settings import *
from members.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponse,HttpRequest
import re,random
def phonecheck(s):
    msg = False
    phoneprefix = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139', '150', '151', '152', '153',
                   '156', '158', '159', '170', '183', '182', '185', '186', '188', '189', '177']

    if len(s) <> 11:
        msg = False

    else:
        if s.isdigit():

            if s[:3] in phoneprefix:
                msg = True
            else:
                msg = False
        else:
            msg = False
    return msg

#验证邮件地址
def validateEmail(email):

    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return True
    return False

def sms(phone,n):

    para = {
        'name': SMS_USER,
        'pwd': SMS_PWD,
        # 'content': '(8888)卡来宝注册验证码。',
        # 'content': '尊敬的用户您好！您的验证码是8888',
        'content': '您好！欢迎您注册成为卡来宝会员，您的验证码是%s'%(n),
        'mobile': phone,
        'stime': '',
        'sign': '卡来宝',
        'type': 'pt',
        'extno': '',
    }

    postData = urllib.urlencode(para)
    req = urllib2.Request(SMS_URL, postData)
    resp = urllib2.urlopen(req).read()
    print(resp)
    return resp

def Json_Code(data=None, msg="", error=0,url=""):
    redata = {'error': error, "msg": msg, 'data': data, 'time': time.time(),"url":url}
    rejson = json.dumps(redata)
    return rejson
#用户第三方登录

# 随机生成身份证号


def makeNew():
    ARR = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    LAST = ('1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2')
    t = time.localtime()[0]
    x = '%02d%02d%02d%04d%02d%02d%03d' %(random.randint(10,99),
                                        random.randint(01,99),
                                        random.randint(01,99),
                                        random.randint(t - 80, t - 18),
                                        random.randint(1,12),
                                        random.randint(1,28),
                                        random.randint(1,999))
    y = 0
    for i in range(17):
        y += int(x[i]) * ARR[i]

    return '%s%s' %(x, LAST[y % 11])
