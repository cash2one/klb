# -*- coding:utf-8 -*-
import settings
from members.models import car, carinfo, recall, recall_log, wechat, recomcode
from django.contrib.auth import authenticate, login
import urllib, json, urllib2, re
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
import BeautifulSoup
import smtplib, random, datetime, sys
from email.mime.text import MIMEText
from email.header import Header
from Crypto.Cipher import AES
import base64
import os
import json
import time
import random
import string
import urllib
import cookielib



# 加密解密，加密后为一串数字
class KLBCode(object):
    def __init__(self, key="fengchao"):
        self.__src_key = key
        self.__key = self.__get_strascii(self.__src_key, True)

    def encode(self, value):
        return "%d" % (self.__get_strascii(value, True) ^ self.__key)

    def decode(self, pwd):
        if self.is_number(pwd):
            return self.__get_strascii((int(pwd)) ^ self.__key, False)
        else:
            return ""

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


class KLBOAuth(object):
    def __init__(self):
        pass

    def CreateUser_Wechat(self, **pam):
        request = pam['request']
        openid = pam['openid']
        nickname = pam['nickname']
        sex = pam['sex']
        language = pam['language']
        province = pam['province']
        city = pam['city']
        country = pam['country']
        headimgurl = pam['headimgurl']
        # privilege = pam['privilege']
        unionid = pam['unionid']
        isWwechat = pam['wechat']
        klbrandom = str(random.randint(10000000, 99999999))
        username = klbrandom + "@weixin"
        password = "klb@weixin"
        try:
            reopenid = pam['reopenid']
        except:
            reopenid = False

        CreateUser = User.objects.create_user(
            username=username,
            nick_name=nickname,
            password=password

        )
        CreateUser.save()
        uid = CreateUser.id

        CreateWechat = wechat.objects.create(
            user_id=uid,
            openid=openid,
            sex=sex,
            nickname=nickname,
            language=language,
            province=province,
            city=city,
            country=country,
            headimgurl=headimgurl,
            unionid=unionid
        )
        self.InSetRecomCode(uid)

        CreateWechat.save()
        WechatID = CreateWechat.id
        if isWwechat:
            return uid
        if reopenid:
            return WechatID

        else:
            user = authenticate(username=username, password=password)
            login(request, user)
            return True

    def LoginUser_Wechat(self, **pam):
        password = "klb@weixin"
        user = authenticate(username=pam['username'], password=password)
        login(pam['request'], user)
        U = User.objects.get(id=user.id)

        U.wechat.sex = pam['sex'],
        U.wechat.nickname = pam['nickname'],
        U.wechat.language = pam['language'],
        U.wechat.province = pam['province'],
        U.wechat.city = pam['city'],
        U.wechat.country = pam['country'],
        U.wechat.headimgurl = pam['headimgurl'],
        U.wechat.unionid = pam['unionid']
        U.wechat.save()
        return True

    def InSetRecomCode(self, uid):
        import time
        C = int(time.time())
        H5C = self.InSetH5RecomCode()
        if not recomcode.objects.filter(user_id=uid).exists():
            CreateCode = recomcode.objects.create(user_id=uid, code=C, h5code=H5C)
            CreateCode.save()
        return C

    def InSetH5RecomCode(self):
        passData = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        StrArr = []
        for i in range(5):
            StrArr.append(random.choice(passData))

        StrArr = ''.join(StrArr)
        if recomcode.objects.filter(h5code=StrArr).exists():
            StrArr = self.InSetH5RecomCode()

        return StrArr


