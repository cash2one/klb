# -*-coding:utf-8 -*-
import cookielib
import random
import string
import urllib
import urllib2
import re
import time
import json
import datetime
import base64
import os
import httplib
from django.core.exceptions import ObjectDoesNotExist
from bxservice.models import bxcarvin
from bxservice.models import bxcarinfo
from bxservice.models import bxpriceinfo
from bxservice.models import bxpayinfo
from bxservice.models import citycode
from bxservice.models import bxygpriceinfo
from bxservice.models import bxyghebaoinfo
from bxservice.models import bxzhcallbackinfo
from bxservice.models import bxashebaoinfo
from bxservice.models import bxaspriceinfo
from bxservice.models import bxascallbackinfo
from bxservice.models import bxygcallbackinfo
from bxservice.models import bxzhisread
import hashlib, socket
from Crypto.Cipher import AES
from urllib import unwrap, toBytes, quote, splittype, splithost, splituser, unquote, addinfourl
from bxservice.models import callbaklog

# 获取vin和发动机号
class Yo(object):
    def __init__(self, plate='', name=''):

        # VIN校验
        self.__VIN_VALUE = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'J': 1, 'K': 2,
                            'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9, 'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6,
                            'X': 7, 'Y': 8, 'Z': 9,
                            }

        self.__VIN_WEIGHT = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 10, 10: 9, 11: 8, 12: 7, 13: 6,
                             14: 5, 15: 4, 16: 3, 17: 2,
                             }
        self.__VIN_NO_CONTAIN = ['I', 'O', 'Q']

        # 随机手机号
        self.__PHONE_HEAD = ['133', '153', '180', '181', '189', '177',
                             '130', '131', '132', '155', '156', '145',
                             '185', '186', '176', '178', '188', '147',
                             '134', '135', '136', '137', '138', '139',
                             '150', '151', '152', '157', '158', '159',
                             '182', '183', '184', '187',
                             ]
        self.__PHONE_BASE = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        # 随机邮箱地址
        self.__MAIL_ORG = ['@qq.com', '@126.com', '@163.com', '@sina.com', '@yahoo.com.cn', '@hotmail.com',
                           '@gmail.com', '@souhu.com']
        self.__MAIL_BASE = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                            'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 'd', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                            'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '_', '-']
        # 数据爬取
        self.url = 'http://chexian.sinosig.com/Net/Human_exact.action'
        self.post = {'paraMap.token': "2696",
                     'paraMap.agentCode': "W00110002",
                     'paraMap.orgID': "01682900",
                     'paraMap.spsource': "NET",
                     'paraMap.redirectControl': "1",
                     'paraMap.pageId': "2",
                     'paraMap.isRegist': "1",
                     'paraMap.orgName': "北京市",
                     'initLicence': "京",
                     'paraMap.licence': plate,
                     'paraMap.contactor': name,
                     'paraMap.phone': self.random_phone(),
                     'paraMap.email': self.random_mail(),
                     'paraMap.premiumType': "1",
                     'paraMap.count': "0",
                     'paraMap.integralShow': "1",
                     }
        self.vin = ''
        self.engine = ''
        self.plate = plate
        self.name = name

    def sure(self, repeat=2, delay=1):
        try:
            r = int(repeat)
            t = delay
            while r > 0:
                r -= 1
                e, v, en = self.get_vin_engine()
                if e:
                    return e, v, en
                else:
                    time.sleep(t)
        except Exception, e:

            return False, '', ''

    def random_phone(self, digit=8):
        head = self.__PHONE_HEAD[random.randrange(0, len(self.__PHONE_HEAD))]
        return head + string.join(random.sample(self.__PHONE_BASE, digit)).replace(" ", "")

    def random_mail(self):
        digit = random.randint(1, 32)
        tail = self.__MAIL_ORG[random.randrange(0, len(self.__MAIL_ORG))]
        return string.join(random.sample(self.__MAIL_BASE, digit)).replace(" ", "") + tail

    def get_vin_engine(self):

        plate = self.plate
        name = self.name
        # 检测输入
        # if plate == '' or name == '' or plate[0:3] != '\xe4\xba\xac':
        #     return False, self.vin, self.engine
        # self.post.setdefault('paraMap.licence', plate)
        # self.post.setdefault('paraMap.contactor', name)
        try:
            # 获得一个cookieJar实例
            cj = cookielib.CookieJar()
            # cookieJar作为参数，获得一个opener的实例
            httpHandler = urllib2.HTTPHandler(debuglevel=1)
            httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), httpHandler, httpsHandler)
            # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            # 伪装成一个正常的浏览器
            opener.addheaders = [('User-agent',
                                  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36')]
            data = urllib.urlencode(self.post)
            op = opener.open(self.url, data)
            da = op.read()

            rev = re.search(r'name="paraMap.frameNo" value=[^i]{18}', da)
            if rev is None:
                return False, '', ''
            sv = rev.group()
            self.vin = sv[-17:]

            ree = re.search(r'name="paraMap.engineNo" value=(.*)["]', da)
            if ree is None:
                return False, '', ''
            b = re.search(r'value=([^ ]*)', ree.group())
            if b is None:
                return False, '', ''
            c = re.search(r'="(.*)[^"]', b.group())
            if c is None:
                return False, '', ''
            d = re.search(r'[^=^"](.*)', c.group())
            if d is None:
                return False, '', ''
            self.engine = d.group()

            # print self.vin, self.engine
            if self.verify(self.vin):
                return True, self.vin.upper(), self.engine
            else:
                return False, self.vin, self.engine
        except Exception, e:
            # print e
            return False, self.vin, self.engine

    def verify(self, v=''):
        """
        校验VIN，成功返回True
        """
        vv = str(v).upper()

        for C in self.__VIN_NO_CONTAIN:
            if C in vv:
                return False

        if vv in ('', None):
            return False

        if type(vv) != str:
            return False

        if len(vv) != 17:
            return False

        # 判断第九位校验位是否正确
        count = 0
        ki = 0
        for i in vv:
            ki += 1
            if ki == 9:
                continue
            count += self.__VIN_VALUE[i] * self.__VIN_WEIGHT[ki]
        count %= 11

        if count == 10:
            count = 'X'
        else:
            count = str(count)

        if count == vv[8]:
            return True
        else:
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


class GetCarInfo(object):
    '''
    Value 传入之，可以是vin号码，也可以是车型中文
    searchType 搜索类型 1为VIN，0为车型中文字符串


    '''

    def __init__(self, Value="", searchType=1):
        self.searchType = searchType
        self.Value = Value

        self.GstUrl_YG = "http://chexian.sinosig.com/Partner/netVehicleModel.action?searchCode=%s&searchType=%s&encoding=utf-8&isSeats=1&pageSize=1&&callback=%s" % (
            self.Value, self.searchType, str(int(time.time())))
        # print(self.GstUrl_YG)

    # 网络获得阳光的车型信息
    def GetInfo_YG(self):
        ROWS = self.GetDBSelect(type="sinosig")
        if ROWS:
            return ROWS
        try:
            CarInfoList = urllib.urlopen(self.GstUrl_YG).read()
            # print(CarInfoList)
            CarInfoList = re.sub(r'([a-zA-Z_0-9\.]*\()|(\);?$)', '', CarInfoList)
            CarInfoJson = json.loads(CarInfoList)
            if len(CarInfoJson['rows']) < 1:
                ROWS = False
            else:
                ROWS = CarInfoJson['rows'][0]


        except Exception as e:
            # print(e)
            i_headers = {
                "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5",
                "Accept": "text/plain"
            }
            # CarInfoList = urllib2.urlopen(self.GstUrl_YG, timeout=20)
            CarInfoList = urllib2.Request(self.GstUrl_YG, headers=i_headers)
            CarInfoList = urllib2.urlopen(CarInfoList, timeout=20).read()
            CarInfoList = re.sub(r'([a-zA-Z_0-9\.]*\()|(\);?$)', '', CarInfoList)
            CarInfoJson = json.loads(CarInfoList)
            if len(CarInfoJson['rows']) < 1:
                ROWS = False
            else:
                ROWS = CarInfoJson['rows'][0]
        return ROWS

    # 网络获取安盛的车型信息
    def GetAnshengCarInfo(self, cityCode="340100", pageSize="1", str=False):

        if str:
            V = str
        else:
            CarYG = self.GetInfo_YG()
            # print(CarYG)
            if CarYG == False:
                return False
            V = CarYG['vehiclefgwcode']
        try:
            V = V.replace(")", "")
            V = V.split(".")
            V = V[0]
            V = V.split(" ")
            V = V[0]
            # print(V)
            AnshengUrl = "http://chexian.axatp.com/selectCarInfo.do?cityCode=%s&searchCode=%s&pageSize=%s&encoding=utf-8&page=1&callback=json" % (
                cityCode, V, pageSize)
            CarInfoList = urllib.urlopen(AnshengUrl).read()
            CarInfoList = re.sub(r'([a-zA-Z_0-9\.]*\()|(\);?$)', '', CarInfoList)
            CarInfoJson = json.loads(CarInfoList.decode("GBK"))
            # print(AnshengUrl)
            if len(CarInfoJson['rows']) < 1:
                for i in range(len(V)):
                    V = V[:-i-1]
                    AnshengUrl = "http://chexian.axatp.com/selectCarInfo.do?cityCode=%s&searchCode=%s&pageSize=%s&encoding=utf-8&page=1&callback=json" % (
                        cityCode, V, pageSize)
                    # print(AnshengUrl)
                    CarInfoList = urllib.urlopen(AnshengUrl).read()
                    CarInfoList = re.sub(r'([a-zA-Z_0-9\.]*\()|(\);?$)', '', CarInfoList)
                    CarInfoJson = json.loads(CarInfoList.decode("GBK"))
                    if len(CarInfoJson['rows']) > 0:
                         if self.searchType == 1:
                             GetCarArr = bxcarvin.objects.filter(vin=self.Value)
                             if GetCarArr.count() > 0:
                                 if GetCarArr[0].bxcarinfo_set.filter(key=CarInfoJson['rows'][0]['key'],
                                                                      value=CarInfoJson['rows'][0]['value'],
                                                                      bxtype="axatp").count() < 1:
                                     AddInfo = GetCarArr[0].bxcarinfo_set.create(key=CarInfoJson['rows'][0]['key'],
                                                                                 value=CarInfoJson['rows'][0]['value'],
                                                                                 bxtype="axatp", vehiclefgwcode=V)
                                     AddInfo.save()
                             return CarInfoJson['rows'][0]
            else:
                if self.searchType == 1:
                             GetCarArr = bxcarvin.objects.filter(vin=self.Value)
                             if GetCarArr.count() > 0:
                                 if GetCarArr[0].bxcarinfo_set.filter(key=CarInfoJson['rows'][0]['key'],
                                                                      value=CarInfoJson['rows'][0]['value'],
                                                                      bxtype="axatp").count() < 1:
                                     AddInfo = GetCarArr[0].bxcarinfo_set.create(key=CarInfoJson['rows'][0]['key'],
                                                                                 value=CarInfoJson['rows'][0]['value'],
                                                                                 bxtype="axatp", vehiclefgwcode=V)
                                     AddInfo.save()
                             return CarInfoJson['rows'][0]
        except:
            return False

    def GetAnshengCarInfoNEW(self, cityCode="340100", pageSize="1", str=False):

        if str:
            V = str
        else:
            CarYG = self.GetInfo_YG()
            # print(CarYG)
            if CarYG == False:
                return False
            V = CarYG['vehiclefgwcode']
            # print(V)
            D = CarYG['key']
            # print(D)
        try:
            # V = V.replace(")", "")
            # V = V.split(".")
            # V = V[0]
            # V = V.split(" ")
            # V = V[0]
            # print(V)
            # AnshengUrl = "http://chexian.axatp.com/selectCarInfo.do?cityCode=%s&searchCode=%s&pageSize=%s&encoding=utf-8&page=1&callback=json" % (
            #     cityCode, V, pageSize)
            AnshengUrl = "http://chexian.axatp.com/ajaxCarBrandSelect.do?operation=configByInput&searchCode=%s&cityCode=%s&firstRegisterDate=&ecInsureId=F9A4168E5B47C8FABEE62B61F8D561FA7C91A135ABAB76F5&isRenewal=&isAgent=0&localProvinceCode=&planDefineId=3&rt=" % (
                 V,cityCode)
            CarInfoList = urllib.urlopen(AnshengUrl).read()
            # CarInfoList = re.sub(r'([a-zA-Z_0-9\.]*\()|(\);?$)', '', CarInfoList)
            CarInfoJson = json.loads(CarInfoList.decode("GBK"))
            # print(AnshengUrl)
            # print(D)
            # print(CarInfoJson['data'])
            if len(CarInfoJson['data']) < 1:
                for i in range(len(V)):
                    V = V[:-i-1]
                    # AnshengUrl = "http://chexian.axatp.com/selectCarInfo.do?cityCode=%s&searchCode=%s&pageSize=%s&encoding=utf-8&page=1&callback=json" % (
                    #     cityCode, V, pageSize)
                    AnshengUrl = "http://chexian.axatp.com/ajaxCarBrandSelect.do?operation=configByInput&searchCode=%s&cityCode=%s&firstRegisterDate=&ecInsureId=F9A4168E5B47C8FABEE62B61F8D561FA7C91A135ABAB76F5&isRenewal=&isAgent=0&localProvinceCode=&planDefineId=3&rt=" % (
                    V,cityCode)
                    print(AnshengUrl)
                    CarInfoList = urllib.urlopen(AnshengUrl).read()
                    CarInfoList = re.sub(r'([a-zA-Z_0-9\.]*\()|(\);?$)', '', CarInfoList)
                    CarInfoJson = json.loads(CarInfoList.decode("GBK"))
                    if len(CarInfoJson['data']) > 0:
                         if self.searchType == 1:
                             GetCarArr = bxcarvin.objects.filter(vin=self.Value)
                             if GetCarArr.count() > 0:
                                 for i in range(len(CarInfoJson['data'])):
                                     if CarInfoJson['data'][i]['rbCode'] == D:
                                         if GetCarArr[0].bxcarinfo_set.filter(key=CarInfoJson['data'][i]['id'],
                                                                              value=CarInfoJson['data'][i]['name'],
                                                                              bxtype="axatp").count() < 1:
                                             AddInfo = GetCarArr[0].bxcarinfo_set.create(key=CarInfoJson['data'][i]['id'],
                                                                                         value=CarInfoJson['data'][i]['name'],
                                                                                         bxtype="axatp", vehiclefgwcode=V)
                                             AddInfo.save()
                                         return CarInfoJson['data'][i]
            else:
                if self.searchType == 1:
                             GetCarArr = bxcarvin.objects.filter(vin=self.Value)
                             if GetCarArr.count() > 0:
                                 for i in range(len(CarInfoJson['data'])):
                                      if CarInfoJson['data'][i]['rbCode'] == D:
                                         if GetCarArr[0].bxcarinfo_set.filter(key=CarInfoJson['data'][i]['id'],
                                                                              value=CarInfoJson['data'][i]['name'],
                                                                              bxtype="axatp").count() < 1:
                                             AddInfo = GetCarArr[0].bxcarinfo_set.create(key=CarInfoJson['data'][i]['id'],
                                                                                         value=CarInfoJson['data'][i]['name'],
                                                                                         bxtype="axatp", vehiclefgwcode=V)
                                             AddInfo.save()
                                             return CarInfoJson['data'][i]
        except:
            return False
    # 直接从数据库读取车型信息
    def GetDBSelect(self, type=""):

        GetCarArr = bxcarvin.objects.filter(vin=self.Value)
        if GetCarArr.count() < 1:
            return False
        Info = GetCarArr[0].bxcarinfo_set.filter(bxtype=type)
        if Info.count() < 1:
            return False
        else:
            CarInfo = Info.values()[0]
            return CarInfo


class FengChaoCrypt(object):
    def AESencrypt(self, plaintext='', password='fengchao', base64=False):

        SALT_LENGTH = 32
        DERIVATION_ROUNDS = 1337
        BLOCK_SIZE = 16
        KEY_SIZE = 32
        MODE = AES.MODE_CBC

        salt = os.urandom(SALT_LENGTH)
        iv = os.urandom(BLOCK_SIZE)

        paddingLength = 16 - (len(plaintext) % 16)
        paddedPlaintext = plaintext + chr(paddingLength) * paddingLength
        derivedKey = password
        for i in range(0, DERIVATION_ROUNDS):
            derivedKey = hashlib.sha256(derivedKey + salt).digest()
        derivedKey = derivedKey[:KEY_SIZE]
        cipherSpec = AES.new(derivedKey, MODE, iv)
        ciphertext = cipherSpec.encrypt(paddedPlaintext)
        ciphertext = ciphertext + iv + salt
        if base64:
            import base64
            return base64.b64encode(ciphertext)
        else:
            return ciphertext.encode("hex")

    def AESdecrypt(self, ciphertext='', password='fengchao', base64=False):
        import hashlib
        from Crypto.Cipher import AES
        SALT_LENGTH = 32
        DERIVATION_ROUNDS = 1337
        BLOCK_SIZE = 16
        KEY_SIZE = 32
        MODE = AES.MODE_CBC

        if base64:
            import base64
            decodedCiphertext = base64.b64decode(ciphertext)
        else:
            decodedCiphertext = ciphertext.decode("hex")
        startIv = len(decodedCiphertext) - BLOCK_SIZE - SALT_LENGTH
        startSalt = len(decodedCiphertext) - SALT_LENGTH
        data, iv, salt = decodedCiphertext[:startIv], decodedCiphertext[startIv:startSalt], decodedCiphertext[
                                                                                            startSalt:]
        derivedKey = password
        for i in range(0, DERIVATION_ROUNDS):
            derivedKey = hashlib.sha256(derivedKey + salt).digest()
        derivedKey = derivedKey[:KEY_SIZE]
        cipherSpec = AES.new(derivedKey, MODE, iv)
        plaintextWithPadding = cipherSpec.decrypt(data)
        paddingLength = ord(plaintextWithPadding[-1])
        plaintext = plaintextWithPadding[:-paddingLength]
        return plaintext


# 操作数据库
class BXDBAction(object):
    def __init__(self):
        pass

    # 保存计算价格需要的信息
    def CreateCarVin(self, licenseno="", ownername="", citycode="", vin="", engine="", user_id=''):

        InDB = {"licenseno": licenseno,
                "ownername": ownername,
                "vin": vin,
                "engine": engine,
                "citycode": citycode}

        AA,BB = bxcarvin.objects.get_or_create(**InDB)

        return AA.id

    # 车型信息
    def CreateCarInfo(self, user_id="", car_id="", key="", vehiclefgwcode="", value="", bxtype=""):

        if bxcarinfo.objects.filter(key=key, car_id=car_id).count() < 1:
            InDB = {"car_id": car_id,
                    "key": key,
                    "vehiclefgwcode": vehiclefgwcode,
                    "value": value,
                    "bxtype": bxtype
                    }
            if user_id and user_id <> "":
                InDB['user_id'] = user_id
            print(InDB)
            print(1111)
            CreateInfo = bxcarinfo.objects.create(**InDB)
            if user_id and user_id <> "":
                CreateInfo.user_id = user_id
            CreateInfo.save()
            return CreateInfo.id
        else:
            return False

    # 判断是否已经存在车辆信息
    def IsSet(self, licenseno="", citycode="", ownername="",id=False):

        if id:
            try:
                R = bxcarvin.objects.get(id=id)
            except ObjectDoesNotExist:
                R = False
            return R

        else:
            Car = bxcarvin.objects.filter(licenseno=licenseno, citycode=citycode, ownername=ownername)
            if Car.exists():
                CarDict = Car.values()[0]
                return CarDict
            else:
                return False

    def ReCarInfo(self, cid, bx="sinosig"):

        GetInfoArr = bxcarinfo.objects.filter(car_id=cid, bxtype=bx)
        if GetInfoArr.exists():
            GetInfoArr = GetInfoArr.values()[0]
            return GetInfoArr
        else:
            return False

    # 将车辆投保算价所需信息写入数据库
    def CreateTBSJinfo(
            self,
            licenseno="",
            order_id="",
            biz_begin_date="",
            biz_end_date="",
            traff_begin_date="",
            traff_end_date="",
            cs_traff_amt="",
            dq_traff_amt="",
            zr_traff_amt="",
            first_register_date="",
            bxtype="cic",
            idcode=""):

        # 查询是否已有这辆车，如果有，拿出车辆id
        GetCarVin = bxcarvin.objects.filter(licenseno=licenseno)
        if GetCarVin.count() > 0:
            car_id = GetCarVin.values()[0]['id']

            # 判断信息是否已经存在
            IsSetVal = bxpriceinfo.objects.filter(car_id=car_id, bxtype=bxtype)
            if IsSetVal.count() < 1:
                InUPCarVINbase = bxcarvin.objects.get(id=car_id)
                InUPCarVINbase.idcode = idcode
                InUPCarVINbase.save()

                CreateInfo = bxpriceinfo.objects.create(
                    car_id=car_id,
                    order_id=order_id,
                    biz_begin_date=biz_begin_date,
                    biz_end_date=biz_end_date,
                    traff_begin_date=traff_begin_date,
                    traff_end_date=traff_end_date,
                    cs_traff_amt=cs_traff_amt,
                    dq_traff_amt=dq_traff_amt,
                    zr_traff_amt=zr_traff_amt,
                    first_register_date=first_register_date,
                    bxtype=bxtype)
                CreateInfo.save()
                return CreateInfo.id
            else:

                return True

        # 如果没有查询到车辆，则返回False
        else:
            # print("建立投保信息时没有找到车辆")
            return False

    # 查询投保算价所需要的信息
    def GetTBSJinfo(self, licenseno="", bxtype=""):
        GetCarVin = bxcarvin.objects.filter(licenseno=licenseno)
        if GetCarVin.count() < 1:
            return False
        else:
            CarID = GetCarVin.values()[0]['id']
            GetInfo = bxpriceinfo.objects.filter(car_id=CarID, bxtype=bxtype)
            if GetInfo.count() < 1:
                return False
            else:
                GetInfo = GetInfo.values()[0]
                GetCar = GetCarVin.values()[0]

                return GetCar, GetInfo
    # 中华报价信息
    def CreatPriceinfo_zh(self,**pam):
        GetCar = bxcarvin.objects.get(vin=pam['vin'],ownername=pam['ownername'])
        IsSet= GetCar.bxzhpriceinfo_set.exists()
        if IsSet:
            GetCar.bxzhpriceinfo_set.update(
                            biztotalpremium = pam['biztotalpremium'],
                            vehicletaxpremium = pam['vehicletaxpremium'],
                            forcepremium = pam['forcepremium'],
                            bizbegindate = pam['bizbegindate'],
                            forcebegindate = pam['forcebegindate'],
                            kind_030004 = pam['kind_030004'],
                            kind_030006 = pam['kind_030006'],
                            kind_030012 = pam['kind_030012'],
                            kind_030018 = pam['kind_030018'],
                            kind_030025 = pam['kind_030025'],
                            kind_030059 = pam['kind_030059'],
                            kind_030065 = pam['kind_030065'],
                            kind_030070 = pam['kind_030070'],
                            kind_030072 = pam['kind_030072'],
                            kind_030106 = pam['kind_030106'],
                            kind_030125 = pam['kind_030125'],
                            kind_031901 = pam['kind_031901'],
                            kind_031902 = pam['kind_031902'],
                            kind_031903 = pam['kind_031903'],
                            kind_031911 = pam['kind_031911'],
                            kind_033531 = pam['kind_033531'],
                            kind_033532 = pam['kind_033532'],
                            kind_033535 = pam['kind_033535'],
                            )
        else:
            CreatINFO = GetCar.bxzhpriceinfo_set.create(
                            biztotalpremium = pam['biztotalpremium'],
                            vehicletaxpremium = pam['vehicletaxpremium'],
                            forcepremium = pam['forcepremium'],
                            bizbegindate = pam['bizbegindate'],
                            forcebegindate = pam['forcebegindate'],
                            kind_030004 = pam['kind_030004'],
                            kind_030006 = pam['kind_030006'],
                            kind_030012 = pam['kind_030012'],
                            kind_030018 = pam['kind_030018'],
                            kind_030025 = pam['kind_030025'],
                            kind_030059 = pam['kind_030059'],
                            kind_030065 = pam['kind_030065'],
                            kind_030070 = pam['kind_030070'],
                            kind_030072 = pam['kind_030072'],
                            kind_030106 = pam['kind_030106'],
                            kind_030125 = pam['kind_030125'],
                            kind_031901 = pam['kind_031901'],
                            kind_031902 = pam['kind_031902'],
                            kind_031903 = pam['kind_031903'],
                            kind_031911 = pam['kind_031911'],
                            kind_033531 = pam['kind_033531'],
                            kind_033532 = pam['kind_033532'],
                            kind_033535 = pam['kind_033535'],
            )
            CreatINFO.save()
    # 回调浮动告知单
    def IsRead(self,flag,orderno='0',businesscode=''):
        GetInfo = bxpayinfo.objects.get(order_id=orderno)
        Is = GetInfo.bxzhisread_set.exists()
        if Is:
            if businesscode == '11':
                GetInfo.bxzhisread_set.update(
                                        orderno=orderno,
                                        businesscode_biz = "11",
                                        businesscode_force = ""
                )
            if businesscode == '12':
                GetInfo.bxzhisread_set.update(
                                        orderno=orderno,
                                        businesscode_force = "12"
                )
        else:
            if businesscode == '11':
                IsReadIN = GetInfo.bxzhisread_set.create(
                                        orderno=orderno,
                                        flag = flag,
                                        businesscode_biz = businesscode,
                                        businesscode_force = ""
                )
                IsReadIN.save()
            if businesscode == '12':
                IsReadIN = GetInfo.bxzhisread_set.create(
                                        orderno=orderno,
                                        flag = flag,
                                        businesscode_biz = "",
                                        businesscode_force = businesscode
                )
                IsReadIN.save()
    # 读取浮动告知单信息
    def GetRead(self,orderno,M):
        try:
            GetInfo = bxzhisread.objects.get(orderno=orderno)
        except:
            RE = {'error':'1','msg':'请阅读商业险浮动告知单或交强险浮动告知单并点击确认'}
            return RE
        if M == "11":
            if GetInfo.businesscode_biz == "11":
                RE = {'error':'0','msg':'1'}
                return RE
            else:
                RE = {'error':'1','msg':'请阅读商业险浮动告知单并点击确认'}
                return RE
        if M == '12':
            if GetInfo.businesscode_force == "12":
                RE = {'error':'0','msg':'1'}
                return RE
            else:
                RE = {'error':'1','msg':'请阅读交强险浮动告知单并点击确认'}
                return RE
        else:
            RE = {'error':'1','msg':'请阅读商业险浮动告知单或交强险浮动告知单并点击确认'}
            return RE
    # 中华核保信息
    def CreatePayInfo(self, **pam):
        try:
            GetCar = bxcarvin.objects.get(vin=pam['vin'],ownername=pam['C_IDET_NAME'])
            if pam['flag']:
                CreateInfoIsSet = GetCar.bxpayinfo_set.filter(app_name=pam['C_APP_NAME']).exists()
                if CreateInfoIsSet:
                    GetCar.bxpayinfo_set.update(
                        session_id=pam['Session_ID'],
                        order_id=pam['ORDER_ID'],
                        app_name=pam['C_APP_NAME'],
                        app_ident_no=pam['C_APP_IDENT_NO'],
                        app_tel=pam['C_APP_TEL'],
                        app_addr=pam['C_APP_ADDR'],
                        app_email=pam['C_APP_EMAIL'],
                        insrnt_name=pam['C_INSRNT_NME'],
                        insrnt_ident_no=pam['C_INSRNT_IDENT_NO'],
                        insrnt_tel=pam['C_INSRNT_TEL'],
                        insrnt_addr=pam['C_INSRNT_ADDR'],
                        insrnt_email=pam['C_INSRNT_EMAIL'],
                        contact_name=pam['C_CONTACT_NAME'],
                        address=pam['C_ADDRESS'],
                        contact_tel=pam['C_CONTACT_TEL'],
                        idet_name=pam['C_IDET_NAME'],
                        ident_no=pam['C_IDENT_NO'],
                        delivery_province=pam['C_DELIVERY_PROVINCE'],
                        delivery_city=pam['C_DELIVERY_CITY'],
                        delivery_district=pam['C_DELIVERY_DISTRICT'],
                        bxgs_type=pam['bxgs_type'],
                        status=pam['status'],
                    )
                else:
                    CreateInfo = GetCar.bxpayinfo_set.create(
                        session_id=pam['Session_ID'],
                        order_id=pam['ORDER_ID'],
                        app_name=pam['C_APP_NAME'],
                        app_ident_no=pam['C_APP_IDENT_NO'],
                        app_tel=pam['C_APP_TEL'],
                        app_addr=pam['C_APP_ADDR'],
                        app_email=pam['C_APP_EMAIL'],
                        insrnt_name=pam['C_INSRNT_NME'],
                        insrnt_ident_no=pam['C_INSRNT_IDENT_NO'],
                        insrnt_tel=pam['C_INSRNT_TEL'],
                        insrnt_addr=pam['C_INSRNT_ADDR'],
                        insrnt_email=pam['C_INSRNT_EMAIL'],
                        address=pam['C_ADDRESS'],
                        contact_tel=pam['C_CONTACT_TEL'],
                        idet_name=pam['C_IDET_NAME'],
                        ident_no=pam['C_IDENT_NO'],
                        delivery_province=pam['C_DELIVERY_PROVINCE'],
                        delivery_city=pam['C_DELIVERY_CITY'],
                        delivery_district=pam['C_DELIVERY_DISTRICT'],
                        businesscode=pam['businesscode'],
                        bxgs_type=pam['bxgs_type'],
                    )
                    CreateInfo.save()
            else:
                IsSet = GetCar.bxpayinfo_set.exists()
                if IsSet:
                    GetCar.bxpayinfo_set.update(
                        c_proposal_no_biz = pam['c_proposal_no_biz'],
                        c_proposal_no_force = pam['c_proposal_no_force']
                    )
                else:
                    return False


        except ObjectDoesNotExist:
            return False

    # 中华回调信息
    def CreateCallback(self, **pam):
        GetInfo = bxpayinfo.objects.get(order_id=pam['ORDER_ID'])
        print(GetInfo.app_name)
        InfoIs =  GetInfo.bxzhcallbackinfo_set.exists()
        if InfoIs:
            GetInfo.bxzhcallbackinfo_set.update(
                chengbao_staus=pam['C_STAUS'],
                message=pam['C_MESSAGE'],
                biz_policy_no=pam['C_POLICY_NO_BIZ'],
                force_policy_no=pam['C_POLICY_NO_FORCE'],
            )
        else:
            CreateInfo = GetInfo.bxzhcallbackinfo_set.create(
                order_id=pam['ORDER_ID'],
                pay_transn = pam['C_PAY_TRANSNO'],
                pay_amt=pam['C_PAY_AMT'],
                pay_staus=pam['C_PAY_STAUS'],
                pay_desc=pam['C_DESC'],
                chengbao_staus=pam['C_STAUS'],
                message=pam['C_MESSAGE'],
                biz_policy_no=pam['C_POLICY_NO_BIZ'],
                force_policy_no=pam['C_POLICY_NO_FORCE'],
                businesscode=pam['BusinessCode']
            )
            CreateInfo.save()
    def SelectPayInfo(self, vin=""):
        ENCODE = FengChaoCrypt()
        try:
            vin = ENCODE.AESdecrypt(vin)
        except:
            vin = False
        if vin:
            GetCar = bxcarvin.objects.get(vin=vin)
            PayInfoArr = GetCar.bxpayinfo_set
            if PayInfoArr.count() > 0:
                PayInfo = PayInfoArr.values()[0]
                return PayInfo
            else:
                return False

    # 查看订单状态
    # 返回1是可以去支付，0是不能支付,False订单不存在
    def OrderIDStatus(self, orderid=""):
        try:
            S = bxpayinfo.objects.get(order_id=orderid)

            return S.status
        except ObjectDoesNotExist:
            return False

    # 安盛核保信息
    def CreatPayinfo_AS(self, **pam):
        if pam['ID'] <> "" and pam['ID'] <> None:
            GetCar = bxcarvin.objects.get(id=pam['ID'])
        else:
            GetCar = bxcarvin.objects.get(vin=pam['vin'],ownername=pam['ownername'])
        CreateInfoIsSet = GetCar.bxashebaoinfo_set.exists()
        if CreateInfoIsSet:
            GetCar.bxashebaoinfo_set.update(
                                            tborder_id=pam['tborder_id'],
                                            item_id=pam['item_id'],
                                            insuredname=pam['insuredname'],
                                            insuredidno=pam['insuredidno'],
                                            insuredmobile=pam['insuredmobile'],
                                            insuredidtype=pam['insuredidtype'],
                                            insuredgender=pam['insuredgender'],
                                            insuredbirthday=pam['insuredbirthday'],
                                            ownername=pam['ownername'],
                                            owneridno=pam['owneridno'],
                                            ownermobile=pam['ownermobile'],
                                            owneremail=pam['owneremail'],
                                            owneridtype=pam['owneridtype'],
                                            ownergender=pam['ownergender'],
                                            ownerbirthday=pam['ownerbirthday'],
                                            ownerage=pam['ownerage'],
                                            addresseename=pam['addresseename'],
                                            addresseemobile=pam['addresseemobile'],
                                            addresseeprovince=pam['addresseeprovince'],
                                            addresseecity=pam['addresseecity'],
                                            addresseetown=pam['addresseetown'],
                                            addresseedetails=pam['addresseedetails'],
                                            applicantname=pam['applicantname'],
                                            applicantidno=pam['applicantidno'],
                                            applicantmobile=pam['applicantmobile'],
                                            applicantemail=pam['applicantemail'],
                                            applicantbirthday=pam['applicantbirthday'],
                                            applicantgender=pam['applicantgender'],
                                            applicantidtype=pam['applicantidtype'],
                                            bxgs_type=pam['bxgs_type'],
                                            status = pam['status'],
                                            session_id = pam['session_id'],
                                            proposalno_biz=pam['proposalno_biz'],
                                            proposalno_force=pam['proposalno_force']
                                            )
        else:
            CreateInfo = GetCar.bxashebaoinfo_set.create(
                                                    tborder_id=pam['tborder_id'],
                                                    item_id=pam['item_id'],
                                                    insuredname=pam['insuredname'],
                                                    insuredidno=pam['insuredidno'],
                                                    insuredmobile=pam['insuredmobile'],
                                                    insuredidtype=pam['insuredidtype'],
                                                    insuredgender=pam['insuredgender'],
                                                    insuredbirthday=pam['insuredbirthday'],
                                                    ownername=pam['ownername'],
                                                    owneridno=pam['owneridno'],
                                                    ownermobile=pam['ownermobile'],
                                                    owneremail=pam['owneremail'],
                                                    owneridtype=pam['owneridtype'],
                                                    ownergender=pam['ownergender'],
                                                    ownerbirthday=pam['ownerbirthday'],
                                                    ownerage=pam['ownerage'],
                                                    addresseename=pam['addresseename'],
                                                    addresseemobile=pam['addresseemobile'],
                                                    addresseeprovince=pam['addresseeprovince'],
                                                    addresseecity=pam['addresseecity'],
                                                    addresseetown=pam['addresseetown'],
                                                    addresseedetails=pam['addresseedetails'],
                                                    applicantname=pam['applicantname'],
                                                    applicantidno=pam['applicantidno'],
                                                    applicantmobile=pam['applicantmobile'],
                                                    applicantemail=pam['applicantemail'],
                                                    applicantbirthday=pam['applicantbirthday'],
                                                    applicantgender=pam['applicantgender'],
                                                    applicantidtype=pam['applicantidtype'],
                                                    bxgs_type=pam['bxgs_type'],
                                                    status = pam['status'],
                                                    session_id = pam['session_id'],
                                                    proposalno_biz=pam['proposalno_biz'],
                                                    proposalno_force=pam['proposalno_force']
                                                    )
            CreateInfo.save()

    # 安盛报价信息
    def CraetPriceinfo_as(self, **pam):
        for n, v in pam.iteritems():
            if n <> "BizFlag" and n <> "FroceFlag" and n <>"bizbegindate" and n <>"forcebegindate" \
                    and n <>"vin" and n <>"biztotalpremium" and n <>"totalpremium" and n <>"standardpremium" \
                    and n <>"forcepremium" and n <>"cov_600" and n <>"cov_701" and n <>"cov_702"\
                    and n <>"vehicletaxpremium" and n <>"forcepremium_f" and n <>"session_id" and n<> "ownername":
                if float(v) > float(0):
                    pam[n] = 1
        GetCar = bxcarvin.objects.get(vin=pam['vin'],ownername=pam['ownername'])
        CreateInfoIsSet = GetCar.bxaspriceinfo_set.exists()
        if CreateInfoIsSet:
            GetCar.bxaspriceinfo_set.update(
                        bizflag=pam['BizFlag'],
                        forceflag=pam['FroceFlag'],
                        cov_200=pam['cov_200'],
                        cov_600=pam['cov_600'],
                        cov_701=pam['cov_701'],
                        cov_702=pam['cov_702'],
                        cov_500=pam['cov_500'],
                        cov_290=pam['cov_290'],
                        cov_231=pam['cov_231'],
                        cov_210=pam['cov_210'],
                        cov_310=pam['cov_310'],
                        cov_900=pam['cov_900'],
                        cov_910=pam['cov_910'],
                        cov_911=pam['cov_911'],
                        cov_912=pam['cov_912'],
                        cov_921=pam['cov_921'],
                        cov_922=pam['cov_922'],
                        cov_923=pam['cov_923'],
                        cov_924=pam['cov_924'],
                        cov_928=pam['cov_928'],
                        cov_929=pam['cov_929'],
                        cov_930=pam['cov_930'],
                        cov_931=pam['cov_931'],
                        biztotalpremium=pam['biztotalpremium'],
                        totalpremium=pam['totalpremium'],
                        standardpremium=pam['standardpremium'],
                        forcepremium=pam['forcepremium'],
                        bizbegindate=pam['bizbegindate'],
                        forcebegindate=pam['forcebegindate'],
                        forcepremium_f=pam['forcepremium_f'],
                        vehicletaxpremium = pam['vehicletaxpremium'],
                        session_id= pam['session_id']
                    )
        else:
            CreateInfo = GetCar.bxaspriceinfo_set.create(
                        bizflag=pam['BizFlag'],
                        forceflag=pam['FroceFlag'],
                        cov_200=pam['cov_200'],
                        cov_600=pam['cov_600'],
                        cov_701=pam['cov_701'],
                        cov_702=pam['cov_702'],
                        cov_500=pam['cov_500'],
                        cov_290=pam['cov_290'],
                        cov_231=pam['cov_231'],
                        cov_210=pam['cov_210'],
                        cov_310=pam['cov_310'],
                        cov_900=pam['cov_900'],
                        cov_910=pam['cov_910'],
                        cov_911=pam['cov_911'],
                        cov_912=pam['cov_912'],
                        cov_921=pam['cov_921'],
                        cov_922=pam['cov_922'],
                        cov_923=pam['cov_923'],
                        cov_924=pam['cov_924'],
                        cov_928=pam['cov_928'],
                        cov_929=pam['cov_929'],
                        cov_930=pam['cov_930'],
                        cov_931=pam['cov_931'],
                        biztotalpremium=pam['biztotalpremium'],
                        totalpremium=pam['totalpremium'],
                        standardpremium=pam['standardpremium'],
                        bizbegindate=pam['bizbegindate'],
                        forcebegindate=pam['forcebegindate'],
                        forcepremium = pam['forcepremium'],
                        forcepremium_f=pam['forcepremium_f'],
                        vehicletaxpremium = pam['vehicletaxpremium'],
                        session_id= pam['session_id']
                    )
            CreateInfo.save()

    def GetPriceinfo_as(self, vin="",ownername='',ID=""):
        try:
            if ID <> "" and ID <> None:
                GetCar = bxcarvin.objects.get(id=ID)
            else:
                GetCar = bxcarvin.objects.get(vin=vin,ownername=ownername)
        except:
            return False
        PriceinfoIsSet = GetCar.bxaspriceinfo_set.exists()
        if PriceinfoIsSet:
            CarInfo = GetCar.bxaspriceinfo_set.get()
            return CarInfo
        else:
            return False
        # 安盛回调信息存储
    def CreatCallBack_as(self,**pam):
        GetInfo = bxashebaoinfo.objects.get(session_id=pam['sessionid'])
        CreateInfoIsSet = GetInfo.bxascallbackinfo_set.exists()
        if CreateInfoIsSet:
            GetInfo.bxascallbackinfo_set.update(
                                            sessionid=pam['sessionid'],
                                            requesttype=pam['requesttype'],
                                            tborderid=pam['tborderid'],
                                            premium=pam['premium'],
                                            itemid=pam['itemid'],
                                            bizpremium=pam['bizpremium'],
                                            bizproposalno=pam['bizproposalno'],
                                            bizpolicyno=pam['bizpolicyno'],
                                            forcepremium=pam['forcepremium'],
                                            forceproposalno = pam['forceproposalno'],
                                            forcepolicyno = pam['forcepolicyno'],
                                            status = pam['status']
                                             )
        else:
            CrestInfo= GetInfo.bxascallbackinfo_set.create(
                                            sessionid=pam['sessionid'],
                                            requesttype=pam['requesttype'],
                                            tborderid=pam['tborderid'],
                                            premium=pam['premium'],
                                            itemid=pam['itemid'],
                                            bizpremium=pam['bizpremium'],
                                            bizproposalno=pam['bizproposalno'],
                                            bizpolicyno=pam['bizpolicyno'],
                                            forcepremium=pam['forcepremium'],
                                            forceproposalno = pam['forceproposalno'],
                                            forcepolicyno = pam['forcepolicyno'],
                                            status = pam['status']
                                             )
            CrestInfo.save()

    def CreatPriceinfo_yg(self,**pam):
        GetCar = bxcarvin.objects.get(vin=pam['vin'],ownername=pam['ownername'])
        CreateInfoIsSet = GetCar.bxygpriceinfo_set.exists()
        if CreateInfoIsSet:
            GetCar.bxygpriceinfo_set.update(
                forceflag=pam['forceflag'],
                cov_200=pam['cov_200'],
                cov_600=pam['cov_600'],
                cov_701=pam['cov_701'],
                cov_702=pam['cov_702'],
                cov_500=pam['cov_500'],
                cov_291=pam['cov_291'],
                cov_231=pam['cov_231'],
                cov_210=pam['cov_210'],
                cov_310=pam['cov_310'],
                cov_390=pam['cov_390'],
                cov_640=pam['cov_640'],
                cov_911=pam['cov_911'],
                cov_912=pam['cov_912'],
                cov_921=pam['cov_921'],
                cov_922=pam['cov_922'],
                cov_928=pam['cov_928'],
                cov_929=pam['cov_929'],
                biztotalpremium=pam['biztotalpremium'], # 商业保费
                totalpremium=pam['totalpremium'],  # 网购价
                standardpremium=pam['standardpremium'], # 市场价
                forcepremium=pam['forcepremium'], # 交强险
                bizbegindate=pam['bizbegindate'], # 商业险起期
                forcebegindate=pam['forcebegindate'], # 交强险起期
                forceotalpremium=pam['forceotalpremium'], # 交强总保费
                vehicletaxpremium=pam['vehicletaxpremium'],
                session_id=pam['session_id']
            )
        else:
            CreateInfo = GetCar.bxygpriceinfo_set.create(
                forceflag=pam['forceflag'],
                cov_200=pam['cov_200'],
                cov_600=pam['cov_600'],
                cov_701=pam['cov_701'],
                cov_702=pam['cov_702'],
                cov_500=pam['cov_500'],
                cov_291=pam['cov_291'],
                cov_231=pam['cov_231'],
                cov_210=pam['cov_210'],
                cov_310=pam['cov_310'],
                cov_390=pam['cov_390'],
                cov_640=pam['cov_640'],
                cov_911=pam['cov_911'],
                cov_912=pam['cov_912'],
                cov_921=pam['cov_921'],
                cov_922=pam['cov_922'],
                cov_928=pam['cov_928'],
                cov_929=pam['cov_929'],
                biztotalpremium=pam['biztotalpremium'],  # 商业保费
                totalpremium=pam['totalpremium'],  # 网购价
                standardpremium=pam['standardpremium'],  # 市场价
                forcepremium=pam['forcepremium'],  # 交强险
                bizbegindate=pam['bizbegindate'],  # 商业险起期
                forcebegindate=pam['forcebegindate'],  # 交强险起期
                forceotalpremium=pam['forceotalpremium'],  # 交强总保费
                vehicletaxpremium=pam['vehicletaxpremium'],
                session_id=pam['session_id']
            )
            CreateInfo.save()
    def CreatPayinfo_yg(self,**pam):
        GetCar = bxcarvin.objects.get(vin=pam['vin'],ownername=pam['ownername'])
        CreateInfoIsSet = GetCar.bxyghebaoinfo_set.exists()
        if CreateInfoIsSet:
            GetCar.bxyghebaoinfo_set.update(
                tborder_id=pam['tborder_id'],
                item_id=pam['item_id'],
                insuredname=pam['insuredname'],
                insuredidno=pam['insuredidno'],
                insuredmobile=pam['insuredmobile'],
                insuredemail = pam['insuredemail'],
                ownername=pam['ownername'],
                owneridno=pam['owneridno'],
                ownermobile=pam['ownermobile'],
                owneremail=pam['owneremail'],
                addresseename=pam['addresseename'],
                addresseemobile=pam['addresseemobile'],
                senddate=pam['senddate'],
                addresseeprovince=pam['addresseeprovince'],
                addresseecity=pam['addresseecity'],
                addresseetown=pam['addresseetown'],
                addresseedetails=pam['addresseedetails'],
                applicantname=pam['applicantname'],
                applicantidno=pam['applicantidno'],
                applicantmobile=pam['applicantmobile'],
                applicantemail=pam['applicantemail'],
                insuredaddresseeDetails = pam['insuredaddresseeDetails'], # 被保险人身份证地址
                bxgs_type=pam['bxgs_type'],
                status=pam['status'],
                session_id=pam['session_id'],
                proposalno_biz=pam['proposalno_biz'],
                proposalno_force=pam['proposalno_force']
            )
        else:
            CreateInfo = GetCar.bxyghebaoinfo_set.create(
                tborder_id=pam['tborder_id'],
                item_id=pam['item_id'],
                insuredname=pam['insuredname'],
                insuredidno=pam['insuredidno'],
                insuredmobile=pam['insuredmobile'],
                insuredemail = pam['insuredemail'],
                ownername=pam['ownername'],
                owneridno=pam['owneridno'],
                ownermobile=pam['ownermobile'],
                owneremail=pam['owneremail'],
                addresseename=pam['addresseename'],
                addresseemobile=pam['addresseemobile'],
                senddate="",
                addresseeprovince=pam['addresseeprovince'],
                addresseecity=pam['addresseecity'],
                addresseetown=pam['addresseetown'],
                addresseedetails=pam['addresseedetails'],
                applicantname=pam['applicantname'],
                applicantidno=pam['applicantidno'],
                applicantmobile=pam['applicantmobile'],
                applicantemail=pam['applicantemail'],
                insuredaddresseeDetails = pam['insuredaddresseeDetails'], # 被保险人身份证地址
                bxgs_type=pam['bxgs_type'],
                status=pam['status'],
                session_id=pam['session_id'],
                proposalno_biz=pam['proposalno_biz'],
                proposalno_force=pam['proposalno_force']
            )
            CreateInfo.save()
    def GetYgInfo(self,vin='',ownername='',ID=''):
        try:
            if ID <> '' and ID <> None:
                GetCar = bxcarvin.objects.get(id=ID)
            else:
                GetCar = bxcarvin.objects.get(vin=vin,ownername=ownername)
        except:
            return False
        PriceinfoIsSet = GetCar.bxygpriceinfo_set.exists()
        if PriceinfoIsSet:
            YgInfo = GetCar.bxygpriceinfo_set.get()
            return YgInfo
        else:
            return False
    def GetYgHeboInfo(self,vin='',ownername='',ID=""):
        try:
            if ID <> '' and ID <>None:
                GetCar = bxcarvin.objects.get(id=ID)
            else:
                GetCar = bxcarvin.objects.get(vin=vin,ownername=ownername)
        except:
            return False
        PriceinfoIsSet = GetCar.bxyghebaoinfo_set.exists()
        if PriceinfoIsSet:
            YgInfo = GetCar.bxyghebaoinfo_set.get()
            return YgInfo
        else:
            return False
    def CreatCallBack_yg(self,**pam):
        Gethebao = bxyghebaoinfo.objects.get(session_id=pam['session_id'])
        IsSet = Gethebao.bxygcallbackinfo_set.filter().exists()
        if IsSet:
            Gethebao.bxygcallbackinfo_set.update(
                                                session_id=pam['session_id'],
                                                usercode = pam['usercode'],
                                                orderno_biz = pam['orderno_biz'],
                                                orderno_force = pam['orderno_force'],
                                                proposalno_biz = pam['proposalno_biz'],
                                                policyno_biz = pam['policyno_biz'],
                                                proposalno_force = pam['proposalno_force'],
                                                policyno_force = pam['policyno_force'],
                                                startdate = pam['startdate'],
                                                enddate = pam['enddate'],
                                                forcepremium = pam['forcepremium'],
                                                vehicletaxpremium = pam['vehicletaxpremium'],
                                                paytime = pam['paytime'],
                                                bizpremium = pam['bizpremium']
            )
        else:
            GetInfo = Gethebao.bxygcallbackinfo_set.create(
                                                session_id=pam['session_id'],
                                                usercode = pam['usercode'],
                                                orderno_biz = pam['orderno_biz'],
                                                orderno_force = pam['orderno_force'],
                                                proposalno_biz = pam['proposalno_biz'],
                                                policyno_biz = pam['policyno_biz'],
                                                proposalno_force = pam['proposalno_force'],
                                                policyno_force = pam['policyno_force'],
                                                startdate = pam['startdate'],
                                                enddate = pam['enddate'],
                                                forcepremium = pam['forcepremium'],
                                                vehicletaxpremium = pam['vehicletaxpremium'],
                                                paytime = pam['paytime'],
                                                bizpremium = pam['bizpremium']
                                                )
            GetInfo.save()
    def GetCityName(self,CityCode):
        try:
            IsGet=citycode.objects.filter(mid=CityCode)
            if IsGet[0].citycode_yg == "" and IsGet[0].citycode_yg == None:
               return IsGet[0].name,IsGet[0].citycode_yg
            else:
               return IsGet[0].name,IsGet[0].citycode_yg
        except:
            print(CityCode)
            IsGet=citycode.objects.get(mid=CityCode)
            if IsGet.citycode_yg == "" and IsGet.citycode_yg == None:
               return IsGet.name,IsGet.citycode_yg
            else:
               return IsGet.name,IsGet.citycode_yg
    def CreatCitycode(self,CityCode,citycode_yg):
        try:
            IsGet=citycode.objects.filter(mid=CityCode)
            if IsGet:
                IsGet[0].citycode_yg=citycode_yg
                IsGet[0].save()
                return True
            else:
                return False
        except:
            IsGet=citycode.objects.get(mid=CityCode)
            if IsGet:
                IsGet.citycode_yg=citycode_yg
                IsGet.save()
                return  True
            else:
                return False
    def CreatCallBackLog(self,xml,bxgs,interface_type):
        SHIJIAN = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        loginfo = callbaklog.objects.create(
            log = xml,
            addtime = SHIJIAN,
            bxgs_type = bxgs,
            interface_type = interface_type
        )
        loginfo.save()
    def GetCallBackInfo(self,sessionid='',bxgs=''):
        if sessionid <> "" and bxgs <> "" :
            if bxgs == 'zh':
                GetInfo = bxpayinfo.objects.get(session_id=sessionid)
                if GetInfo:
                    try:
                        Getorderno = GetInfo.bxzhcallbackinfo_set.get()
                        RE = {'error':'0','orderno':Getorderno.order_id,"bxgs":'zh'}
                        return RE
                    except:
                        RE = {'error':'1','orderno':""}
                        return RE
                else:
                    RE = {'error':'1','orderno':""}
                    return RE
            if bxgs == 'as':
                try:
                    GetInfo = bxascallbackinfo.objects.get(sessionid=sessionid)
                    RE = {'error':'0','orderno':GetInfo.tborderid,"bxgs":'as'}
                    return RE
                except:
                    RE = {'error':'1','orderno':""}
                    return RE
            if bxgs == "yg":
                try:
                    GetInfo = bxygcallbackinfo.objects.get(session_id=sessionid)
                    GetInfo = bxyghebaoinfo.objects.get(id=GetInfo.hebao_id)
                    RE = {'error':'0','orderno':GetInfo.tborder_id,"bxgs":'yg'}
                    return RE
                except:
                    RE = {'error':'1','orderno':""}
                    return RE
    def GetHeBaoInfo(self,order='',bxgs=''):
        if order == '' or bxgs == "":
            return False
        if bxgs == "zh":
            HeBaoInfo = bxpayinfo.objects.filter(order_id=order)
            return HeBaoInfo[0]
        if bxgs == 'as':
            HeBaoInfo = bxashebaoinfo.objects.filter(tborder_id=order)
            return HeBaoInfo[0]
        if bxgs == 'yg':
            HeBaoInfo = bxyghebaoinfo.objects.filter(tborder_id=order)
            return HeBaoInfo[0]
class IsTerminal():
    def __init__(self,agent):
        self.agent=''.join(re.findall(r'[a-zA-Z]',agent))
    def IsTer(self,):
        # agent = re.findall(self.reg,self.agent)
        if 'Android' in self.agent:
            print(self.agent)
            return True
        if 'iPhone' in self.agent:
            print(self.agent)
            return True
        if 'CFNetwork' in self.agent:
            print(self.agent)
            return True
        if 'Windows' in self.agent:
            print(self.agent)
            return False
        if self.agent == '':
            return True
        else:
            return True
    def IsNull(self,INFO=''):
        if INFO == "":
            return True
        for i in range(len(INFO)):
            if INFO[i][0] == 'C_INSRNT_EMAIL':
                if INFO[i][1] == '':
                    return True
            if INFO[i][0] == 'C_APP_EMAIL':
                if INFO[i][1] == '':
                    return True
            if INFO[i][0] == 'C_INSRNT_ADDR':
                if INFO[i][1] == '':
                    return True
            if INFO[i][0] == 'C_IDENT_NO':
                if INFO[i][1] == '' or len(INFO[i][1]) <> 18:
                    return True
            if INFO[i][0] == 'C_INSRNT_TEL':
                if INFO[i][1] == '':
                    return True
            if INFO[i][0] == 'C_APP_ADDR':
                if INFO[i][1] == '':
                    return True
            if INFO[i][0] == 'C_APP_IDENT_NO':
                if INFO[i][1] == '' or len(INFO[i][1]) <> 18:
                    return True
            if INFO[i][0] == 'C_INSRNT_IDENT_NO':
                if INFO[i][1] == '' or len(INFO[i][1]) <> 18:
                    return True
            if INFO[i][0] == 'C_CONTACT_TEL':
                if INFO[i][1] == '':
                    return True
            if INFO[i][0] == 'C_APP_NAME':
                if INFO[i][1] == '':
                    return True
            if INFO[i][0] == 'C_IDET_NAME':
                if INFO[i][1] == '':
                    return True
            if INFO[i][0] == 'C_INSRNT_NME':
                if INFO[i][1] == '':
                    return True
            if INFO[i][0] == 'C_ADDRESS':
                if INFO[i][1] == '':
                    return True
            if INFO[i][0] == 'C_APP_TEL':
                if INFO[i][1] == '':
                    return True
            if INFO[i][0] == 'C_CONTACT_NAME':
                if INFO[i][1] == '':
                    return True
        return False
    # 获取注册日期
class GetregisterDate():
    def GetregisterDate(self,licenseno,vin,engineNo,CityCode='110100'):
        phone = ['133', '153', '180', '181', '189', '177',
                 '130', '131', '132', '155', '156', '145',
                 '185', '186', '176', '178', '188', '147',
                 '134', '135', '136', '137', '138', '139',
                 '150', '151', '152', '157', '158', '159',
                 '182', '183', '184', '187']
        r = random.randint(0, len(phone))
        try:
            phone = phone[r]
        except:
            phone = phone[1]
        self.phone = str(phone) + str(random.randint(10000000, 99999999))
        birsday = ['0909','0304','0903','0806','0902','0103','0203']
        b= random.randint(0, len(birsday))
        bri = str(birsday[b])
        P = citycode.objects.get(mid=CityCode)
        citycodeNEW = P.pid
        if CityCode == '110100':
            citycodeNEW = '110000'
        if CityCode == '120100':
            citycodeNEW = '120000'
        url = "http://www.ecpic.com.cn/cpiccar/sales/businessCollect/submitVehicleBaseInfo"
        body = {"VehicleInfo":{"driveArea":2,"plateNo":licenseno},"Opportunity":{"licenseOwner":"一口价","mobile":self.phone,"email":"","giftInfo":"","extCustomerInfo":"","externalOrderNo":"","buyerNick":"","buyerId":"","bannerPath":""},"PolicyBaseInfo":{"provinceCode":citycodeNEW,"cityCode":CityCode,"branchCode":"","orgdeptCode":"","otherSource":"","cmpId":""},"productList":'',"hideUserName":"","userId":"","registNo":"","zjhm":bri}
        REDICT = self.SendRE(url=url,body=body)
        bodyNEW = {"VehicleInfo":{"driveArea":2,"carVIN":vin,"engineNo":engineNo,"plateNo":licenseno},"PolicyBaseInfo":{"provinceCode":citycodeNEW,"cityCode":CityCode},"random":REDICT['random'],"orderNo":REDICT['orderNo']}
        urlNEW = 'http://www.ecpic.com.cn/cpiccar/sale/businessCollect/queryVehicleModelByVinAndEngineNo'
        REDICT = self.SendRE(url=urlNEW,body=bodyNEW)
        return REDICT['registerDate']
    def SendRE(self,url,body):
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        req.add_header('Referer', 'http://www.ecpic.com.cn/cpiccar/sales/businessCollect/initVehicleBaseInfo')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:41.0) Gecko/20100101 Firefox/41.0')
        req.add_header('Host', 'www.ecpic.com.cn')
        postBody = json.dumps(body)
        response = urllib2.urlopen(req, postBody)
        response = response.read()
        REDICT = json.loads(response)
        return REDICT
class ConfirmRate():
    def __init__(self,Order_id):
        self.OrderID = Order_id
        self.url_biz = "http://e.cic.cn/nsp/vehicle/initFloatNotice.do?orderNo=%s&businessCode=11" % self.OrderID
        self.url_force = "http://e.cic.cn/nsp/vehicle/initFloatNotice.do?orderNo=%s&businessCode=12" % self.OrderID
        self.url_b1 = "http://e.cic.cn/nsp/vehicle/confirmFolatNotice.do?orderNo=%s&businessCode=11" % self.OrderID
        self.url_f1 = "http://e.cic.cn/nsp/vehicle/confirmFolatNotice.do?orderNo=%s&businessCode=12" % self.OrderID
        self.url_b = "http://e.cic.cn/nsp/vehicle/confirmFloatNotifyPage.do?cooperateCode=001501&orderNo=%s&businessCode=11" % self.OrderID
        self.url_f = "http://e.cic.cn/nsp/vehicle/confirmFloatNotifyPage.do?cooperateCode=001501&orderNo=%s&businessCode=12" % self.OrderID
    def Confirm(self,M='11'):
        try:
            RE = self.Post(M=M,flag=True)
            RE = self.Post(M=M,flag=False)
            RE = {"error":"0","msg":"0"}
            return RE
        except:
            RE = {'error':'1','msg':"1"}
            return RE
    def Post(self,flag=False,M='11'):
        if M == '11':
            if flag:
                url = self.url_b1
            else:
                url = self.url_b
        if M == '12':
            if flag:
                url = self.url_f1
            else:
                url = self.url_f
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        if M == "11":
            req.add_header('Referer',self.url_biz)
        if M == "12":
            req.add_header('Referer',self.url_force)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:41.0) Gecko/20100101 Firefox/41.0')
        req.add_header('Host', 'e.cic.cn')
        if flag:
            body = {"businessCode": M, "orderNo": self.OrderID }
        else:
            body = {"businessCode": M, "cooperateCode":"001501","orderNo": self.OrderID }
        postBody = json.dumps(body)
        response = urllib2.urlopen(req, postBody)
        return response
