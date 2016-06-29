# -*- coding:utf-8 -*-
from LYZ.settings import *
from datetime import datetime
import time,urllib,json,sys,httplib,urllib2,re

# 字符串加密解密
class AppBaseStr(object):

    def __init__(self, key=SECRET_KEY):
        self.__src_key = key
        self.__key = self.__get_strascii(self.__src_key, True)

    def encode(self, value):
        return "%d" % (self.__get_strascii(value, True) ^ self.__key)

    def decode(self, pwd):
        if self.is_number(pwd):
            return self.__get_strascii((int(pwd)) ^ self.__key, False)
        else:
            return False

    def reset_key(self, key):
        self.__src_key = key
        self.__key = self.__get_strascii(self.__src_key, True)

    def __get_strascii(self, value, bFlag):
        if bFlag:
            return self.__get_str2ascii(value)
        else:
            return self.__get_ascii2str(value)

    def __get_str2ascii(self, value):
        ls = []
        for i in value:
            ls.append(self.__get_char2ascii(i))
        return long("".join(ls))

    def __get_char2ascii(self, char):
        try:
            return "%03.d" % ord(char)
        except (TypeError, ValueError):
            print "key error."
            exit(1)

    def __get_ascii2char(self, ascii):
        if self.is_ascii_range(ascii):
            return chr(ascii)
        else:
            print "ascii error(%d)" % ascii
            exit(1)

    def __get_ascii2str(self, n_chars):
        ls = []
        s = "%s" % n_chars
        n, p = divmod(len(s), 3)
        if p > 0:
            nRet = int(s[0: p])
            ls.append(self.__get_ascii2char(nRet))

        pTmp = p
        while pTmp < len(s):
            ls.append(self.__get_ascii2char(int(s[pTmp: pTmp + 3])))
            pTmp += 3
        return "".join(ls)

    def is_number(self, value):
        try:
            int(value)
            return True
        except (TypeError, ValueError):
            pass
        return False

    def is_ascii_range(self, n):
        return 0 <= n < 256

    def is_custom_ascii_range(self, n):
        return 33 <= n < 48 or 58 <= n < 126


# 输出JSON数据
class PrintJson(object):
    def __init__(self):
        self._time = str(datetime.now())
        self._error = 0
        self._msg = None
        self._data = {}
        self._url = ''
        self._jsonvalue = ''
        self._jsonstr = ''
        self._len = 0

    def echo(self, msg=None, data=None, error=0, url=None, _len=None):
        if error <> None and error <> "":
            self._error = error
        if msg <> None and msg <> "":
            self._msg = msg
        if data <> None and data <> "":
            self._data = data
        if url <> None and url <> "":
            self._url = url
        if _len <> None and _len <> "":
            self._len = _len

        self._jsonvalue = {"time": self._time, "error": self._error, "msg": self._msg, "data": self._data,
                           "url": self._url, "len": self._len}
        self._jsonstr = json.dumps(self._jsonvalue)
        return self._jsonstr
'''
验证
'''
class AppCheck(object):
    #验证手机号
    def phonecheck(self,s):
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
    def validateEmail(self,email):

        if len(email) > 7:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) <> None:
                return True
        return False

    def UserCheck(self,s):
        if re.match("^[a-zA-z][a-zA-Z0-9_]{2,9}$",s) <> None:
            return True
        else:
            return False
    def PwdCheck(self,s):

        if re.match("^[^\s]{6,20}$",s)<> None:
            return True
        else:
            return False

class SendMessage(object):

    def send(self,phone,n):

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
        return resp


#用户key加密解密

class UserKey(object):
    def __init__(self):
        self.BaseCode = AppBaseStr()
    def encode(self,uid="",mobile=""):
        Str = str(uid)+"||"+str(mobile)+"||"+str(time.time()*1000)
        return self.BaseCode.encode(Str)
    def decode(self,s):
        return self.BaseCode.decode(s)