class MyCarClass(object):
    def __init__(self):
        pass

    def CarIsSet(self, c="", vin=""):
        Car = car.objects.filter(chepai=c, vin=vin).exists()
        if Car:
            return True
        else:
            return False

    def CreateCar(self, **pam):
        uid = pam['uid']
        chepai = pam['chepai']
        carusername = pam['carusername']
        vin = pam['vin']
        fadongji = pam['fadongji']
        car_params = urllib.urlencode({'vin': vin, 'key': "f7528d0d8a354b6e85cc2623cc53cf2c"})
        Req_Url = "http://apis.haoservice.com/lifeservice/vin?%s" % car_params
        print(Req_Url)
        car_json = urllib.urlopen(Req_Url).read()
        car_array = json.loads(car_json)
        if car_array['error_code'] == 0:
            AddCar = car(user_id=uid,
                         chepai=chepai,
                         carusername=carusername,
                         vin=vin,
                         fadongji=fadongji,
                         )
            AddCar.save()
            try:
                M = carinfo(
                    car_id=AddCar.id,
                    name=car_array['result']['name'],
                    brand=car_array['result']['brand'],
                    productionDate=car_array['result']['productionDate'],
                    model=car_array['result']['model'],
                    engineType=car_array['result']['engineType'],
                    displacement=car_array['result']['displacement'],
                    power=car_array['result']['power'],
                    type=car_array['result']['type'],
                    reatedQuality=car_array['result']['reatedQuality'],
                    totalQuality=car_array['result']['totalQuality'],
                    equipmentQuality=car_array['result']['equipmentQuality'],
                    combustionType=car_array['result']['combustionType'],
                    emissionStandards=car_array['result']['emissionStandards'],
                    shaftNum=car_array['result']['shaftNum'],
                    shaftdistance=car_array['result']['shaftdistance'],
                    shaftLoad=car_array['result']['shaftLoad'],
                    springNum=car_array['result']['springNum'],
                    tireNum=car_array['result']['tireNum'],
                    tireSpecifications=car_array['result']['tireSpecifications'],
                    departureAngle=car_array['result']['departureAngle'],
                    beforeAfterHanging=car_array['result']['beforeAfterHanging'],
                    beforeWheelTrack=car_array['result']['beforeWheelTrack'],
                    afterWheelTrack=car_array['result']['afterWheelTrack'],
                    carLong=car_array['result']['carLong'],
                    carWidth=car_array['result']['name'],
                    carHigh=car_array['result']['carHigh'],
                    crateLong=car_array['result']['crateLong'],
                    crateWidth=car_array['result']['crateWidth'],
                    crateHight=car_array['result']['crateHight'],
                    maxSpeed=car_array['result']['maxSpeed'],
                    carrying=car_array['result']['carrying'],
                    cabCarring=car_array['result']['cabCarring'],
                    turnToType=car_array['result']['turnToType'],
                    trailerTotalQuality=car_array['result']['trailerTotalQuality'],
                    loadQualityFactor=car_array['result']['loadQualityFactor'],
                    semiSaddleBearingQuelity=car_array['result']['semiSaddleBearingQuelity'],
                    engineProducers=car_array['result']['engineProducers'],
                )
                M.save()
            except Exception, e:
                print(e)
                print("error")
            #
            self.ReCall(vin=vin, year="2015", uid=uid, carid=AddCar.id)
            return AddCar.id
        else:
            return False

    def GetCar(self, uid):
        try:
            C = car.objects.filter(user_id=uid).order_by("-id")
        except:
            C = False

        return C

    def ReCall(self, vin, year, uid=None, carid=None):
        IsSetReCall = recall.objects.filter(vin=vin)
        if IsSetReCall.exists():
            return IsSetReCall
        else:
            if not recall_log.objects.filter(vin=vin, user_id=uid).exists():
                InSetLog = recall_log(vin=vin, user_id=uid)
                InSetLog.save()
                LogId = InSetLog.id
            else:
                LogId = False
            RecallUrl = "http://www.dpac.gov.cn/web/vinQuery/vinQuery.do?m=queryVin"
            para = {
                'vin': vin,
                'year': year,
            }
            postData = urllib.urlencode(para)

            req = urllib2.Request(RecallUrl, postData)
            resp = urllib2.urlopen(req).read()
            resp = str(resp).replace("\r\n", "")
            soup = BeautifulSoup.BeautifulSoup(resp)
            soup1 = soup.findAll('table')
            mm = self.makelist(soup1[1])
            print(mm)
            ReArr = []
            for i in range(len(mm)):
                if i <> 0:
                    if mm[i][0] == u"未查询到相关数据":
                        print("不召回")
                    else:
                        ReArr.append(mm[i])
            print(ReArr)
            if len(ReArr) < 1:
                return False
            else:
                for i in range(len(ReArr)):
                    CreateReCall = recall(
                        user_id=uid,
                        car_id=carid,
                        vin=vin,
                        recall_time=ReArr[i][1],
                        factory=ReArr[i][2],
                        cartype=ReArr[i][3],
                        log_id=LogId,
                    )
                    CreateReCall.save()
                return recall.objects.filter(vin=vin)

    def ReCallLog(self, uid):
        Log = recall_log.objects.filter(user_id=uid).order_by("-id")
        return Log

    def makelist(self, table):
        result = []
        allrows = table.findAll('tr')
        for row in allrows:
            result.append([])
            allcols = row.findAll('td')
            for col in allcols:
                thestrings = [unicode(s) for s in col.findAll(text=True)]
                thetext = ''.join(thestrings)
                result[-1].append(thetext)
        return result