class MyURLOpener(urllib.FancyURLopener):
    def open_http(self, url, data=None, method=None):
        """Use HTTP protocol."""
        import httplib
        user_passwd = None
        proxy_passwd = None
        if isinstance(url, str):
            host, selector = splithost(url)
            if host:
                user_passwd, host = splituser(host)
                host = unquote(host)
            realhost = host
        else:
            host, selector = url
            # check whether the proxy contains authorization information
            proxy_passwd, host = splituser(host)
            # now we proceed with the url we want to obtain
            urltype, rest = splittype(selector)
            url = rest
            user_passwd = None
            if urltype.lower() != 'http':
                realhost = None
            else:
                realhost, rest = splithost(rest)
                if realhost:
                    user_passwd, realhost = splituser(realhost)
                if user_passwd:
                    selector = "%s://%s%s" % (urltype, realhost, rest)
                if proxy_bypass(realhost):
                    host = realhost

                    # print "proxy via http:", host, selector
        if not host: raise IOError, ('http error', 'no host given')

        if proxy_passwd:
            import base64
            proxy_auth = base64.b64encode(proxy_passwd).strip()
        else:
            proxy_auth = None

        if user_passwd:
            import base64
            auth = base64.b64encode(user_passwd).strip()
        else:
            auth = None
        h = httplib.HTTP(host)

        if method is not None:
            h.putrequest(method, selector)
        else:
            h.putrequest('GET', selector)

        if data is not None:
            # h.putrequest('POST', selector)
            h.putheader('Content-Type', 'application/x-www-form-urlencoded')
            h.putheader('Content-Length', '%d' % len(data))

        if proxy_auth: h.putheader('Proxy-Authorization', 'Basic %s' % proxy_auth)
        if auth: h.putheader('Authorization', 'Basic %s' % auth)
        if realhost: h.putheader('Host', realhost)
        for args in self.addheaders: h.putheader(*args)
        h.endheaders(data)
        errcode, errmsg, headers = h.getreply()
        fp = h.getfile()
        if errcode == -1:
            if fp: fp.close()
            # something went wrong with the HTTP status line
            raise IOError, ('http protocol error', 0,
                            'got a bad status line', None)
        # According to RFC 2616, "2xx" code indicates that the client's
        # request was successfully received, understood, and accepted.
        if (200 <= errcode < 300):
            return addinfourl(fp, headers, "http:" + url, errcode)
        else:
            if data is None:
                return self.http_error(url, fp, errcode, errmsg, headers)
            else:
                return self.http_error(url, fp, errcode, errmsg, headers, data)

    def open(self, fullurl, data=None, method=None):
        """Use URLopener().open(file) instead of open(file, 'r')."""
        fullurl = unwrap(toBytes(fullurl))
        # percent encode url, fixing lame server errors for e.g, like space
        # within url paths.
        fullurl = quote(fullurl, safe="%/:=&?~#+!$,;'@()*[]|")
        if self.tempcache and fullurl in self.tempcache:
            filename, headers = self.tempcache[fullurl]
            fp = open(filename, 'rb')
            return addinfourl(fp, headers, fullurl)
        urltype, url = splittype(fullurl)
        if not urltype:
            urltype = 'file'
        if urltype in self.proxies:
            proxy = self.proxies[urltype]
            urltype, proxyhost = splittype(proxy)
            host, selector = splithost(proxyhost)
            url = (host, fullurl)  # Signal special case to open_*()
        else:
            proxy = None
        name = 'open_' + urltype
        self.type = urltype
        name = name.replace('-', '_')
        if not hasattr(self, name):
            if proxy:
                return self.open_unknown_proxy(proxy, fullurl, data)
            else:
                return self.open_unknown(fullurl, data)
        try:
            return getattr(self, name)(url, data, method)
        except socket.error, msg:
            raise IOError, ('socket error', msg), sys.exc_info()[2]
