# -*- coding:utf-8 -*-

import datetime, random, urllib, urllib2, time,httplib,sys, xmltodict,re,base64
import urllib
from LYZ.settings import *
from suds.client import *
from Crypto.Hash import SHA
import datetime, random, urllib, urllib2, time, httplib
import sys, xmltodict, re
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import MD5
from common import GetCarInfo
from LYZ.common import *
import base64
from common import *
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class YangGuang(object):
    # 支付地址测试
    # URL = "http://1.202.156.227:7002/netCarPcPayVerifyAction.action?%s&signFlag=2"
    # WAP_URL = "http://1.202.156.227:7002/netCarAppPayVerifyAction.action?%s&signFlag=2"
    # 支付地址生产
    URL = "http://chexian.sinosig.com/netCarPcPayVerifyAction.action?%s&signFlag=2"
    WAP_URL = "http://chexian.sinosig.com/netCarAppPayVerifyAction.action?%s&signFlag=2"
    def __init__(self,user_id='',licenseNo='',ownerName='',mobilePhone='',cityCode='',engine='',vin='',drivCity=''):
        self.user_id = user_id
        # 身份证号
        self.ownerId = makeNew()
        # 车牌号
        self.licenseNo = licenseNo
        # 车主姓名
        self.ownerName = ownerName
        # 车主手机
        self.mobilePhone = mobilePhone
        # 发动机号
        self.engine = engine
        self.cityCode = cityCode
        # 车架号
        self.vin = vin
        self.drivCity = drivCity
        self.c_url="http://chexian.sinosig.com/travelCity!getTravelCityForInterface.action?hotSign=0&limit=0&queryCon=%s&contName=&encoding=UTF-8&callback=jsonp"% self.drivCity
        self.Url = "http://1.202.156.227:7002/InterFaceServlet"
        self.SellerId= "kalaibao"
        self.SessionID = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + str(random.randint(100000000000000000, 999999999999999999))
        self.AddTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 车辆注册日期
        self.firstRegisterDate = str((datetime.date.today() + datetime.timedelta(days=-365 * 2)).strftime("%Y-%m-%d"))
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
        self.phone = phone + str(random.randint(10000000, 99999999))
        # 商业保险起期
        self.bizBeginDate = str((datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"))
        # 交强险起期
        self.forceBeginDate = str((datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"))
        # 本地订单号
        self.TBorder = str(datetime.datetime.now().strftime("%Y%m%d")) + str(
            random.randint(10000000, 99999999))
        self.ItemId = str(datetime.datetime.now().strftime("%Y%m%d")) + str(
            random.randint(100000, 999999))
        self.sign = Sign()

    def Get_095(self):
        Send = (
            str(self.licenseNo).encode('GBK'),
            str('01630600').encode('GBK'), # 城市代码
            "0".encode('GBK')
        )
        Rest=str(self.Send(Send=Send,Is126=False,Is125=False,Is120=False,Interface='095')).decode('gbk')
        print(Rest)
    # 获得基础信息接口
    def Get_100(self):
        self.Get_095()
        BXAction= BXDBAction()
        Name,citycode_yg = BXAction.GetCityName(CityCode=self.cityCode)
        if citycode_yg == "" or citycode_yg == None:
            self.c_url="http://chexian.sinosig.com/travelCity!getTravelCityForInterface.action?hotSign=0&limit=0&queryCon=%s&contName=&encoding=UTF-8&callback=jsonp"% Name
            conn = httplib.HTTPConnection("chexian.sinosig.com")
            conn.request(method="GET",url=self.c_url)
            response = conn.getresponse()
            res= response.read()
            res= re.sub(r'([a-zA-Z_0-9\.]*\()|(\);?$)', '', res)
            REDICT= json.loads(res)
            # 查询城市出错
            try:
                self.cityCodeNEW = REDICT[0]['id']
                # 存入数据库
                try:
                    BXAction.CreatCitycode(CityCode=self.cityCode,citycode_yg=self.cityCodeNEW)
                except:
                    pass
            except:
                Result = {}
                REDICT = {'error':'1',"msg":"该城市不可投保"}
                ErrorMessage = ""
                return Result,REDICT,ErrorMessage
        else:
            self.cityCodeNEW=citycode_yg
        Send=(
            str(self.ownerName).encode('GBK'), # 车主姓名
            str(self.phone).encode('GBK'), # 车主电话号
            str(self.cityCodeNEW).encode('GBK'), # 城市代码
            str(self.licenseNo).encode('GBK'), # 车牌号
        )
        # 转码出错
        try:
            Result = str(self.Send(Send=Send,Is126=False,Is125=False,Is120=False,Interface=100)).decode('gbk')
        except:
            self.EchoLog(msg="100接口编码出错",data="gbk出错",status=0)
            ErrorMessage = "数据异常"
            REDICT = {"error": "1", "msg": "对不起！网络异常请稍后再试！"}
            Result = ""
            return Result,REDICT,ErrorMessage
        self.EchoLog(msg="接口100返回",data=Result)
        REDICT = xmltodict.parse(Result,encoding='utf-8')
        ErrorMessage = REDICT['PackageList']['Package']['Header']['ErrorMessage']
        if ErrorMessage <> "" and ErrorMessage <> None:
            self.EchoLog(msg="100接口出错",data=Result,status=0)
            REDICT = {"error": "1", "msg": ErrorMessage}
            return ErrorMessage, REDICT, Result
        return Result,REDICT,ErrorMessage
    # 保费试算接口
    def Get_105(self):
        Result,REDICT,ErrorMessage = self.Get_100()
        if ErrorMessage <> "" and ErrorMessage <> None:
            return Result,REDICT,ErrorMessage
        self.CarInfoArr = GetCarInfo(Value=self.vin)
        ASInfo = self.CarInfoArr.GetDBSelect(type="sinosig")
        if ASInfo:
            self.CarInfo = ASInfo
        else:
            self.CarInfo = self.CarInfoArr.GetAnshengCarInfo(self.cityCode)
        try:
            GetRE = GetregisterDate()
            self.firstRegisterDateNEW = GetRE.GetregisterDate(licenseno=self.licenseNo,vin=self.vin,engineNo=self.engine,CityCode=self.cityCode)
        except:
            self.firstRegisterDateNEW=self.firstRegisterDate
        
        Send = (
            str(self.engine).encode('GBK'), # 发动机号
            str(self.ownerName).encode('GBK'), # 车主姓名
            str(self.vin).encode('GBK'), # 车架号
            str(self.CarInfo['key']).encode('GBK'), # 车辆ID
            str(self.firstRegisterDateNEW), # 注册登记日期
            str(self.CarInfo['value']).encode('GBK'), # 车辆品牌型号
            str(makeNew()), # 车主身份证
        )
        Result = self.Send(Send=Send,Is126=False,Is125=False,Is120=False,Interface=105).decode("gbk")
        REDICT = xmltodict.parse(Result,encoding='utf-8')
        ErrorMessage = REDICT['PackageList']['Package']['Header']['ErrorMessage']
        self.EchoLog(msg="接口105返回",data=Result)
        if ErrorMessage <> "" and ErrorMessage <> None:
            self.EchoLog(msg="105接口出错",data=Result,status=0)
            REDICT = {"error":"1","msg":ErrorMessage}
            return Result,REDICT,ErrorMessage
        # REDICT = json.loads(json.dumps(REDICT))
        NewDict = REDICT['PackageList']['Package']['Response']['TagsList']['Tags']
        REDICT = self.ShowList(NewDict)
        InCreateHeBao = BXDBAction()
        InCreateHeBao.CreatPayinfo_yg(
                                    vin=self.vin,
                                    tborder_id="",
                                    item_id="",
                                    insuredname=self.ownerName,
                                    insuredidno="",
                                    insuredmobile="",
                                    insuredemail = '',
                                    ownername=self.ownerName,
                                    owneridno="",
                                    ownermobile='',
                                    owneremail='',
                                    addresseename="",
                                    addresseemobile="",
                                    senddate='', # 配送时间
                                    addresseeprovince="",
                                    addresseecity="",
                                    addresseetown="",
                                    addresseedetails="",
                                    applicantname=self.ownerName,
                                    applicantidno="",
                                    applicantmobile="",
                                    applicantemail="",
                                    insuredaddresseeDetails = "",
                                    bxgs_type="sinosig",
                                    status = "0",
                                    session_id ="",
                                    proposalno_biz = "",
                                    proposalno_force = "",
                                    ID=""
        )
        return Result,REDICT,ErrorMessage
    # 修改报价接口
    def Get_110(self,CHESHUN="0", SANZHE='50000', DAOQIANG='0', SHIJI='10000', CHENGKE='10000', BOLI='0',
                JIAOQIANG='1', ZIRAN='0', HUAHEN='0', SHESHUI='0', CHESHUN_BJ='0', SANZHE_BJ='0', DAOQIANG_BJ='0',
                SHIJI_BJ='0', CHENGKE_BJ='0', FUJIA_BJ='0'):
        Result,REDICT,ErrorMessage = self.Get_105()
        if ErrorMessage <> "" and ErrorMessage <> None:
            return Result,REDICT,ErrorMessage
        ZIRAN = (ZIRAN == "1") and REDICT['ZiRan'] or "0"
        DAOQIANG = (DAOQIANG == "1") and REDICT['DaoQiang']  or "0"
        CHESHUN = (CHESHUN == "1") and REDICT['VehicleLoss'] or "0"
        Send=(
            CHESHUN,  # cov_200车辆损失险
            HUAHEN,   # cov_210车身划痕损险
            BOLI,     # cov_231玻璃单独破碎险
            SHESHUI,      # cov_291发动机特别损失险
            ZIRAN,    # cov_310自燃损失险
            "0.00",      # cov_321指定专修厂
            "0",      # cov_390高速高价救援险
            DAOQIANG, # cov_500全车盗抢险
            SANZHE,   # cov_600商业第三者责任险
            "0",      # cov_640交通事故精神损害赔偿责任险
            SHIJI,    # cov_701司机座位责任险
            CHENGKE,  # cov_702乘客座位责任险
            CHESHUN_BJ,  # cov_911不计免赔险(车损险)
            SANZHE_BJ,   # cov_912不计免赔险(三者险)
            DAOQIANG_BJ, # cov_921不计免赔险（机动车盗抢险）
            "0",         # cov_922不计免赔险（车身划痕损失险)
            SHIJI_BJ,    # cov_928不计免赔险(司机险)
            CHENGKE_BJ,  # cov_929不计免赔险(乘客险)
            JIAOQIANG,   # forceFlag 是否投保交强险
        )
        Result = self.Send(Send=Send,Is126=False,Is125=False,Is120=False,Interface=110).decode("gbk")
        REDICT = xmltodict.parse(Result,encoding='utf-8')
        ErrorMessage = REDICT['PackageList']['Package']['Header']['ErrorMessage']
        if ErrorMessage <> "" and ErrorMessage <> None:
            REDICT = {"error":"1","msg":ErrorMessage}
            self.EchoLog(msg="110接口出错",data=Result,status=0)
            return Result,REDICT,ErrorMessage
        NewDict = REDICT['PackageList']['Package']['Response']['TagsList']['Tags']
        REDICT = self.ShowList(NewDict)
        self.EchoLog(msg="接口110返回",data=Result)
        InCreatePriceinfo = BXDBAction()
        InCreatePriceinfo.CreatPriceinfo_yg(
                                        vin=self.vin,
                                        forceflag=JIAOQIANG,
                                        cov_200=REDICT['VehicleLoss'],
                                        cov_600=REDICT['SanZhe'],
                                        cov_701=REDICT['ZeRenSJ'],
                                        cov_702=REDICT['ZeRenCK'],
                                        cov_500=REDICT['DaoQiang'],
                                        cov_291=REDICT['SheShui'],
                                        cov_231=REDICT['BoLiPS'],
                                        cov_210=REDICT['HuaHen'],
                                        cov_310=REDICT['ZiRan'],
                                        cov_390="0",
                                        cov_640="0",
                                        cov_911=REDICT['BUJiCS'],
                                        cov_912=REDICT['BuJiSZ'],
                                        cov_921=REDICT['BuJiDQ'],
                                        cov_922=REDICT['BUJIHH'],
                                        cov_928=REDICT['BuJiSJ'],
                                        cov_929=REDICT['BuJiCK'],
                                        biztotalpremium=REDICT['BizPremium'],  # 商业保费
                                        totalpremium=REDICT['TotalPremium'],  # 网购价
                                        standardpremium="",  # 市场价
                                        forcepremium=REDICT['forcePre'],  # 交强险
                                        bizbegindate="",  # 商业险起期
                                        forcebegindate="",  # 交强险起期
                                        forceotalpremium=REDICT['ForePremium'],  # 交强总保费
                                        vehicletaxpremium=REDICT['VehTaxPremium'],
                                        session_id=self.SessionID,
                                        ownername = self.ownerName
        )
        return Result,REDICT,ErrorMessage
    def ShowList(self, NewDict):
        REDICT = {
            "Session_ID": "",
            "ORDER_ID": "",
            "TotalPremium": "",
            "BizPremium": "",
            "bizPremium": "",
            "InsuranceGift": "暂无礼品",
            "klbGift": "暂无礼品",
            "VehicleLoss": "0",  # 车损
            "ZeRenCK": "0",  # 责任险乘客
            "ZeRenSJ": "0",  # 责任险司机
            "SanZhe": "0",  # 三者
            "SanZheBE": "0",  # 三者保额
            "ZeRenSJBE": "0",  # 责任险司机保额
            "ZeRenCKBE": "0",  # 责任险乘客保额
            "BuJiSZ": "0",  # 不计免赔三者
            "DaoQiang": "0",  # 盗抢险
            "BuJiDQ": "0",  # 不计盗抢
            "BuJiSJ": "0",  # 不计司机
            "BuJiCK": "0",  # 不计乘客
            "BuJiCSRY": "0",  # 不计车上人员
            "BUJiCS": "0",  # 不计车损
            "BUJIZR": "0",  # 不计自燃
            "BoLiPS": "0",  # 玻璃破碎
            "BUJIHH": "0",  # 不计划痕
            "BuJiTY": "0",  # 不计免赔特约
            "BuJiHB": "0",  # 不计免赔合并
            "BUJISS": "0",  # 不计涉水
            "BuJiFJ": "0",  # 不计免赔附加
            "ZiRan": "0",  # 自然
            "totalPremium": "",
            "BuJiMPZJ": "0",
            "ForePremium": "0",  # 交强险总计
            "SheShui": "0",
            "HuaHen": "0",
            "forcePremium": "0",
            "forcePre": "0",
            "VehTaxPremium": "0",
        }
        # if NewDict
        for i in range(len(NewDict)):
            # 判断
            if NewDict[i]['@type'] == "luxury":
                MsgAll = NewDict[i]['Tag']
                for n in range(len(MsgAll)):
                    Definition = MsgAll[n]['Definition']
                    for v in range(len(Definition)):
                        if Definition[v].has_key('#text'):
                            # 车损
                            if Definition[v]['#text'] == "cov_200":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "value":
                                        VehicleLoss = Definition[m]['#text']
                                        if VehicleLoss == "0.00":
                                            VehicleLoss = "0"
                                            REDICT['VehicleLoss'] = VehicleLoss
                                        else:
                                            REDICT['VehicleLoss'] = VehicleLoss
                                        break
                            # 自然
                            if Definition[v]['#text'] == "cov_310":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "value":
                                        ZiRan = Definition[m]['#text']
                                        if ZiRan == "0.00":
                                            ZiRan ="0"
                                            REDICT['ZiRan'] = ZiRan
                                        else:
                                            REDICT['ZiRan'] = ZiRan
                                        break
                            # 盗抢
                            if Definition[v]['#text'] == "cov_500":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "value":
                                        DaoQiang = Definition[m]['#text']
                                        if DaoQiang == "0.00":
                                            DaoQiang = "0"
                                        else:
                                            REDICT['DaoQiang'] = DaoQiang
                                        break
            if NewDict[i]['@type'] == "":
                MsgAll = NewDict[i]['Tag']
                for n in range(len(MsgAll)):
                    Definition = MsgAll[n]['Definition']
                    for v in range(len(Definition)):
                        if Definition[v].has_key('#text'):
                            # 车损
                            if Definition[v]['#text'] == "cov_200":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        VehicleLoss = Definition[m]['#text']
                                        if VehicleLoss == "0":
                                            REDICT['VehicleLoss'] = "不支持"
                                        else:
                                            VehicleLoss = round(float(VehicleLoss) / float(100), 2)
                                            REDICT['VehicleLoss'] = VehicleLoss
                                            # print("车损的价格是:%s" % VehicleLoss)
                                        break
                            # 三者
                            if Definition[v]['#text'] == "cov_600":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        SanZhe = Definition[m]['#text']
                                        SanZhe = round(float(SanZhe) / float(100), 2)
                                        # print("三者的价格是:%s" % SanZhe)
                                        REDICT['SanZhe'] = SanZhe
                                        break
                            # 责任司机
                            if Definition[v]['#text'] == "cov_701":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        ZeRenSJ = Definition[m]['#text']
                                        ZeRenSJ = round(float(ZeRenSJ) / float(100), 2)
                                        # print("责任司机的价格是:%s" % ZeRenSJ)
                                        REDICT['ZeRenSJ'] = ZeRenSJ
                                        break
                            # 乘客
                            if Definition[v]['#text'] == "cov_702":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        ZeRenCK = Definition[m]['#text']
                                        ZeRenCK = round(float(ZeRenCK) / float(100), 2)
                                        # print("责任乘客的价格是:%s" % ZeRenCK)
                                        REDICT['ZeRenCK'] = ZeRenCK
                                        break
                            # 盗抢
                            if Definition[v]['#text'] == "cov_500":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        DaoQiang = Definition[m]['#text']
                                        if DaoQiang == "0":
                                            REDICT['DaoQiang'] = "不支持"
                                        else:
                                            DaoQiang = round(float(DaoQiang) / float(100), 2)
                                            # print("责任乘客的价格是:%s" % DaoQiang)
                                            REDICT['DaoQiang'] = DaoQiang
                                        break
                            # 玻璃
                            if Definition[v]['#text'] == "cov_231":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        BoLiPS = Definition[m]['#text']
                                        BoLiPS = round(float(BoLiPS) / float(100), 2)
                                        # print("玻璃的价格是:%s" % BoLiPS)
                                        REDICT['BoLiPS'] = BoLiPS
                                        break
                            # 涉水
                            if Definition[v]['#text'] == "cov_291":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        SheShui = Definition[m]['#text']
                                        if SheShui == "0":
                                            REDICT['SheShui'] = "不支持"
                                        else:
                                            SheShui = round(float(SheShui) / float(100), 2)
                                            # print("玻璃的价格是:%s" % SheShui)
                                            REDICT['SheShui'] = SheShui
                                        break
                            # 自然
                            if Definition[v]['#text'] == "cov_310":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        ZiRan = Definition[m]['#text']
                                        if ZiRan == "0":
                                            REDICT['ZiRan'] = "不支持"
                                        else:
                                            ZiRan = round(float(ZiRan) / float(100), 2)
                                            # print("自然的价格是:%s" % ZiRan)
                                            REDICT['ZiRan'] = ZiRan
                                        break
                            # 划痕
                            if Definition[v]['#text'] == "cov_210":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        HuaHen = Definition[m]['#text']
                                        if HuaHen == "0":
                                             REDICT['HuaHen'] = "不支持"
                                        else:
                                            HuaHen = round(float(HuaHen) / float(100), 2)
                                            # print("划痕的价格是:%s" % HuaHen)
                                            REDICT['HuaHen'] = HuaHen
                                        break
                            #  不计划痕
                            if Definition[v]['#text'] == "cov_922":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        BUJIHH = Definition[m]['#text']
                                        BUJIHH = round(float(BUJIHH) / float(100), 2)
                                        # print("不计划痕的价格是:%s" % BUJIHH)
                                        REDICT['BUJIHH'] = BUJIHH
                                        break
                            # 不计盗抢
                            if Definition[v]['#text'] == "cov_921":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        BuJiDQ = Definition[m]['#text']
                                        BuJiDQ = round(float(BuJiDQ) / float(100), 2)
                                        # print("不计划痕的价格是:%s" % BuJiDQ)
                                        REDICT['BuJiDQ'] = BuJiDQ
                                        break
                            # 不计车损
                            if Definition[v]['#text'] == "cov_911":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        BUJiCS = Definition[m]['#text']
                                        BUJiCS = round(float(BUJiCS) / float(100), 2)
                                        # print("不计车损的价格是:%s" % BUJiCS)
                                        REDICT['BUJiCS'] = BUJiCS
                                        break
                            # 不计 三者
                            if Definition[v]['#text'] == "cov_912":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        BuJiSZ = Definition[m]['#text']
                                        BuJiSZ = round(float(BuJiSZ) / float(100), 2)
                                        # print("不计三者的价格是:%s" % BuJiSZ)
                                        REDICT['BuJiSZ'] = BuJiSZ
                                        break
                            # 不计司机
                            if Definition[v]['#text'] == "cov_928":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        BuJiSJ = Definition[m]['#text']
                                        BuJiSJ = round(float(BuJiSJ) / float(100), 2)
                                        # print("不计司机的价格是:%s" % BuJiSJ)
                                        REDICT['BuJiSJ'] = BuJiSJ
                                        break
                            #　不计乘客
                            if Definition[v]['#text'] == "cov_929":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        BuJiCK = Definition[m]['#text']
                                        BuJiCK = round(float(BuJiCK) / float(100), 2)
                                        # print("不计司机的价格是:%s" % BuJiCK)
                                        REDICT['BuJiCK'] = BuJiCK
                                        break
                            # 商业总保费
                            if Definition[v]['#text'] == "bizTotalPremium":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        BizPremium = Definition[m]['#text']
                                        BizPremium = round(float(BizPremium) / float(100), 2)
                                        # print("商业总保费的价格是:%s" % BizPremium)
                                        REDICT['BizPremium'] = BizPremium
                                        REDICT['bizPremium'] = BizPremium
                                        break
                            # 总保费
                            if Definition[v]['#text'] == "totalPremium":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        TotalPremium = Definition[m]['#text']
                                        TotalPremium = round(float(TotalPremium) / float(100), 2)
                                        # print("总保费的价格是:%s" % TotalPremium)
                                        REDICT['TotalPremium'] = TotalPremium
                                        REDICT['TotalPremium'] = TotalPremium
                                        break

            if NewDict[i]['@type'] == "force":
                MsgAll = NewDict[i]['Tag']
                for n in range(len(MsgAll)):
                    Definition = MsgAll[n]['Definition']
                    for v in range(len(Definition)):
                        if Definition[v].has_key('#text'):
                            # 车损
                            if Definition[v]['#text'] == "forcePremium":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        forcePre = Definition[m]['#text']
                                        forcePre = round(float(forcePre) / float(100), 2)
                                        REDICT['forcePre'] = forcePre
                                        # print("交强险的价格是:%s" % forcePre)
                                        break
                            if Definition[v]['#text'] == "vehicleTaxPremium":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        VehTaxPremium = Definition[m]['#text']
                                        VehTaxPremium = round(float(VehTaxPremium) / float(100), 2)
                                        REDICT['VehTaxPremium'] = VehTaxPremium
                                        # print("车船税的价格是:%s" % VehTaxPremium)
                                        break
                            if Definition[v]['#text'] == "forceTotalPremium":
                                for m in range(len(Definition)):
                                    if Definition[m]['@name'] == "premium":
                                        ForePremium = Definition[m]['#text']
                                        ForePremium = round(float(ForePremium) / float(100), 2)
                                        REDICT['forceTotalPremium'] = ForePremium
                                        REDICT['ForePremium'] = ForePremium
                                        REDICT['forcePremium'] = ForePremium
                                        # print("交强总保费的价格是:%s" % ForePremium)
                                        break
        REDICT['BuJiMPZJ'] = round(float(REDICT['BuJiSJ']) + float(REDICT['BuJiCK']) + float(REDICT['BuJiSZ']) + float(REDICT['BUJiCS']) + float(REDICT['BuJiDQ']),2)
        return REDICT
    # 保存保费接口
    def Get_115(self,vin=''):
        Priceinfo = BXDBAction()
        Priceinfo = Priceinfo.GetPriceinfo_as(vin=vin)
        Send=()
        Result=self.Send(Send=Send,Is126=False,Is125=False,Is120=False,Interface=115,SessionID=Priceinfo.session_id).decode("gbk")
        REDICT = xmltodict.parse(Result,encoding='utf-8')
        ErrorMessage = REDICT['PackageList']['Package']['Header']['ErrorMessage']
        if ErrorMessage <> "" and ErrorMessage <> None:
            self.EchoLog(msg="接口115出错",data=Result,status=0)
            REDICT={"error":"1","msg":ErrorMessage}
            return Result,REDICT,ErrorMessage
        return Result,REDICT,ErrorMessage
    # 申请核保接口
    def Get_120(self,vin='',IsterInfo=False, insuredEmail='',applicantname='', applicantidno='', applicantmobile='', applicantemail='',
                 insuredname='', insuredidno='', insuredmobile='', addresseeprovince='', addresseecity='',
                 addresseetown='', addresseename='',addresseemobile="", addresseedetails='', ownername='', owneridno='',
                 insuredaddresseeDetails='',ID=''):
        InCreateHeBao = BXDBAction()
        print(ID)
        print(vin)
        print(insuredname)
        if ID <> "" and ID <> None:
            InCreateInfo = InCreateHeBao.GetYgInfo(ID=ID)
        else:
            InCreateInfo = InCreateHeBao.GetYgInfo(vin=vin,ownername=ownername)
        # 如果没有查到
        if InCreateInfo == False:
            ErrorMessage = "没有查到信息"
            REDICT={"error":"1","msg":ErrorMessage}
            URL = False
            Result =False
            return Result,REDICT,URL,ErrorMessage
        Send = (
                str(self.TBorder).encode('GBK'), # TBorder 本地生成订单号
                str(self.TBorder).encode('GBK'), # TBorder 本地生成订单号
                str(self.ItemId).encode('GBK'),
                str(self.TBorder).encode('GBK'), # TBorder 本地生成订单号
                str(self.ItemId).encode('GBK'),
                str(insuredidno).encode('GBK'), # 被保险人身份证号
                str(insuredEmail).encode('GBK'), # 被保险人邮箱
                str(insuredname).encode('GBK'), # 被保险人姓名
                str(insuredmobile).encode('GBK'), # 被保险人电话
                str(applicantemail).encode('GBK'), # 投保人邮箱
                str(applicantidno).encode('GBK'), # 投保人身份证号
                str(applicantmobile).encode('GBK'), # 投保人电话
                str(applicantname).encode('GBK'), # 投保人姓名
                str(ownername).encode('GBK'), # 车主姓名
                str(applicantmobile).encode('GBK'), # 车主电话
                str(owneridno).encode('GBK'), # 车主身份证号
                str(applicantemail).encode('GBK'), # 车主邮箱
                str(addresseename).encode('GBK'), # 收件人姓名
                str(addresseemobile).encode('GBK'), # 收件人电话
                str(addresseeprovince).encode('GBK'), # 省份代码
                str(addresseecity).encode('GBK'), # 城市代码
                str(addresseetown).encode('GBK'), # 区县代码
                str(insuredaddresseeDetails).encode('GBK'), # 被保险人身份证地址
                str(addresseedetails).encode('GBK'), # 收件地址
                 )
        InCreateHeBao.CreatPayinfo_yg(
                                    vin=vin,
                                    tborder_id=self.TBorder,
                                    item_id=self.ItemId,
                                    insuredname=insuredname,
                                    insuredidno=insuredidno,
                                    insuredmobile=insuredmobile,
                                    insuredemail = '',
                                    ownername=ownername,
                                    owneridno=owneridno,
                                    ownermobile='',
                                    owneremail='',
                                    addresseename=addresseename,
                                    addresseemobile=addresseemobile,
                                    senddate='', # 配送时间
                                    addresseeprovince=addresseeprovince,
                                    addresseecity=addresseecity,
                                    addresseetown=addresseetown,
                                    addresseedetails=addresseedetails,
                                    applicantname=applicantname,
                                    applicantidno=applicantidno,
                                    applicantmobile=applicantmobile,
                                    applicantemail=applicantemail,
                                    insuredaddresseeDetails = insuredaddresseeDetails,
                                    bxgs_type="sinosig",
                                    status = "0",
                                    session_id =InCreateInfo.session_id,
                                    proposalno_biz = "",
                                    proposalno_force = "",
                                    ID = ID
        )
        SessionID=InCreateInfo.session_id
        Result = self.Send(Send=Send,Is126=False,Is125=False,Is120=True,Interface=120,SessionID=str(InCreateInfo.session_id).encode('GBK')).decode('gbk')
        REDICT = xmltodict.parse(Result,encoding='utf-8')
        ErrorMessage = REDICT['PackageList']['Package']['Header']['ErrorMessage']
        if ErrorMessage <> "" and ErrorMessage <> None:
            self.EchoLog(msg="接口120出错",data=Result,status=0)
            REDICT={"error":"1","msg":ErrorMessage}
            URL = False
            return Result,REDICT,URL,ErrorMessage
        NEWLIST= REDICT['PackageList']['Package']['Response']['Order']['SubOrderList']['SubOrder']
        ProposalNo_biz,ProposalNo_force = self.Get_ProposalNo(NEWLIST=NEWLIST)
        InCreateHeBao.CreatPayinfo_yg(
                                    vin=vin,
                                    tborder_id=self.TBorder,
                                    item_id=self.ItemId,
                                    insuredname=insuredname,
                                    insuredidno=insuredidno,
                                    insuredmobile=insuredmobile,
                                    insuredemail = '',
                                    ownername=ownername,
                                    owneridno=owneridno,
                                    ownermobile='',
                                    owneremail='',
                                    addresseename=addresseename,
                                    addresseemobile=addresseemobile,
                                    senddate='', # 配送时间
                                    addresseeprovince=addresseeprovince,
                                    addresseecity=addresseecity,
                                    addresseetown=addresseetown,
                                    addresseedetails=addresseedetails,
                                    applicantname=applicantname,
                                    applicantidno=applicantidno,
                                    applicantmobile=applicantmobile,
                                    applicantemail=applicantemail,
                                    insuredaddresseeDetails = insuredaddresseeDetails,
                                    bxgs_type="sinosig",
                                    status = "0",
                                    session_id =SessionID,
                                    proposalno_biz = ProposalNo_biz,
                                    proposalno_force = ProposalNo_force,
                                    ID = ID
        )
        # 判断是否需要身份验证
        if REDICT['PackageList']['Package']['Response']['IsIdVerifi'] == "1":
            Result, REDICT, URL, ErrorMessage=  self.Get_126(vin=vin,ownername=ownername,IsterInfo=IsterInfo,Flag=True,ID=ID)
            if ErrorMessage <> "" and ErrorMessage <> None:
                 URL = False
                 REDICT={'error':'1','msg':ErrorMessage}
                 return Result,REDICT,URL,ErrorMessage
            URL = False
            REDICT={'error':'2','msg':"请输入验证码"}
            return Result,REDICT,URL,ErrorMessage
        if ProposalNo_biz == "" and ProposalNo_force == "":
            REDICT={"error":'1','msg':"对不起！系统异常请稍后再试！"}
            URL = False
            return Result,REDICT,URL,ErrorMessage
        if ProposalNo_biz <> None and ProposalNo_force <> None:
            ProposalNo = ProposalNo_biz
        if ProposalNo_biz == None and ProposalNo_force <> None:
            ProposalNo =ProposalNo_force
        if ProposalNo_biz <> None and ProposalNo_force == None:
            ProposalNo = ProposalNo_biz
        if ID <> "" and ID <> None:
            InCreateHeBao = InCreateHeBao.GetYgHeboInfo(ID=ID)
        else:
            InCreateHeBao = InCreateHeBao.GetYgHeboInfo(vin=vin,ownername=ownername)
        if InCreateHeBao == False:
            Result = False
            URL = False
            REDICT={"error":'1','msg':"对不起！网络异常请稍后再试！"}
            return Result,REDICT,URL,ErrorMessage
        insrancename = InCreateHeBao.applicantname
        params = urllib.urlencode({'proposalno': ProposalNo, 'insrancename': insrancename})
        if IsterInfo:
            URL = self.WAP_URL % params
        else:
            URL = self.URL % params
        return Result,REDICT,URL,ErrorMessage
    # 获取验证码接口
    def Get_126(self,vin="",ownername='',Verify='',IsterInfo=False,Flag=False,ID=''):

        Priceinfo = BXDBAction()
        # ID 为车辆ID
        if ID <> "" and ID <> None:
            Priceinfo = Priceinfo.GetYgInfo(ID=ID)
        else:
            Priceinfo = Priceinfo.GetYgInfo(vin=vin,ownername=ownername)
        if Priceinfo == False:
           Result =False
           URL = False
           ErrorMessage = "输入信息有误"
           REDICT={'error':'1','msg':ErrorMessage}
           return Result,REDICT,URL,ErrorMessage
        Send = ()
        Result = self.Send(Send=Send,Is126=True,Is120=False,Is125=False,Interface=126,SessionID=str(Priceinfo.session_id).encode('gbk')).decode('gbk')
        REDICT = xmltodict.parse(Result,encoding='utf-8')
        ErrorMessage = REDICT['PackageList']['Package']['Header']['ErrorMessage']
        if ErrorMessage <> "" and ErrorMessage <> None:
           URL = False
           ErrorMessage = REDICT['PackageList']['Package']['Header']['ErrorMessage']
           REDICT={'error':'1','msg':ErrorMessage}
           return Result,REDICT,URL,ErrorMessage
        if Flag:
            URL = False
            return Result, REDICT, URL, ErrorMessage
        else:
            Result, REDICT, ErrorMessage = self.Get_127(vin=vin,ownername=ownername,Verify=Verify,ID=ID)
            if ErrorMessage <> "" and ErrorMessage <> None:
                URL = False
                return Result, REDICT, URL, ErrorMessage
            else:
                Priceinfo = BXDBAction()
                if ID <> "" and ID <> None:
                    Priceinfo = Priceinfo.GetYgHeboInfo(ID=ID)
                else:
                    Priceinfo = Priceinfo.GetYgHeboInfo(vin=vin,ownername=ownername)
                if Priceinfo == False:
                    Result = False
                    URL = False
                    REDICT = REDICT = {"error": '1', 'msg': "对不起！网络繁忙请稍后再试！"}
                    return Result, REDICT, URL, ErrorMessage
                insrancename = Priceinfo.applicantname
                if Priceinfo.proposalno_biz == "" and Priceinfo.proposalno_force == "":
                    REDICT = {"error": '1', 'msg': "对不起！网络繁忙请稍后再试！"}
                    URL = False
                    return Result, REDICT, URL, ErrorMessage
                if Priceinfo.proposalno_biz <> None and Priceinfo.proposalno_force <> None:
                    ProposalNo = Priceinfo.proposalno_biz
                if Priceinfo.proposalno_biz == None and Priceinfo.proposalno_force <> None:
                    ProposalNo = Priceinfo.proposalno_force
                if Priceinfo.proposalno_biz <> None and Priceinfo.proposalno_force == None:
                    ProposalNo = Priceinfo.proposalno_biz
                params = urllib.urlencode({'proposalno': ProposalNo, 'insrancename': insrancename})
                if IsterInfo:
                    URL = self.WAP_URL % params
                else:
                    URL = self.URL % params
                return Result, REDICT, URL, ErrorMessage
    # 保存验证码接口
    def Get_127(self,vin='',ownername='',Verify='',ID=''):
        Priceinfo = BXDBAction()
        if ID <> "" and ID <> None:
            Priceinfo = Priceinfo.GetYgInfo(ID=ID)
        else:
            Priceinfo = Priceinfo.GetYgInfo(vin=vin,ownername=ownername)
        Send = (
            Verify,
        )
        Result = self.Send(Send=Send,Is126=True,Is120=False,Is125=False,Interface=127,SessionID=str(Priceinfo.session_id).encode('gbk')).decode('gbk')
        # print (Result)
        REDICT = xmltodict.parse(Result,encoding='utf-8')
        ErrorMessage = REDICT['PackageList']['Package']['Header']['ErrorMessage']
        ResponseCode = REDICT['PackageList']['Package']['Response']['ResponseCode']
        if ErrorMessage <> "" and ErrorMessage <> None:
            ErrorMessage = REDICT['PackageList']['Package']['Header']['ErrorMessage']
            self.EchoLog(msg="127接口出错",data=Result,status=0)
            REDICT={"error":"1","msg":ErrorMessage}
            return Result,REDICT,ErrorMessage
        elif ResponseCode == "error":
            ErrorMessage = REDICT['PackageList']['Package']['Response']['ResponseMessage']
            self.EchoLog(msg="127接口出错",data=Result,status=0)
            REDICT={"error":"1","msg":ErrorMessage}
            return Result,REDICT,ErrorMessage
        else:
            return Result,REDICT,ErrorMessage
    def Get_ProposalNo(self,NEWLIST):
        """
        获取订单号
        :param NEWREDICT:
        :return:
        """
        try:
            for i in range(len(NEWLIST)):
                    NEWDICT = NEWLIST[i]
                    if NEWDICT['@type']  == 'biz':
                        ProposalNo_biz = NEWDICT['ProposalNo']
                    if NEWDICT['@type'] == 'force':
                        ProposalNo_force= NEWDICT['ProposalNo']
                        return  ProposalNo_biz,ProposalNo_force
        except:
            if NEWLIST['@type'] == 'biz':
                ProposalNo_biz = NEWLIST['ProposalNo']
            else:
                ProposalNo_biz =''
            if NEWLIST['@type'] == 'force':
                ProposalNo_force = NEWLIST['ProposalNo']
            else:
                ProposalNo_force = ''
            return  ProposalNo_biz,ProposalNo_force
    def CallBack(self,xml=''):
        BDAction = BXDBAction()
        BDAction.CreatCallBackLog(xml=xml,bxgs='sinosig',interface_type='')
        try:
            REDICT = xmltodict.parse(xml,encoding='utf-8')
        except:
            return '''<?xml version="1.0" encoding="GBK"?><response finishTime='%s'>
            <isSuccess>F</isSuccess><orderNo></orderNo ><errorCode>400</errorCode><errorReason>解析xml失败</errorReason>
            </response>'''% self.AddTime
        SessionID = REDICT['message']['request']['content']['sessionId']
        UserCode = REDICT['message']['request']['content']['userCode']
        OrderList = REDICT['message']['request']['content']['orderInfoList']['orderInfo']
        proposalNo_froce,proposalNo_biz = self.GetcovInfo(ListIDCT=OrderList,SessionID=SessionID,UserCode=UserCode)
        applyInfoDICT = REDICT['message']['request']['content']['applyInfo']
        self.GetApplyInfo(DICT=applyInfoDICT)
        if proposalNo_froce <> '' and proposalNo_biz <>'':
            proposalNo = proposalNo_biz
        if proposalNo_froce <> '' and proposalNo_biz == '':
            proposalNo = proposalNo_froce
        if proposalNo_froce == '' and proposalNo_biz <> '':
            proposalNo = proposalNo_biz
        return '''<?xml version="1.0" encoding="utf-8"?><response finishTime='%s'>
                  <isSuccess>T</isSuccess><orderNo>%s</orderNo></response>''' % (self.AddTime,proposalNo)
    def GetApplyInfo(self,DICT):
        #车辆信息
        VehDICT = DICT['vehicleInfo']
        vin = VehDICT['VIN']
        orgName = VehDICT['orgName'] # 所属城市
        numPlate = VehDICT['numPlate'] # 车牌号
        brand = VehDICT['brand'] # 车辆型号
        engineNum = VehDICT['engineNum'] # 发动机号
        purchaseDate= VehDICT['purchaseDate'] # 车辆初等日期
        # 车主信息
        OwnerDICT = DICT['ownerInfo']
        ownerName = OwnerDICT['ownerName']
        ownerIdType = OwnerDICT['ownerIdType']
        ownerIdNo = OwnerDICT['ownerIdNo']
        ownerContect = OwnerDICT['ownerContect']
        ownerMail = OwnerDICT['ownerMail']
        # 投保人信息
        InsureDICT = DICT['insureInfo']
        insureName = InsureDICT['insureName']
        insureIdType = InsureDICT['insureIdType']
        insureIdNo = InsureDICT['insureIdNo']
        insureContect = InsureDICT['insureContect']
        insureMail = InsureDICT['insureMail']
        # 被保险人信息
        InsuredDICT =DICT['insuredInfo']
        insuredName = InsuredDICT['insuredName']
        insuredIdType = InsuredDICT['insuredIdType']
        insuredIdNo = InsuredDICT['insuredIdNo']
        insuredContect = InsuredDICT['insuredContect']
        insuredMail = InsuredDICT['insuredMail']
        # 收件地址
        address = DICT['address']
    def GetcovInfo(self,ListIDCT,SessionID,UserCode):
        if ListIDCT <> "" and ListIDCT <> None:
            try:
                for i in range(len(ListIDCT)):
                    NewDICT = ListIDCT[i]
                    if NewDICT['insuranceType'] == '0': # '0' 为交强险
                        SubDICT = ListIDCT[i]['compulsory']
                        orderNo_froce = NewDICT['orderNo'] # 定单号
                        proposalNo_froce = NewDICT['proposalNo']
                        policyNo_froce = NewDICT['policyNo'] # 保单号
                        startDate_froce = NewDICT['startDate'] # 起保 日期
                        endDate_froce = NewDICT['endDate'] # 终日期
                        premium_froce = SubDICT['premium']
                        vehicletaxpremium = SubDICT['tax']
                        payTime_froce = NewDICT['payTime']
                    if NewDICT['insuranceType'] == '1':
                        SubDICT = ListIDCT[i]['commercial']
                        List = SubDICT['insuranceList']['insure']
                        orderNo_biz = NewDICT['orderNo']
                        policyNo_biz = NewDICT['policyNo']
                        proposalNo_biz = NewDICT['proposalNo']
                        policyNo_biz = NewDICT['policyNo']
                        startDate_biz = NewDICT['startDate'] # 起保 日期
                        endDate_biz = NewDICT['endDate'] # 终日期
                        premium_biz = SubDICT['premium']
                        InCreateCallBack = BXDBAction()
                        InCreateCallBack.CreatCallBack_yg(
                                                session_id=SessionID,
                                                usercode = UserCode,
                                                orderno_biz = orderNo_biz,
                                                orderno_force = orderNo_froce,
                                                proposalno_biz = proposalNo_biz,
                                                policyno_biz = policyNo_biz,
                                                proposalno_force = proposalNo_froce,
                                                policyno_force = policyNo_froce,
                                                startdate = startDate_froce,
                                                enddate = endDate_froce,
                                                forcepremium = premium_froce,
                                                vehicletaxpremium = vehicletaxpremium,
                                                paytime = payTime_froce,
                                                bizpremium = premium_biz
                        )
                        try:
                            for i in range(len(List)):
                                NewDICT = List[i]
                                if NewDICT['riskCode'] == 'A':
                                    cov_200_amount = NewDICT['amount']
                                    cov_200 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'B':
                                    cov_600_amount = NewDICT['amount']
                                    cov_600 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'D3':
                                    cov_701_amount = NewDICT['amount']
                                    cov_701 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'D4':
                                    cov_702_amount = NewDICT['amount']
                                    cov_702 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'G1':
                                    cov_500_amount = NewDICT['amount']
                                    cov_500 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'F':
                                    cov_231_amount = NewDICT['amount']
                                    cov_231 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'Z':
                                    cov_310_amount = NewDICT['amount']
                                    cov_310 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'L':
                                    cov_210_amount = NewDICT['amount']
                                    cov_210 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'Q3': # 指定厂专修
                                    cov_zdzx_amount = NewDICT['amount']
                                    cov_zdzx = NewDICT['premium']
                                if NewDICT['riskCode'] == 'M': #
                                    cov_291_amount = NewDICT['amount']
                                    cov_291 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'X1':
                                    BJ_amount = NewDICT['amount']
                                    BJ = NewDICT['premium']
                                if NewDICT['riskCode'] == 'J': #
                                    cov_390_amount = NewDICT['amount']
                                    cov_390 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'Q': #
                                    cov_jdmp_amount = NewDICT['amount']
                                    cov_jdmp = NewDICT['premium']
                                if NewDICT['riskCode'] == 'Z2': #
                                    cov_XL_amount = NewDICT['amount']
                                    cov_XL = NewDICT['premium']
                                if NewDICT['riskCode'] == 'Z3': #
                                    cov_XL_amount = NewDICT['amount']
                                    cov_XL = NewDICT['premium']
                                if NewDICT['riskCode'] == 'R': #
                                    cov_640_amount = NewDICT['amount']
                                    cov_640 = NewDICT['premium']
                            return proposalNo_froce,proposalNo_biz
                        except:
                            if List['riskCode'] == 'A':
                                cov_200_amount = List['amount']
                                cov_200 = List['premium']
                            else:
                                cov_200_amount = '0'
                                cov_200 = '0'
                            if List['riskCode'] == 'B':
                                cov_600_amount = List['amount']
                                cov_600 = List['premium']
                            else:
                                cov_600_amount = '0'
                                cov_600 = '0'
                            if List['riskCode'] == 'D3':
                                cov_701_amount = List['amount']
                                cov_701 = List['premium']
                            else:
                                cov_701_amount = '0'
                                cov_701 = '0'
                            if List['riskCode'] == 'D4':
                                cov_702_amount = List['amount']
                                cov_702 = List['premium']
                            else:
                                cov_702_amount = '0'
                                cov_702 = '0'
                            if List['riskCode'] == 'G1':
                                cov_500_amount = List['amount']
                                cov_500 = List['premium']
                            else:
                                cov_500_amount = '0'
                                cov_500 = '0'
                            if List['riskCode'] == 'F':
                                cov_231_amount = List['amount']
                                cov_231 = List['premium']
                            else:
                                cov_231_amount = '0'
                                cov_231 = '0'
                            if List['riskCode'] == 'Z':
                                cov_310_amount = List['amount']
                                cov_310 = List['premium']
                            else:
                                cov_310_amount = '0'
                                cov_310 = '0'
                            if List['riskCode'] == 'L':
                                cov_210_amount = List['amount']
                                cov_210 = List['premium']
                            else:
                                cov_210_amount = '0'
                                cov_210 = '0'
                            if List['riskCode'] == 'Q3':  # 指定厂专修
                                cov_zdzx_amount = List['amount']
                                cov_zdzx = List['premium']
                            else:
                                cov_zdzx_amount = '0'
                                cov_zdzx = '0'
                            if List['riskCode'] == 'M':  #
                                cov_291_amount = List['amount']
                                cov_291 = List['premium']
                            else:
                                cov_291_amount = '0'
                                cov_291 = '0'
                            if List['riskCode'] == 'X1':
                                BJ_amount = List['amount']
                                BJ = List['premium']
                            else:
                                BJ_amount = '0'
                                BJ = '0'
                            if List['riskCode'] == 'J':  #
                                cov_390_amount = List['amount']
                                cov_390 = List['premium']
                            else:
                                cov_390_amount = '0'
                                cov_390 = '0'
                            if List['riskCode'] == 'Q':  #
                                cov_jdmp_amount = List['amount']
                                cov_jdmp = List['premium']
                            else:
                                cov_jdmp_amount = '0'
                                cov_jdmp = '0'
                            if List['riskCode'] == 'Z2':  #
                                cov_XL_amount = List['amount']
                                cov_XL = List['premium']
                            else:
                                cov_XL_amount = '0'
                                cov_XL = '0'
                            if List['riskCode'] == 'Z3':  #
                                cov_XL_amount = List['amount']
                                cov_XL = List['premium']
                            else:
                                cov_XL_amount = '0'
                                cov_XL = '0'
                            if List['riskCode'] == 'R':  #
                                cov_640_amount = List['amount']
                                cov_640 = List['premium']
                            else:
                                cov_640_amount = '0'
                                cov_640 = '0'
                            return proposalNo_froce,proposalNo_biz
            except:
               if ListIDCT['insuranceType'] =='0':
                   SubDICT = ListIDCT['compulsory']
                   orderNo_froce = ListIDCT['orderNo']  # 定单号
                   proposalNo_froce = ListIDCT['proposalNo']
                   policyNo_froce = ListIDCT['policyNo']  # 保单号
                   startDate_froce = ListIDCT['startDate']  # 起保 日期
                   endDate_froce = ListIDCT['endDate']  # 终日期
                   premium_froce = SubDICT['premium']
                   vehicletaxpremium = SubDICT['tax']
                   payTime_froce = ListIDCT['payTime']
                   policyNo_biz = ''
                   InCreateCallBack = BXDBAction()
                   InCreateCallBack.CreatCallBack_yg(
                                                session_id=SessionID,
                                                usercode = UserCode,
                                                orderno_biz = "",
                                                orderno_force = orderNo_froce,
                                                proposalno_biz = "",
                                                policyno_biz = "",
                                                proposalno_force = proposalNo_froce,
                                                policyno_force = policyNo_froce,
                                                startdate = startDate_froce,
                                                enddate = endDate_froce,
                                                forcepremium = premium_froce,
                                                vehicletaxpremium = vehicletaxpremium,
                                                paytime = payTime_froce,
                                                bizpremium = ""
                        )
                   return proposalNo_froce,policyNo_biz
               if ListIDCT['insuranceType'] =='1':
                   SubDICT = ListIDCT['commercial']
                   List = SubDICT['insuranceList']['insure']
                   orderNo_biz = ListIDCT['orderNo']
                   policyNo_biz = ListIDCT['policyNo']
                   proposalNo_biz = ListIDCT['proposalNo']
                   policyNo_biz = ListIDCT['policyNo']
                   startDate_biz = ListIDCT['startDate']  # 起保 日期
                   endDate_biz = ListIDCT['endDate']  # 终日期
                   premium_biz = SubDICT['premium']
                   payTime = ListIDCT['payTime']
                   proposalNo_froce = ''
                   InCreateCallBack = BXDBAction()
                   InCreateCallBack.CreatCallBack_yg(
                                                session_id=SessionID,
                                                usercode = UserCode,
                                                orderno_biz = orderNo_biz,
                                                orderno_force = "",
                                                proposalno_biz = proposalNo_biz,
                                                policyno_biz = policyNo_biz,
                                                proposalno_force = "",
                                                policyno_force = "",
                                                startdate = startDate_biz,
                                                enddate = endDate_biz,
                                                forcepremium = "",
                                                vehicletaxpremium = "",
                                                paytime = payTime,
                                                bizpremium = ""
                        )
                   try:
                       for i in range(len(List)):
                                NewDICT = List[i]
                                if NewDICT['riskCode'] == 'A':
                                    cov_200_amount = NewDICT['amount']
                                    cov_200 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'B':
                                    cov_600_amount = NewDICT['amount']
                                    cov_600 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'D3':
                                    cov_701_amount = NewDICT['amount']
                                    cov_701 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'D4':
                                    cov_702_amount = NewDICT['amount']
                                    cov_702 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'G1':
                                    cov_500_amount = NewDICT['amount']
                                    cov_500 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'F':
                                    cov_231_amount = NewDICT['amount']
                                    cov_231 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'Z':
                                    cov_310_amount = NewDICT['amount']
                                    cov_310 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'L':
                                    cov_210_amount = NewDICT['amount']
                                    cov_210 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'Q3':  # 指定厂专修
                                    cov_zdzx_amount = NewDICT['amount']
                                    cov_zdzx = NewDICT['premium']
                                if NewDICT['riskCode'] == 'M':  #
                                    cov_291_amount = NewDICT['amount']
                                    cov_291 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'X1':
                                    BJ_amount = NewDICT['amount']
                                    BJ = NewDICT['premium']
                                if NewDICT['riskCode'] == 'J':  #
                                    cov_390_amount = NewDICT['amount']
                                    cov_390 = NewDICT['premium']
                                if NewDICT['riskCode'] == 'Q':  #
                                    cov_jdmp_amount = NewDICT['amount']
                                    cov_jdmp = NewDICT['premium']
                                if NewDICT['riskCode'] == 'Z2':  #
                                    cov_XL_amount = NewDICT['amount']
                                    cov_XL = NewDICT['premium']
                                if NewDICT['riskCode'] == 'Z3':  #
                                    cov_XL_amount = NewDICT['amount']
                                    cov_XL = NewDICT['premium']
                                if NewDICT['riskCode'] == 'R':  #
                                    cov_640_amount = NewDICT['amount']
                                    cov_640 = NewDICT['premium']
                       return proposalNo_froce,policyNo_biz
                   except:
                       if List['riskCode'] == 'A':
                           cov_200_amount = NewDICT['amount']
                           cov_200 = NewDICT['premium']
                       else:
                           cov_200_amount = '0'
                           cov_200 = '0'
                       if List['riskCode'] == 'B':
                           cov_600_amount = NewDICT['amount']
                           cov_600 = NewDICT['premium']
                       else:
                           cov_600_amount = '0'
                           cov_600 = '0'
                       if List['riskCode'] == 'D3':
                           cov_701_amount = NewDICT['amount']
                           cov_701 = NewDICT['premium']
                       else:
                           cov_701_amount = '0'
                           cov_701 = '0'
                       if List['riskCode'] == 'D4':
                           cov_702_amount = NewDICT['amount']
                           cov_702 = NewDICT['premium']
                       else:
                           cov_702_amount = '0'
                           cov_702 = '0'
                       if List['riskCode'] == 'G1':
                           cov_500_amount = NewDICT['amount']
                           cov_500 = NewDICT['premium']
                       else:
                           cov_500_amount = '0'
                           cov_500 = '0'
                       if List['riskCode'] == 'F':
                           cov_231_amount = NewDICT['amount']
                           cov_231 = NewDICT['premium']
                       else:
                           cov_231_amount = '0'
                           cov_231 = '0'
                       if List['riskCode'] == 'Z':
                           cov_310_amount = NewDICT['amount']
                           cov_310 = NewDICT['premium']
                       else:
                           cov_310_amount = '0'
                           cov_310 = '0'
                       if List['riskCode'] == 'L':
                           cov_210_amount = NewDICT['amount']
                           cov_210 = NewDICT['premium']
                       else:
                           cov_210_amount = '0'
                           cov_210 = '0'
                       if List['riskCode'] == 'Q3':  # 指定厂专修
                           cov_zdzx_amount = NewDICT['amount']
                           cov_zdzx = NewDICT['premium']
                       else:
                           cov_zdzx_amount = '0'
                           cov_zdzx = '0'
                       if List['riskCode'] == 'M':  #
                           cov_291_amount = NewDICT['amount']
                           cov_291 = NewDICT['premium']
                       else:
                           cov_291_amount = '0'
                           cov_291 = '0'
                       if List['riskCode'] == 'X1':
                           BJ_amount = NewDICT['amount']
                           BJ = NewDICT['premium']
                       else:
                           BJ_amount = '0'
                           BJ = '0'
                       if List['riskCode'] == 'J':  #
                           cov_390_amount = NewDICT['amount']
                           cov_390 = NewDICT['premium']
                       else:
                           cov_390_amount = '0'
                           cov_390 = '0'
                       if List['riskCode'] == 'Q':  #
                           cov_jdmp_amount = NewDICT['amount']
                           cov_jdmp = NewDICT['premium']
                       else:
                           cov_jdmp_amount = '0'
                           cov_jdmp = '0'
                       if List['riskCode'] == 'Z2':  #
                           cov_XL_amount = NewDICT['amount']
                           cov_XL = NewDICT['premium']
                       else:
                           cov_XL_amount = '0'
                           cov_XL = '0'
                       if List['riskCode'] == 'Z3':  #
                           cov_XL_amount = NewDICT['amount']
                           cov_XL = NewDICT['premium']
                       else:
                           cov_XL_amount = '0'
                           cov_XL = '0'
                       if List['riskCode'] == 'R':  #
                           cov_640_amount = NewDICT['amount']
                           cov_640 = NewDICT['premium']
                       else:
                           cov_640_amount = '0'
                           cov_640 = '0'
                       return proposalNo_froce,policyNo_biz
    def Send(self,Is120,Is125,Is126,Send,Interface,SessionID=False):
        if SessionID:
            SessID = SessionID
        else:
            SessID = self.SessionID
        InVal=(
            SessID,
            self.AddTime
        )
        SendVal = InVal + Send
        #打开文件
        File = WEB_ROOT + "/bxxml/yangguang/"+str(Interface)+".xml"
        #读文件
        FileOpen = open(File).read()
        FileOpen = FileOpen.replace("\n","")
        #替换空格
        result, number = re.subn(">(\s{1,})<", "><", FileOpen)
        result = result % SendVal
        if Is125:
            InputsList = "<Request><Order>%s</Order></Request>" % (
                re.findall("<Order>(.*?)</Order>", result)[0])
        elif Is126:
            InputsList = "<Request>%s</Request>" % (
                re.findall("<Request>(.*?)</Request>", result)[0])
        elif Is120:
            InputsList = "<Request><Order>%s</InputsList></Request>" % (
                re.findall("<Order>(.*?)</InputsList>", result)[0])
        else:
            InputsList = "<Request><InputsList>%s</InputsList></Request>"%(re.findall("<InputsList>(.*?)</InputsList>",result)[0])
        Mysign = self.sign.rsa_sign(data=InputsList,Flag=True)
        result = result.replace("<!--[SIGN]-->", str(Mysign))
        self.EchoLog(msg="接口"+str(Interface)+"发送",data=result)
        try:
            # webservice = httplib.HTTP("1.202.156.227:7002")
            webservice = httplib.HTTP("chexian.sinosig.com")
            webservice.putrequest("POST", "/InterFaceServlet")
            # webservice.putheader("Host", "1.202.156.227:7002")
            webservice.putheader("Host", "chexian.sinosig.com")
            webservice.putheader("Connection", "close")
            webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
            webservice.putheader("Content-length", "%d" % len(result))
            webservice.endheaders()
            webservice.send(result)
            webservice.getreply()
            ReXML = webservice.getfile().read()
            return ReXML
        except:
            ReXML='''<?xml version="1.0" encoding="GBK" standalone="yes"?><PackageList><Package><Header><Version>2</Version><RequestType>100</RequestType><InsureType>100</InsureType><SessionId></SessionId><SendTime></SendTime><Status>100</Status><ErrorMessage>网络异常！请稍后再试</ErrorMessage><SellerId>2015061901</SellerId></Header></Package></PackageList>'''
            return ReXML

    def EchoLog(self,msg='',data='',status=1):
        if status == 0:
            print("\n")
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>[ start %s start ]<<<<<<<<<<<<<<<<<<<<<<<<" %msg)
            print(data)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>[ end %s end ]<<<<<<<<<<<<<<<<<<<<<<<<<<<<" %msg)
        else:
            pass
class Sign(object):

    gm = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCpi714LS6BTL2xVPy7tAGPd2muIebSHrKTLqQ2mmUXjaEfHftIH1-slYQbtfTzimX7LO5VJGZtBohOfhMY-YSGEiMFJAmmHefX0SX6dY80FpC_Wgf-l0FVn4NQ5HcIXYMONAF7HXnhSJfgJ4Rp1x7NP1-0mLnhuHWCv1zYtw9gjwIDAQAB"
    sm = "MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAIj6NQC+WNcUoJ1IGoHwtmpFMjjdyFNPov4GTRquB/KZPBD/2TSbLyJlOFWuXXCdA8xxdd9n2sX47DIoJxdYGpQjl5MWUxLDAv5/uWtDXDobBZfIzXAk4FfUk84L9UwYwxx4jLmAwyULm7fQWCRWRXgc1omsk480x7WHuDt+Pc+VAgMBAAECgYAzEJQR4uRbymTWPbskFgjrNUCz0nqMFHQ/Hzo/aAGuf1HVRIxFAFViDTojNw2+ncp8vQ+kaaM1iscDK9Tm7wF5DEC9ZQ2ZKGJAxANZRx7EYqVr8yuZpgHXq5pseZXWbuOun4fQkLRqIJB5r/aM5bvsh5HyCIjWPTbMaLkiFTJ6AQJBAM6LMj8W5ZZbkAO9ohNcQ+0L7m1GvhtZ5ShvopM2qJs0qZBqvznZezmerrQfSVHUFYzKVIo4EY83DVXMAUmoCwkCQQCpxrPvF/unwagXBAdxd1/zh9e0zc/cpHs/0W8o62aVl4conDFYIN/ARjDWpTCOqTA7O7ggO1CnRcjkPkMbuactAkA2bwj3B5nKXqc91SR55b8hIhvcQOCpZK+4UHOQSL926BIoNXngTSjkrqVsYzJ3lmV3jXtqUgyOqfuhuPo950PBAkBT+uhSoshnCRI+oE2WQPiDnHSFCTGC8RHOVajo0tihspy259w4vbowgAf0hS3pw6MKCdZgizawJ4Lh9DJ56nHZAkBjaeKixt3U47NpjjfuLt9ryaR3VSc4Ptv8ocqabAGaZNayhiDUcz1peoxU4dcv6ZnYImd7r2UWTKfKtITnc8bj"

    def rsa_sign(self,data,Flag=False):

        pri_key = RSA.importKey(base64.b64decode(self.sm))
        pkcs = PKCS1_v1_5.new(pri_key)
        digest = MD5.new(data)
        if Flag:
            result = base64.urlsafe_b64encode(pkcs.sign(digest))
            result = str(result).replace("=","")
        else:
            result = base64.b64encode(pkcs.sign(digest))
        return result



    def rsa_verify(self, data, sign):

        pubkey = RSA.importKey(base64.b64decode(self.gm))
        digest = MD5.new(data)
        pkcs = MD5.new(pubkey)
        return pkcs.verify(digest, base64.b64decode(sign))