# 用户基本信息

class UserClass(object):
    def __init__(self):
        pass

    def GetUser(self, uid):
        try:
            return User.objects.get(id=uid)
        except ObjectDoesNotExist:
            return False

    def SetUser(self, **pam):
        uid = pam['uid']
        real_name = pam['real_name']
        sex = pam['sex']
        email = pam['email']
        idcard = pam['idcard']
        phone = pam['phone']
        addr = pam['addr']

        UpUser = User.objects.get(id=uid)

        UpUser.real_name = real_name
        UpUser.sex = sex
        if email:
            UpUser.email = email
        if phone:
            UpUser.phone = phone
        UpUser.idcard = idcard

        UpUser.addr = addr
        UpUser.save()

        return UpUser.id


# 发送邮件
class KLBSendMail(object):
    def __init__(self):
        pass

    def SendMail(self, to_list, sub, content, t=False):

        mail_host = "smtp.exmail.qq.com"
        mail_user = "service@kalaibao.com"
        mail_pass = "klb139726845"

        if t:
            me = mail_user + "<" + t + ">"
        else:
            me = "卡来宝" + "<" + mail_user + ">"

        msg = MIMEText(content, _subtype='html', _charset='utf-8')
        msg['Subject'] = Header(sub, "utf-8")
        msg['From'] = Header(mail_user, "utf-8")
        msg['To'] = Header(to_list, "utf-8")
        try:

            s = smtplib.SMTP()
            s.connect(mail_host)

            s.ehlo()
            s.starttls()
            s.login(mail_user, mail_pass)
            s.sendmail(me, to_list, msg.as_string())
            s.close()
            print '1'
            return True
        except Exception, e:
            print '2'
            print str(e)
            return False


# 输出JSON数据
class PrintJson(object):
    def __init__(self):
        self._time = str(datetime.datetime.now())
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
平安保险
'''
class PingAn(object):
    def __init__(self):
        #用户名
        self.username = "QHXL-00001"
        #密码
        self.userpwd = "xxxll888"
        #查询类型
        self.SearchType = None
        #返回结果
        self.ReData = None
        #登录的地址
        self.login_page ="https://epcis-nba-ptp.pingan.com/epcisnba/j_security_check"
        #获取用户基本信息
        self.user_info = "https://epcis-nba-ptp.pingan.com/epcisnba/"
        #获取用户信息地址
        self.user = "https://epcis-nba-ptp.pingan.com/epcisnba/quoteandapply/newQuotation.jsp"
        #
        self.bd = "https://epcis-nba-ptp.pingan.com/epcisnba/quickSearch.do"
        #最终结果页
        self.Search_Page = "https://epcis-nba-ptp.pingan.com/epcisnba/quickSearchVoucher.do"


    '''
    查询信息
    参数 c: 查询类型 1为车牌号 2为车架号
    参数 v: 查询值
    '''

    def GetUserInfo(self,c=1,v=''):
        try:
            c = abs(int(c))
            if c==1 or c==2:
                self.SearchType = c
            else:
                self.SearchType = 1
        except:
            self.SearchType = 1
        #获得一个cookieJar实例
        cj = cookielib.CookieJar()
        #cookieJar作为参数，获得一个opener的实例
        opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        #伪装成一个正常的浏览器
        opener.addheaders = [('User-agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36')]
        #生成Post数据，含有登陆用户名密码
        data = urllib.urlencode({"j_username":self.username,"j_password":self.userpwd})
        #以post的方法访问登陆页面，访问之后cookieJar会自定保存cookie
        opener.open(self.login_page,data)

        post_in = {
            'departmentCode': '20121',
            'businessSourceCode': '2',
            'businessSourceDetailCode': '2',
            'channelSourceCode': '9',
            'channelSourceDetailCode': 'V',
            'partnerWorknetCode': 'null',
            'personnelType': '1',
            'isFleet': 'N'
        }
        #
        post_info = {
            'vehicleLicenceCode': v,
            'vehicleFrameNo': '',
            'isSelectedLoanVehicle': '0',
            'departmentCode': '20121',
            'businessSourceCode': '2',
            'businessSourceDetailCode': '2',
            'channelSourceCode': '9',
            'channelSourceDetailCode': 'V',
            'ownershipAttributeCode': '03'
        }
        #
        data = urllib.urlencode(post_info)
        op=opener.open(self.bd,data)
        data = op.read()

        data = unicode(data, 'gbk')
        dataArr = json.loads(data)
        List1 =[]
        List2 = []
        #判断是否有数据返回
        if len(dataArr['data']['quickSearchResult'])<1:
            self.ReData=None
        else:
            #获取商业险往年保单投保列表
            ListC01 = dataArr['data']['quickSearchResult']['C01']
            #获取交强险往年保单投保列表
            ListC51 = dataArr['data']['quickSearchResult']['C51']
            #存放数组
            if ListC01 and len(ListC01)>0:
                for i in ListC01:
                    List1.append(i['policyNo'])
            #存放数组
            if ListC51 and len(ListC51)>0:
                for i in ListC51:
                    List2.append(i['policyNo'])

            QueryID = []
            #
            if len(List1)>0:
                QueryID.append(List1[0])
            #
            if len(List2)>0:
                QueryID.append(List2[0])

            #请求
            QueryPam = {
                'policyNoC51': (len(List2)>0) and List2[0] or '',
                'policyNoC01': (len(List1)>0) and List1[0] or '',
                'departmentCode': '20121',
                'businessSourceCode': '2',
                'businessSourceDetailCode': '2',
                'channelSourceCode': '9',
                'channelSourceDetailCode': 'V',
                'productCode': '',
                'bidFlag': '0',
                'planCode': 'C01',
                'usageAttributeCode': '02',
                'ownershipAttributeCode': '03',
                'isSelectDriver': '0',
                'insuredNumber': '1',
                'loanVehicle': '0',
                'voucherType': '1',
                'nbaHotshot': 'nbaHotshot',
            }

            #最终查询
            PostData = urllib.urlencode(QueryPam)
            Re=opener.open(self.Search_Page,PostData)
            self.ReData = Re.read()
            self.ReData = unicode(self.ReData, 'gbk')

        return self.ReData

#获取VIN
class GetCarVin(object):
    def __init__(self,licenseNo,ownerName):
        self.licenseNo = licenseNo
        self.ownerName = ownerName

    def isInDB(self):
        from bxservice.models import bxcarvin
        DB_IsSet =  bxcarvin.objects.filter(licenseno=self.licenseNo,ownername=self.ownerName)
        if DB_IsSet.count()>0:
            return DB_IsSet.values()[0]
        else:
            return False
    def GetYangGuang(self):
        from bxservice.common import Yo
        try:
            action = Yo(self.licenseNo, self.ownerName)
            err, vin, engine = action.sure()
            VIN={"vin":vin,"engine":engine}
            return VIN
        except:
            return False

#url编码
class UrlCode(object):

    def Encode(self,urldata):
        encode = urllib.urlencode(urldata)
        return encode



