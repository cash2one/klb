# -*- coding:utf-8 -*-

import datetime, random, urllib, urllib2, time, httplib
from LYZ.settings import *
import sys, xmltodict, re
from LYZ.common import makeNew
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import MD5
from common import GetCarInfo
from LYZ.common import *
import base64
from common import *

reload(sys)
sys.setdefaultencoding('utf-8')


class AnSheng(object):
    # URL = "http://ws.95550.cn:9999/ecws/mobPhonePayDispatcherController.do"
    WAP_URL = "http://baoxian.95550.cn/payRequestInit.do?ecInsureId=%s&sourceType=weChat"
    URL = "http://pre-net.tpis.tpaic.com:11580/ecws/mobPhonePayDispatcherController.do"
    SellerId = "kalaibao"
    #
    TEST_S_URL = "http://dev.tpis.tpaic.com:14080/selectCarInfo.do?cityCode=340100&searchCode=&pageSize=100&page=1&callback=json"

    def __init__(self,
                 cityCode=None,
                 licenseNo=None,
                 ownerName=None,
                 mobilePhone=None,
                 engine="",
                 vin="",
                 user_id=""
                 ):
        self.user_id = user_id
        # 身份证号
        self.ownerId = makeNew()
        # 车牌号
        self.licenseNo = licenseNo
        # 车主姓名
        self.ownerName = ownerName
        # 车主手机
        self.mobilePhone = mobilePhone
        # 城市编码
        self.cityCode = cityCode
        # 发动机号
        self.engine = engine
        # 车架号
        self.vin = vin
        # 车辆注册日期
        self.firstRegisterDate = str((datetime.date.today() + datetime.timedelta(days=-365 * 2)).strftime("%Y-%m-%d"))

        # 商业保险起期
        self.bizBeginDate = str((datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"))
        # 交强险起期
        self.forceBeginDate = str((datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"))
        # 本地订单号
        self.TBorder = str(datetime.datetime.now().strftime("%Y%m%d")) + str(
            random.randint(10000000, 99999999))
        self.ItemId = str(datetime.datetime.now().strftime("%Y%m%d")) + str(
            random.randint(100000, 999999))
        self.SessionID = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + str(
            random.randint(100000000000000000, 999999999999999999))

        self.AddTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.sign = Sign()
    def Get_100(self):
        """
        向安盛服务器发送数据，并接收返回xml，并转化为字典
        Args:
            参数自己写
        Returns:
            自己写

        """
        # 查询车型

        self.CarInfoArr = GetCarInfo(Value=self.vin)
        ASInfo = self.CarInfoArr.GetDBSelect(type="axatp")
        try:
            if ASInfo:
                self.Key = ASInfo['key']
                self.value = ASInfo['value']
            else:
                self.CarInfo = self.CarInfoArr.GetAnshengCarInfoNEW(self.cityCode)
                self.Key = self.CarInfo['id']
                self.value = self.CarInfo['name']
        except:
            if ASInfo:
                self.Key = ASInfo['key']
                self.value = ASInfo['value']
            else:
                self.CarInfo = self.CarInfoArr.GetAnshengCarInfo(self.cityCode)
                self.Key = self.CarInfo['key']
                self.value = self.CarInfo['value']
        # print(self.licenseNo)
        SendVal = (
            self.SessionID,
            self.AddTime,
            str(self.cityCode).encode("GBK"),
            str(self.licenseNo).encode("GBK")
        )

        if self.cityCode == "310100":
            X =""
            ErrorMessage = "该城市不可投保!"
            REDICT = {"error":"1","msg":ErrorMessage}
            return ErrorMessage, REDICT, X
        X = self.Send(Interface="100", SendVal=SendVal)
        REDICT = xmltodict.parse(X, encoding="utf-8")
        MsgAll = json.loads(json.dumps(REDICT))
        MsgHeader = MsgAll['PackageList']['Package']['Header']
        ErrorMessage = MsgHeader['ErrorMessage']
        if ErrorMessage <> "" and ErrorMessage <> None:
            REDICT = {"error": "1", "msg": ErrorMessage}
            return ErrorMessage, REDICT, X

        return ErrorMessage, REDICT, X

    # 保费计算接口
    def Get_105(self):
        ErrorMessage, REDICT, X = self.Get_100()
        if ErrorMessage <> "" and ErrorMessage <> None:
            return ErrorMessage, REDICT, X
        REDICTNEW = REDICT['PackageList']['Package']['Response']['TagsList']['Tags']
        RE = self.GetDate(REDICTNEW=REDICTNEW)
        if RE['bizBeginDate'] <> "":
            return ErrorMessage, REDICT, RE
        try:
            GetRE = GetregisterDate()
            self.firstRegisterDateNEW = GetRE.GetregisterDate(licenseno=self.licenseNo,vin=self.vin,engineNo=self.engine,CityCode=self.cityCode)
        except:
            self.firstRegisterDateNEW=self.firstRegisterDate
        SendVal = (
            self.SessionID,
            self.AddTime,
            self.Key.encode("GBK"),
            str(self.engine).encode("GBK"),
            str(self.vin).encode("GBK"),
            self.firstRegisterDate,
            self.value.encode("GBK"),
            self.bizBeginDate.encode("GBK"),
            self.firstRegisterDateNEW.encode("GBK"),
            str(self.ownerName).encode("GBK")
        )
        X = self.Send(Interface="105", SendVal=SendVal)
        REDICT = xmltodict.parse(X, encoding="utf-8")
        MsgAll = json.loads(json.dumps(REDICT))
        MsgHeader = MsgAll['PackageList']['Package']['Header']
        ErrorMessage = MsgHeader['ErrorMessage']
        if ErrorMessage <> "" and ErrorMessage <> None:
            REDICT = {"error": "1", "msg": ErrorMessage}
            return ErrorMessage, REDICT, X
        NewDict = MsgAll['PackageList']['Package']['Response']['TagsList']['Tags']
        REDICT = self.ShowList(NewDict)
        if REDICT['BizPremium'] <> "0":
            BizFlag = "1"
        else:
            BizFlag = "0"
        if REDICT['forcePremium'] <> "0":
            FroceFlag = "1"
        else:
            FroceFlag = "0"
        if REDICT['BizPremium'] == "":
            REDICT['BizPremium'] = 0
        if REDICT['TotalPremium']=="":
            REDICT['TotalPremium'] = 0
        InCreateHeBao = BXDBAction()
        InCreateHeBao.CraetPriceinfo_as(
                                    vin=self.vin,
                                    BizFlag=BizFlag,
                                    FroceFlag=FroceFlag,
                                    cov_200=REDICT['VehicleLoss'],
                                    cov_600=REDICT['SanZheBE'],
                                    cov_701=REDICT['ZeRenSJBE'],
                                    cov_702=REDICT['ZeRenCKBE'],
                                    cov_500=REDICT['DaoQiang'],
                                    cov_290=REDICT['SheShui'],
                                    cov_231=REDICT['BoLiPS'],
                                    cov_210=REDICT['HuaHen'],
                                    cov_310=REDICT['ZiRan'],
                                    cov_900=REDICT['BuJiTY'],
                                    cov_910=REDICT['BuJiHB'],
                                    cov_911=REDICT['BUJiCS'],
                                    cov_912=REDICT['BuJiSZ'],
                                    cov_921=REDICT['BuJiDQ'],
                                    cov_922=REDICT['BUJIHH'],
                                    cov_923=REDICT['BUJIZR'],
                                    cov_924=REDICT['BUJISS'],
                                    cov_928=REDICT['BuJiSJ'],
                                    cov_929=REDICT['BuJiCK'],
                                    cov_930=REDICT['BuJiCSRY'],
                                    cov_931=REDICT['BuJiFJ'],
                                    biztotalpremium=int(REDICT['BizPremium'] * 100),
                                    totalpremium=int(REDICT['TotalPremium'] * 100),
                                    standardpremium=int(REDICT['TotalPremium'] * 100),
                                    forcepremium=int(REDICT['ForePremium'] * 100),
                                    bizbegindate=self.bizBeginDate,
                                    forcebegindate=self.forceBeginDate,
                                    vehicletaxpremium=int(REDICT['VehTaxPremium'] * 100),
                                    forcepremium_f=int(REDICT['forcePre'] * 100),
                                    session_id= self.SessionID,
                                    ownername=self.ownerName

        )
        InCreateHeBao.CreatPayinfo_AS(
                                    vin=self.vin,
                                    tborder_id="",
                                    item_id="",
                                    insuredname=self.ownerName,
                                    insuredidno="",
                                    insuredmobile="",
                                    insuredidtype="",
                                    insuredgender="",
                                    insuredbirthday="",
                                    ownername=self.ownerName,
                                    owneridno="",
                                    ownermobile="",
                                    owneremail="",
                                    owneridtype="",
                                    ownergender="",
                                    ownerbirthday="",
                                    ownerage="",
                                    addresseename="",
                                    addresseemobile="",
                                    addresseeprovince="",
                                    addresseecity="",
                                    addresseetown="",
                                    addresseedetails="",
                                    applicantname=self.ownerName,
                                    applicantidno="",
                                    applicantmobile="",
                                    applicantemail="",
                                    applicantbirthday="",
                                    applicantgender="",
                                    applicantidtype="",
                                    bxgs_type="axatp",
                                    status = "0",
                                    session_id =self.SessionID,
                                    proposalno_biz='',
                                    proposalno_force='',
                                    ID=''
                                    )
        return ErrorMessage, REDICT, X

    def Get_110(self, CHESHUN="1", SANZHE='50000', DAOQIANG='1', SHIJI='10000', CHENGKE='10000', BOLI='0',
                JIAOQIANG='1', ZIRAN='0', HUAHEN='0', SHESHUI='0', CHESHUN_BJ='0', SANZHE_BJ='0', DAOQIANG_BJ='0',
                SHIJI_BJ='0', CHENGKE_BJ='0', FUJIA_BJ='0'):
        ErrorMessage, REDICT, X = self.Get_105()
        if ErrorMessage:
            return ErrorMessage, REDICT, X
        SendVal = (
            self.SessionID,
            self.AddTime,
            CHESHUN.encode("GBK"),  # 机动车损失险 200
            SANZHE.encode("GBK"),   # 第三者责任险  600
            DAOQIANG.encode("GBK"), # 盗抢险  500
            SHIJI.encode("GBK"),  # 司机责任险  cov_701
            CHENGKE.encode("GBK"),  # 乘客责任险     cov_702
            BOLI.encode("GBK"),  # 玻璃险      cov_231
            JIAOQIANG.encode("GBK"),  # 交强险
            ZIRAN.encode("GBK"),  # 自燃损失险
            HUAHEN.encode("GBK"),  # 划痕险
            SHESHUI.encode("GBK"),  # 涉水险
            '0',  # 不计免赔特约条款cov_900
            '0',  # 不计免赔所有条款cov_910
            CHESHUN_BJ.encode("GBK"),  # 不计免赔车损cov_911
            SANZHE_BJ.encode("GBK"),  # 不计免赔三者cov_912
            DAOQIANG_BJ.encode("GBK"),  # 不计免赔盗抢cov_921
            HUAHEN,  # 不计免赔车身划痕cov_922
            '0',  # 不计免赔自燃cov_923
            '0',  # 不计免赔涉水cov_924
            SHIJI_BJ.encode("GBK"),  # 不计免赔责任司机cov_928
            CHENGKE_BJ.encode("GBK"),  # 不计免赔责任乘客cov_929
            '0',  # 不计免赔人员责任险cov_930
            FUJIA_BJ.encode("GBK"),  # 不计免赔附加险cov_931
        )
        X = self.Send(Interface="110", SendVal=SendVal)
        REDICT = xmltodict.parse(X, encoding="utf-8")
        MsgAll = json.loads(json.dumps(REDICT))
        MsgHeader = MsgAll['PackageList']['Package']['Header']
        ErrorMessage = MsgHeader['ErrorMessage']
        if ErrorMessage <> "" and ErrorMessage <> None:
            Status = REDICT['PackageList']['Package']['Header']['Status']
            if Status == '400':
                REDICT = {"error": "1", "msg": ErrorMessage}
                return ErrorMessage, REDICT, X
            if Status == '500':
                REDICT = {"error": "1", "msg": "此保单正在核保中！请稍后！"}
                return ErrorMessage, REDICT, X
            if Status == '':
                pass
            if Status == '':
                pass
        NewDict = MsgAll['PackageList']['Package']['Response']['TagsList']['Tags']
        REDICT = self.ShowList(NewDict, t="optional",ForceFlag=JIAOQIANG)
        if REDICT['BizPremium'] <> "0":
            BizFlag = "1"
        else:
            BizFlag = "0"
        InCreateHeBao = BXDBAction()
        InCreateHeBao.CraetPriceinfo_as(
                                    vin = self.vin,
                                    BizFlag = BizFlag,
                                    FroceFlag= JIAOQIANG,
                                    cov_200 = CHESHUN,
                                    cov_600 = SANZHE,
                                    cov_701 = SHIJI,
                                    cov_702 = CHENGKE,
                                    cov_500 = DAOQIANG,
                                    cov_290 = SHESHUI,
                                    cov_231 = BOLI,
                                    cov_210 = HUAHEN,
                                    cov_310 = ZIRAN,
                                    cov_900 = "0",
                                    cov_910 = "0",
                                    cov_911 = CHESHUN_BJ,
                                    cov_912 = SANZHE_BJ,
                                    cov_921 = DAOQIANG_BJ,
                                    cov_922 = "0",
                                    cov_923 = "0",
                                    cov_924 = "0",
                                    cov_928 = SHIJI_BJ,
                                    cov_929 = CHENGKE_BJ,
                                    cov_930 = "0",
                                    cov_931 = "0",
                                    biztotalpremium = int(REDICT['BizPremium']*100),
                                    totalpremium = int(REDICT['totalPremium']*100),
                                    standardpremium = int(REDICT['totalPremium']*100),
                                    forcepremium = int(REDICT['ForePremium']*100),
                                    bizbegindate = self.bizBeginDate,
                                    forcebegindate = self.forceBeginDate,
                                    vehicletaxpremium = int(REDICT['VehTaxPremium']*100),
                                    forcepremium_f=int(REDICT['forcePre']*100),
                                    session_id= self.SessionID,
                                    ownername=self.ownerName
        )
        if REDICT['ZiRan'] < 0:
            REDICT['ZiRan'] = str(REDICT['ZiRan'])[1:] + "(赠送)"
        if REDICT['SheShui'] < 0:
            REDICT['SheShui'] = str(REDICT['SheShui'])[1:] + "(赠送)"
        if REDICT['HuaHen'] < 0:
            REDICT['HuaHen'] = str(REDICT['HuaHen'])[1:] + "(赠送)"
        if REDICT['BoLiPS'] < 0:
            REDICT['BoLiPS'] = str(REDICT['BoLiPS'])[1:] + "(赠送)"
        InCreateHeBao.CreatPayinfo_AS(
                                    vin=self.vin,
                                    tborder_id="",
                                    item_id="",
                                    insuredname=self.ownerName,
                                    insuredidno="",
                                    insuredmobile="",
                                    insuredidtype="",
                                    insuredgender="",
                                    insuredbirthday="",
                                    ownername=self.ownerName,
                                    owneridno="",
                                    ownermobile="",
                                    owneremail="",
                                    owneridtype="",
                                    ownergender="",
                                    ownerbirthday="",
                                    ownerage="",
                                    addresseename="",
                                    addresseemobile="",
                                    addresseeprovince="",
                                    addresseecity="",
                                    addresseetown="",
                                    addresseedetails="",
                                    applicantname=self.ownerName,
                                    applicantidno="",
                                    applicantmobile="",
                                    applicantemail="",
                                    applicantbirthday="",
                                    applicantgender="",
                                    applicantidtype="",
                                    bxgs_type="axatp",
                                    status = "0",
                                    session_id =self.SessionID,
                                    proposalno_biz="",
                                    proposalno_force="",
                                    ID = ""

        )
        return ErrorMessage, REDICT, X


    def Get_115(self,IsterInfo,vin='', applicantname='', applicantidno='', applicantmobile='', applicantemail='',
                 insuredname='', insuredidno='', insuredmobile='', addresseeprovince='', addresseecity='',
                 addresseetown='', addresseename='',addresseemobile="", addresseedetails='', ownername='', owneridno='',
                 ID=''):
        # cda20150909 修改
        Priceinfo = BXDBAction()
        if ID <> "" and ID <> None:
            Priceinfo = Priceinfo.GetPriceinfo_as(ID=ID)
        else:
            Priceinfo = Priceinfo.GetPriceinfo_as(vin=vin,ownername=ownername)
        if Priceinfo == False:
            PayUrl = False
            X = False
            ErrorMessage = "投保人输入信息有误"
            REDICT = {"error": "1", "msg": ErrorMessage}
            return X,REDICT, ErrorMessage,PayUrl
        SendVal = (
            str(Priceinfo.session_id).encode('GBK'),
            str(self.AddTime).encode('GBK'),
            str(self.TBorder).encode('GBK'),  # 本地生成订单号
            str(Priceinfo.totalpremium).encode('GBK'),  # 保费
            str(self.TBorder).encode('GBK'),  #
            str(self.ItemId).encode('GBK'),  # 产品ID
            str(Priceinfo.forcepremium).encode('GBK'),  # 保费
            str(self.TBorder).encode('GBK'),  #
            str(self.ItemId).encode('GBK'),
            str(Priceinfo.biztotalpremium).encode('GBK'),
            str(Priceinfo.forceflag).encode('GBK'),
            str(Priceinfo.cov_200).encode('GBK'),  # 机动车损失险
            str(Priceinfo.cov_210).encode('GBK'),  # 划痕险
            str(Priceinfo.cov_231).encode('GBK'),  # 玻璃险
            str(Priceinfo.cov_290).encode('GBK'),  # 涉水险
            str(Priceinfo.cov_310).encode('GBK'),  # 自燃损失险
            str(Priceinfo.cov_500).encode('GBK'),  # 盗抢险
            str(Priceinfo.cov_600).encode('GBK'),  # 三者险
            str(Priceinfo.cov_701).encode('GBK'),  # 责任司机
            str(Priceinfo.cov_702).encode('GBK'),  # 责任乘客
            str(Priceinfo.cov_900).encode('GBK'),  # 不计免赔特约条款
            str(Priceinfo.cov_911).encode('GBK'),  # 不计免赔车损
            str(Priceinfo.cov_912).encode('GBK'),  # 不计三者
            str(Priceinfo.cov_921).encode('GBK'),  # 不计免赔险（机动车盗抢险
            str(Priceinfo.cov_928).encode('GBK'),  # 不计免赔险(司机)
            str(Priceinfo.cov_922).encode('GBK'),  # 不计划痕
            str(Priceinfo.cov_923).encode('GBK'),  # 不计免赔险（自燃险
            str(Priceinfo.cov_924).encode('GBK'),  # 不计免赔险（涉水险）
            str(Priceinfo.cov_929).encode('GBK'),  # 不计免赔险（车上人员责任险（乘客））
            str(Priceinfo.cov_930).encode('GBK'),  # 不计免赔险（车上人员责任险
            str(Priceinfo.cov_931).encode('GBK'),  # 不计免赔（附加险）
            str(Priceinfo.totalpremium).encode('GBK'),  # 总保费
            str(Priceinfo.standardpremium).encode('GBK'),  # 应交保费
            str(Priceinfo.biztotalpremium).encode('GBK'),  # 商业保费
            str(Priceinfo.bizflag).encode('GBK'),  # 是否投保商业险
            str(applicantmobile).encode('GBK'),  # 车主电话
            str(owneridno).encode('GBK'),  # 车主身份证号
            str(ownername).encode('GBK'),  # 车主姓名
            str(insuredname).encode('GBK'),  # 被保险人姓名
            str(insuredidno).encode('GBK'),  # 被保险人身份证号
            str(insuredmobile).encode('GBK'),  # 被保险人电话
            str(applicantname).encode('GBK'),  # 投保人姓名
            str(applicantidno).encode('GBK'),  # 投保人身份证号
            str(applicantmobile).encode('GBK'),  # 投保人电话
            str(addresseename).encode('GBK'),  # 收件人姓名
            str(addresseemobile).encode('GBK'),  # 收件人电话
            str(addresseeprovince).encode('GBK'),  # 省份代码
            str(addresseecity).encode('GBK'),  # 城市代码
            str(addresseetown).encode('GBK'),  # 区县代码
            str(addresseedetails).encode('GBK'),  # 详细地址
            str(Priceinfo.bizbegindate).encode('GBK'),  # 商业险起期
            str(Priceinfo.forcebegindate).encode('GBK'),  # 交强险起期
            str(Priceinfo.vehicletaxpremium).encode('GBK'),  # 车船税
            str(Priceinfo.forcepremium).encode('GBK'),  # 交强总保费
            str(Priceinfo.forcepremium_f).encode('GBK'),  # 交强险
        )
        InCreateHeBao = BXDBAction()
        InCreateHeBao.CreatPayinfo_AS(
                                    vin=vin,
                                    tborder_id=self.TBorder,
                                    item_id=self.ItemId,
                                    insuredname=insuredname,
                                    insuredidno=insuredidno,
                                    insuredmobile=insuredmobile,
                                    insuredidtype="",
                                    insuredgender="",
                                    insuredbirthday="",
                                    ownername=ownername,
                                    owneridno=owneridno,
                                    ownermobile=applicantmobile,
                                    owneremail="",
                                    owneridtype="",
                                    ownergender="",
                                    ownerbirthday="",
                                    ownerage="",
                                    addresseename=addresseename,
                                    addresseemobile=addresseemobile,
                                    addresseeprovince=addresseeprovince,
                                    addresseecity=addresseecity,
                                    addresseetown=addresseetown,
                                    addresseedetails=addresseedetails,
                                    applicantname=applicantname,
                                    applicantidno=applicantidno,
                                    applicantmobile=applicantmobile,
                                    applicantemail=applicantemail,
                                    applicantbirthday="",
                                    applicantgender="",
                                    applicantidtype="",
                                    bxgs_type="axatp",
                                    status = "1",
                                    session_id =Priceinfo.session_id,
                                    proposalno_biz="",
                                    proposalno_force="",
                                    ID=ID
        )
        X = self.Send(Interface="115", SendVal=SendVal, Is115=True)
        REDICT = xmltodict.parse(X, encoding="utf-8")
        ErrorMessage = REDICT['PackageList']['Package']['Header']['ErrorMessage']
        if ErrorMessage <> "" and ErrorMessage <> None:

            PayUrl =False
            REDICT = {"error": "1", "msg": ErrorMessage}
            return ErrorMessage, REDICT, X,PayUrl
        NEWLIST = REDICT['PackageList']['Package']['Response']['Order']['SubOrderList']['SubOrder']
        ProposalNo_biz,ProposalNo_force = self.Get_ProposalNo(NEWLIST=NEWLIST)
        InCreateHeBao.CreatPayinfo_AS(
                                    vin=vin,
                                    tborder_id=self.TBorder,
                                    item_id=self.ItemId,
                                    insuredname=insuredname,
                                    insuredidno=insuredidno,
                                    insuredmobile=insuredmobile,
                                    insuredidtype="",
                                    insuredgender="",
                                    insuredbirthday="",
                                    ownername=ownername,
                                    owneridno=owneridno,
                                    ownermobile=applicantmobile,
                                    owneremail="",
                                    owneridtype="",
                                    ownergender="",
                                    ownerbirthday="",
                                    ownerage="",
                                    addresseename=addresseename,
                                    addresseemobile=addresseemobile,
                                    addresseeprovince=addresseeprovince,
                                    addresseecity=addresseecity,
                                    addresseetown=addresseetown,
                                    addresseedetails=addresseedetails,
                                    applicantname=applicantname,
                                    applicantidno=applicantidno,
                                    applicantmobile=applicantmobile,
                                    applicantemail=applicantemail,
                                    applicantbirthday="",
                                    applicantgender="",
                                    applicantidtype="",
                                    bxgs_type="axatp",
                                    status = "1",
                                    session_id =Priceinfo.session_id,
                                    proposalno_biz=ProposalNo_biz,
                                    proposalno_force=ProposalNo_force,
                                    ID=ID
        )
        if IsterInfo:
            if REDICT['PackageList']['Package']['Response']['Order']['PayURL'] <> "":
                PayUrl = REDICT['PackageList']['Package']['Response']['Order']['PayURL']
                order= re.findall(r'[0-9]',PayUrl)
                order=''.join(order)
                PayUrl = self.WAP_URL % order
            else:
                PayUrl = False
                ErrorMessage = "对不起,系统异常！稍后再试！"
                REDICT = {"error": "1", "msg": ErrorMessage}
                return ErrorMessage, REDICT, X,PayUrl
        else:
            PayUrl = REDICT['PackageList']['Package']['Response']['Order']['PayURL']
        if PayUrl == "" or PayUrl == None:
            PayUrl = False
            ErrorMessage = "对不起,系统异常！稍后再试！"
            REDICT = {"error": "1", "msg": ErrorMessage}
            return ErrorMessage, REDICT, X,PayUrl

        return X,REDICT, ErrorMessage,PayUrl
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
                        print(ProposalNo_biz)
                    if NEWDICT['@type'] == 'force':
                        ProposalNo_force= NEWDICT['ProposalNo']
                        print(ProposalNo_force)

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
    # 回调接口
    def CallBack(self, xml):
        BDAction = BXDBAction()
        BDAction.CreatCallBackLog(xml=xml,bxgs='axatp',interface_type='')
        try:
            RE = xmltodict.parse(xml, encoding="utf-8")
        except:
            msg = "XML格式错误"
            SessionID = "NULL"
            RE = self.ReContent(msg=msg,SessionID=SessionID)
            return HttpResponse(RE, content_type="application/xml")

        if RE['PackageList']['Package']['Header']['RequestType'] == "" or \
             RE['PackageList']['Package']['Header']['RequestType'] == None:  # 请求类型
            msg = "RequestType不能为空"
            SessionID = 'NULL'
            RE = self.ReContent(msg=msg,SessionID=SessionID)
            return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
        else:
            # 核保回调

            if RE['PackageList']['Package']['Header']['RequestType'] == "215":
                return self.CallBack_215(RE=RE,xml=xml)
            # 承保回调
            if RE['PackageList']['Package']['Header']['RequestType'] == "230":
                return self.CallBack_230(RE=RE, xml=xml)


    def CallBack_215(self, RE,xml):
        BDAction = BXDBAction()
        BDAction.CreatCallBackLog(xml=xml,bxgs='axatp',interface_type='215')
        if RE['PackageList']['Package']['Header']['SessionId'] == "" or \
                RE['PackageList']['Package']['Header']['SessionId'] == None:
            msg ="SessionId不能为空"
            SessionID = "NULL"
            RE = self.ReContent(msg=msg,SessionID=SessionID)
            return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
        else:
            SessionID = RE['PackageList']['Package']['Header']['SessionId']
        if RE['PackageList']['Package']['Response']['Order']['TBOrderId'] == "" or \
                RE['PackageList']['Package']['Response']['Order']['TBOrderId'] == None:
            msg = "TBorder不能为空"
            SessionID = SessionID
            RE = self.ReContent(msg=msg,SessionID=SessionID)
            return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
        else:
            Premium = RE['PackageList']['Package']['Response']['Order']['Premium']
        if RE['PackageList']['Package']['Response']['Order']['SubOrderList'] == '' or\
             RE['PackageList']['Package']['Response']['Order']['SubOrderList'] == None:
            msg = "SubOrderList不能为空"
            SessionID = SessionID
            RE = self.ReContent(msg=msg,SessionID=SessionID)
            return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
        else:
            RELIST = RE['PackageList']['Package']['Response']['Order']['SubOrderList']['SubOrder']
            if len(RELIST) > 2:
                if RELIST['@type'] == 'biz':
                    BizPremium = RELIST['Premium']
                    BizProposalNo = RELIST['ProposalNo'] # 投保单号
                    ItemId = RELIST['ItemId']
                elif RELIST['@type'] == 'force':
                    ForcePremium = RELIST['Premium']
                    ForceProposalNo = RELIST['ProposalNo'] # 投保单号
                    ItemId = RELIST['ItemId']
            else:
                for i in range(len(RELIST)):
                      if RELIST[i]['@type'] == "biz":
                          BizPremium = RELIST[i]['Premium']
                          BizProposalNo = RELIST[i]['ProposalNo'] # 投保单号
                          ItemId = RELIST[i]['ItemId']
                      if RELIST[i]['@type'] == "force":
                          ForcePremium = RELIST[i]['Premium']
                          ForceProposalNo = RELIST[i]['ProposalNo'] # 投保单号
                          ItemId = RELIST[i]['ItemId']
                          break

            tborderid = RE['PackageList']['Package']['Response']['Order']['TBOrderId']
            Status = RE['PackageList']['Package']['Header']['Status']
            DBAction = BXDBAction()
            DBAction.CreatCallBack_as(
                                    sessionid=SessionID,
                                    requesttype="215",
                                    tborderid=tborderid,
                                    premium=Premium,
                                    itemid=ItemId,
                                    bizpremium=BizPremium,
                                    bizproposalno=BizProposalNo,
                                    bizpolicyno="",
                                    forcepremium=ForcePremium,
                                    forceproposalno = ForceProposalNo,
                                    forcepolicyno = "",
                                    status = Status
            )
        return HttpResponse(xml, content_type="application/xml")
    def CallBack_230(self, RE,xml):
        BDAction = BXDBAction()
        BDAction.CreatCallBackLog(xml=xml,bxgs='axatp',interface_type='230')
        if RE['PackageList']['Package']['Header']['SessionId'] == "" or \
                RE['PackageList']['Package']['Header']['SessionId'] == None:
            msg ="SessionId不能为空"
            SessionID = "NULL"
            RE = self.ReContent(msg=msg,SessionID=SessionID)
            return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
        else:
            SessionID = RE['PackageList']['Package']['Header']['SessionId']
        if RE['PackageList']['Package']['Response']['Order']['TBOrderId'] == "" or \
                RE['PackageList']['Package']['Response']['Order']['TBOrderId'] == None:
            msg = "TBorder不能为空"
            SessionID = SessionID
            RE = self.ReContent(msg=msg,SessionID=SessionID)
            return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
        else:
            Premium = RE['PackageList']['Package']['Response']['Order']['Premium']
        if RE['PackageList']['Package']['Response']['Order']['SubOrderList'] == '' or\
                RE['PackageList']['Package']['Response']['Order']['SubOrderList'] == None:
            msg = "SubOrderList不能为空"
            SessionID = SessionID
            RE = self.ReContent(msg=msg,SessionID=SessionID)
            return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
        else:
            RELIST = RE['PackageList']['Package']['Response']['Order']['SubOrderList']['SubOrder']
            if len(RELIST) >2:
                if RELIST['@type'] == 'biz':
                    BizPremium = RELIST['Premium']
                    BizProposalNo = RELIST['ProposalNo'] # 投保单号
                    BizPolicyNo = RELIST['PolicyNo'] # 保单号
                    ItemId = RELIST['ItemId']
                elif RELIST['@type'] == 'force':
                    ForcePremium = RELIST['Premium']
                    ForceProposalNo = RELIST['ProposalNo'] # 投保单号
                    ForcePolicyNo = RELIST['PolicyNo'] # 保单号
                    ItemId = RELIST['ItemId']
            else:
                for i in range(len(RELIST)):
                      if RELIST[i]['@type'] == "biz":
                          BizPremium = RELIST[i]['Premium']
                          BizProposalNo = RELIST[i]['ProposalNo'] # 投保单号
                          BizPolicyNo = RELIST[i]['PolicyNo'] # 保单号
                          ItemId = RELIST[i]['ItemId']
                      if RELIST[i]['@type'] == "force":
                          ForcePremium = RELIST[i]['Premium']
                          ForceProposalNo = RELIST[i]['ProposalNo'] # 投保单号
                          ForcePolicyNo = RELIST[i]['PolicyNo'] # 保单号
                          ItemId = RELIST[i]['ItemId']
                          break
            tborderid = RE['PackageList']['Package']['Response']['Order']['TBOrderId']
            Status = RE['PackageList']['Package']['Header']['Status']
            DBAction = BXDBAction()
            DBAction.CreatCallBack_as(
                                    sessionid=SessionID,
                                    requesttype="230",
                                    tborderid=tborderid,
                                    premium=Premium,
                                    itemid=ItemId,
                                    bizpremium=BizPremium,
                                    bizproposalno=BizProposalNo,
                                    bizpolicyno=BizPolicyNo,
                                    forcepremium=ForcePremium,
                                    forceproposalno = ForceProposalNo,
                                    forcepolicyno = ForcePolicyNo,
                                    status = Status
                                     )
        return HttpResponse(xml, content_type="application/xml")
    def GetDate(self,REDICTNEW):
        bizBeginDate = ""
        forceBeginDate = ""
        for i in range(len(REDICTNEW)):
            if REDICTNEW[i]['@type'] == 'deadline':
                D = REDICTNEW[i]['Tag']
                for n in range(len(D)):
                    Definition = D[n]['Definition']
                    if Definition[n].has_key('#text'):
                        if Definition[n]['#text'] == "date":
                             for m in range(len(Definition)):
                                 if Definition[m]['@name'] == "value":
                                     bizBeginDate = Definition[m]['#text']
                        if Definition[n]['#text'] == "forceBeginDate":
                             for m in range(len(Definition)):
                                 if Definition[m]['@name'] == "value":
                                     forceBeginDate = Definition[m]['#text']
        RE = {}
        RE['bizBeginDate'] = bizBeginDate
        RE['forceBeginDate'] = forceBeginDate
        return RE
    def ShowList(self, NewDict, t="recommend",ForceFlag=''):
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
        try:
                for i in range(len(NewDict)):
                    # 判断
                    if NewDict[i]['@type'] == "force":
                        ForceAll = NewDict[i]['Tag']
                        for n in range(len(ForceAll)):
                            Definition = ForceAll[n]['Definition']
                            for v in range(len(Definition)):
                                if Definition[v].has_key('#text'):
                                    # 交强险价格
                                    if Definition[v]['#text'] == "forcePremium":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                forcePre = Definition[m]['#text']
                                                forcePre = round(float(forcePre) / float(100), 2)
                                                print("交强险的价格是:%s"%forcePre)
                                                REDICT['forcePre'] = forcePre
                                                break

                                    # 车船价格
                                    if Definition[v]['#text'] == "vehicleTaxPremium":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                VehTaxPremium = Definition[m]['#text']
                                                VehTaxPremium = round(float(VehTaxPremium) / float(100), 2)
                                                print("车船的价格是:%s"%forcePre)
                                                REDICT['VehTaxPremium'] = VehTaxPremium
                                                break

                                    # 交强险总价格
                                    if Definition[v]['#text'] == "forceTotalPremium":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                forcePremium = Definition[m]['#text']
                                                forcePremium = round(float(forcePremium) / float(100), 2)
                                                print("交强险的价格是:%s"%forcePre)
                                                REDICT['forcePremium'] = forcePremium
                                                REDICT['ForePremium'] = forcePremium
                                                break
                    if NewDict[i]['@type'] == t:
                        RecommendAll = NewDict[i]['Tag']
                        for n in range(len(RecommendAll)):
                            Definition = RecommendAll[n]['Definition']
                            for v in range(len(Definition)):
                                if Definition[v].has_key('#text'):
                                    # 车损价格
                                    if Definition[v]['#text'] == "cov_200":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                VehicleLoss = Definition[m]['#text']
                                                VehicleLoss = round(float(VehicleLoss) / float(100), 2)
                                                if VehicleLoss < 0:
                                                    VehicleLoss = 0
                                                # print("车损的价格是:%s"%VehicleLoss)
                                                REDICT['VehicleLoss'] = VehicleLoss
                                                break
                                    # 三者
                                    if Definition[v]['#text'] == "cov_600":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                SanZhe = Definition[m]['#text']
                                                SanZhe = round(float(SanZhe) / float(100), 2)
                                                if SanZhe < 0:
                                                    SanZhe = 0
                                                # print("三者的价格是:%s"%SanZhe)
                                                REDICT['SanZhe'] = SanZhe
                                                break

                                    # 三者保额
                                    if Definition[v]['#text'] == "cov_600":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "value":
                                                SanZheBE = Definition[m]['#text']
                                                if SanZheBE < 0:
                                                    SanZheBE = 0
                                                # print("三者保额的价格是:%s"%SanZheBE)
                                                REDICT['SanZheBE'] = SanZheBE
                                                break

                                    # 责任险司机
                                    if Definition[v]['#text'] == "cov_701":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                ZeRenSJ = Definition[m]['#text']
                                                ZeRenSJ = round(float(ZeRenSJ) / float(100), 2)
                                                if ZeRenSJ < 0:
                                                    ZeRenSJ = 0
                                                # print("责任险司机的价格是:%s"%ZeRenSJ)
                                                REDICT['ZeRenSJ'] = ZeRenSJ
                                                break
                                    # 责任险司机保额
                                    if Definition[v]['#text'] == "cov_701":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "value":
                                                ZeRenSJBE = Definition[m]['#text']
                                                if ZeRenSJBE < 0:
                                                    ZeRenSJBE = 0
                                                # print("责任险司机保额的价格是:%s"%ZeRenSJ)
                                                REDICT['ZeRenSJBE'] = ZeRenSJBE
                                                break

                                    # 责任险乘客
                                    if Definition[v]['#text'] == "cov_702":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                ZeRenCK = Definition[m]['#text']
                                                ZeRenCK = round(float(ZeRenCK) / float(100), 2)
                                                if ZeRenCK < 0:
                                                    ZeRenCK = 0
                                                # #print("责任险乘客的价格是:%s"%ZeRenCK)
                                                REDICT['ZeRenCK'] = ZeRenCK
                                                break

                                    # ZeRenCKBE
                                    # 责任险乘客保额
                                    if Definition[v]['#text'] == "cov_702":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "value":
                                                ZeRenCKBE = Definition[m]['#text']
                                                if ZeRenCKBE < 0:
                                                    ZeRenCKBE = 0
                                                # #print("责任险乘客的价格是:%s"%ZeRenCKBE)
                                                REDICT['ZeRenCKBE'] = ZeRenCKBE
                                                break

                                    # 盗抢险
                                    if Definition[v]['#text'] == "cov_500":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                DaoQiang = Definition[m]['#text']
                                                DaoQiang = round(float(DaoQiang) / float(100), 2)
                                                if DaoQiang < 0:
                                                    DaoQiang = 0
                                                # print("盗抢险的价格是:%s"%DaoQiang)

                                                REDICT['DaoQiang'] = DaoQiang
                                                break
                                    # 玻璃破碎险
                                    if Definition[v]['#text'] == "cov_231":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BoLiPS = Definition[m]['#text']
                                                BoLiPS = round(float(BoLiPS) / float(100), 2)
                                                # if BoLiPS < 0:
                                                #     BoLiPS = str(BoLiPS)[1:]
                                                # print("玻璃破碎险的价格是:%s"%BoLiPS)
                                                REDICT['BoLiPS'] = BoLiPS
                                                break

                                    # 划痕险
                                    if Definition[v]['#text'] == "cov_210":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                HuaHen = Definition[m]['#text']
                                                HuaHen = round(float(HuaHen) / float(100), 2)
                                                # if HuaHen < 0:
                                                #     HuaHen = str(HuaHen)[1:]
                                                # print("划痕险的价格是:%s"%HuaHen)
                                                REDICT['HuaHen'] = HuaHen
                                                break
                                    # 发动机涉水险
                                    if Definition[v]['#text'] == "cov_290":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                SheShui = Definition[m]['#text']
                                                SheShui = round(float(SheShui) / float(100), 2)
                                                # if SheShui < 0:
                                                #     SheShui = str(SheShui)[1:]
                                                # print("发动机涉水险的价格是:%s"%SheShui)
                                                REDICT['SheShui'] = SheShui
                                                break
                                    # 自燃险
                                    if Definition[v]['#text'] == "cov_310":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                ZiRan = Definition[m]['#text']
                                                ZiRan = round(float(ZiRan) / float(100), 2)
                                                # if ZiRan < 0:
                                                #     ZiRan = str(ZiRan)[1:]
                                                # print("自燃险的价格是:%s"%ZiRan)
                                                REDICT['ZiRan'] = ZiRan
                                                break

                                                # 不计免赔总计BuJiMPZJ

                                    # 不计免赔车损
                                    if Definition[v]['#text'] == "cov_911":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BUJiCS = Definition[m]['#text']
                                                BUJiCS = round(float(BUJiCS) / float(100), 2)
                                                # if BUJiCS < 0:
                                                #     BUJiCS = 0
                                                # print("不计免赔车损的价格是:%s"%BUJiCS)
                                                REDICT['BUJiCS'] = BUJiCS
                                                break
                                    # 不计免赔三者
                                    if Definition[v]['#text'] == "cov_912":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BuJiSZ = Definition[m]['#text']
                                                BuJiSZ = round(float(BuJiSZ) / float(100), 2)
                                                # if BuJiSZ < 0:
                                                #     BuJiSZ = 0
                                                # print("不计免赔三者的价格是:%s"%BuJiSZ)
                                                REDICT['BuJiSZ'] = BuJiSZ
                                                break
                                    # 不计免赔盗抢
                                    if Definition[v]['#text'] == "cov_921":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BuJiDQ = Definition[m]['#text']
                                                BuJiDQ = round(float(BuJiDQ) / float(100), 2)
                                                # if BuJiDQ < 0:
                                                #     BuJiDQ = 0
                                                # print("不计免赔盗抢的价格是:%s"%BuJiDQ)
                                                REDICT['BuJiDQ'] = BuJiDQ
                                                break
                                    # 不计划痕
                                    if Definition[v]['#text'] == "cov_922":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BUJIHH = Definition[m]['#text']
                                                BUJIHH = round(float(BUJIHH) / float(100), 2)
                                                # if BUJIHH < 0:
                                                #     BUJIHH = 0
                                                # print("不计划痕的价格是:%s"%BUJIHH)
                                                REDICT['BUJIHH'] = BUJIHH
                                                break
                                    # 不计自燃
                                    if Definition[v]['#text'] == "cov_923":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BUJIZR = Definition[m]['#text']
                                                BUJIZR = round(float(BUJIZR) / float(100), 2)
                                                # if BUJIZR < 0:
                                                #     BUJIZR = 0
                                                # print("不计划痕的价格是:%s"%BUJIZR)
                                                REDICT['BUJIZR'] = BUJIZR
                                                break
                                    # 不计涉水
                                    if Definition[v]['#text'] == "cov_924":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BUJISS = Definition[m]['#text']
                                                BUJISS = round(float(BUJISS) / float(100), 2)
                                                # if BUJISS < 0:
                                                #     BUJISS = 0
                                                # print("不计涉水的价格是:%s"%BUJISS)
                                                REDICT['BUJISS'] = BUJISS
                                                break

                                    # 不计免赔（司机）
                                    if Definition[v]['#text'] == "cov_928":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BuJiSJ = Definition[m]['#text']
                                                BuJiSJ = round(float(BuJiSJ) / float(100), 2)
                                                # if BuJiSJ < 0:
                                                #     BuJiSJ = 0
                                                # print("不计免赔（司机）的价格是:%s"%BuJiSJ)
                                                REDICT['BuJiSJ'] = BuJiSJ
                                                break
                                    # 不计免赔（乘客）
                                    if Definition[v]['#text'] == "cov_929":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BuJiCK = Definition[m]['#text']
                                                BuJiCK = round(float(BuJiCK) / float(100), 2)
                                                # if BuJiCK < 0:
                                                #     BuJiCK = 0
                                                # print("不计免赔（乘客）的价格是:%s"%BuJiCK)
                                                REDICT['BuJiCK'] = BuJiCK
                                                break

                                    # 不计免赔特约条款
                                    if Definition[v]['#text'] == "cov_900":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BuJiTY = Definition[m]['#text']
                                                BuJiTY = round(float(BuJiTY) / float(100), 2)
                                                if BuJiTY < 0:
                                                    BuJiTY = 0
                                                # print("不计免赔特约条款的价格是:%s"%BuJiTY)
                                                REDICT['BuJiTY'] = BuJiTY
                                                break

                                    # BuJiHB
                                    # 不计免赔特约条款
                                    if Definition[v]['#text'] == "cov_910":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BuJiHB = Definition[m]['#text']
                                                BuJiHB = round(float(BuJiHB) / float(100), 2)
                                                if BuJiHB < 0:
                                                    BuJiHB = 0
                                                # print("不计免赔特约条款的价格是:%s"%BuJiHB)
                                                REDICT['BuJiHB'] = BuJiHB
                                                break

                                    # BuJiCSRY
                                    # 不计免赔车上人员
                                    if Definition[v]['#text'] == "cov_930":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BuJiCSRY = Definition[m]['#text']
                                                BuJiFJBuJiCSRY = round(float(BuJiCSRY) / float(100), 2)
                                                # if BuJiCSRY < 0:
                                                #     BuJiCSRY = 0
                                                # print("不计免赔特约条款的价格是:%s"%BuJiCSRY)
                                                REDICT['BuJiCSRY'] = BuJiCSRY
                                                break

                                    # BuJiFJ
                                    # 不计免赔附加
                                    if Definition[v]['#text'] == "cov_931":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BuJiFJ = Definition[m]['#text']
                                                BuJiFJ = round(float(BuJiFJ) / float(100), 2)
                                                if BuJiFJ < 0:
                                                    BuJiFJ = 0
                                                # print("不计免赔附加的价格是:%s"%BuJiFJ)
                                                REDICT['BuJiFJ'] = BuJiFJ
                                                break


                                    # 应交总保费
                                    if Definition[v]['#text'] == "totalPremium":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                TotalPremium = Definition[m]['#text']
                                                TotalPremium = round(float(TotalPremium) / float(100), 2)
                                                # print("保费总价格是:%s"%TotalPremium)
                                                REDICT['TotalPremium'] = TotalPremium
                                                REDICT['totalPremium'] = TotalPremium
                                                break

                                                # 应交商业险保费
                                    if Definition[v]['#text'] == "bizTotalPremium":
                                        for m in range(len(Definition)):
                                            if Definition[m]['@name'] == "premium":
                                                BizPremium = Definition[m]['#text']
                                                BizPremium = round(float(BizPremium) / float(100), 2)
                                                # print("保费总价格是:%s"%TotalPremium)
                                                REDICT['BizPremium'] = BizPremium
                                                REDICT['bizPremium'] = BizPremium
                                                break
                return REDICT
        except:
            return REDICT
    def ReContent(self,msg,SessionID):
        SendVal = (
                SessionID,
                self.AddTime,
                msg
        )
        # 打开文件
        File = WEB_ROOT + "/bxxml/ansheng/" + str(400) + ".xml"
        # 读文件
        FileOpen = open(File).read()

        FileOpen = FileOpen.replace("\n", "")
        # 替换空格
        result, number = re.subn(">(\s{1,})<", "><", FileOpen)
        result = result % SendVal
        InputsList = "<Response></Response>"
        Mysign = self.sign.rsa_sign(data=InputsList)
        result = result.replace("<!--[SIGN]-->", str(Mysign))
        return result
    # 发送通用方法
    def Send(self, Interface, SendVal, Is115=False):

        """
        向安盛服务器发送数据，并接收返回xml，并转化为字典

        Args:
            Interface (str): 接口代号，对应bxxml/ansheng/{$Interface}.xml
            SendVal (tuple):  需要向保险服务器提交的数据

        Returns:
          dict: 返回结果字典

        """
        # 打开文件
        File = WEB_ROOT + "/bxxml/ansheng/" + str(Interface) + ".xml"
        # 读文件
        FileOpen = open(File).read()

        FileOpen = FileOpen.replace("\n", "")
        # 替换空格
        result, number = re.subn(">(\s{1,})<", "><", FileOpen)
        result = result % SendVal
        if Is115:
            InputsList = "<Request><Order>%s</InputsList></Request>" % (
                re.findall("<Order>(.*?)</InputsList>", result)[0])
        else:
            InputsList = "<Request><InputsList>%s</InputsList></Request>" % (
                re.findall("<InputsList>(.*?)</InputsList>", result)[0])
        Mysign = self.sign.rsa_sign(data=InputsList)

        result = result.replace("<!--[SIGN]-->", str(Mysign))
        self.EchoLog("----%s----接口发送到服务器的xml" % str(Interface), result)
        try:
            # http://pre-net.tpis.tpaic.com:11580/ecws/mobPhonePayDispatcherController.do
            webservice = httplib.HTTP("ws.95550.cn:9999")
            # webservice = httplib.HTTP("dev.tpis.tpaic.com:20680")
            webservice.putrequest("POST", "/ecws/mobPhonePayDispatcherController.do")
            # webservice.putheader("Host", "dev.tpis.tpaic.com:20680")
            webservice.putheader("Host", "ws.95550.cn:9999")
            webservice.putheader("Connection", "close")
            webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
            webservice.putheader("Content-length", "%d" % len(result))
            webservice.endheaders()
            webservice.send(result)
            # webservice.getreply()
            statuscode, statusmessage, header = webservice.getreply()
            #print "Response: ", statuscode, statusmessage
            #print "headers: ", header
            ReXML = webservice.getfile().read()

            self.EchoLog("----%s----接口服务器返回的xml"% str(Interface), ReXML)
        except:
           ReXML='''<?xml version="1.0" encoding="GBK" standalone="yes"?><PackageList><Package><Header><Version>2</Version><RequestType>100</RequestType><InsureType>100</InsureType><SessionId></SessionId><SendTime></SendTime><Status>100</Status><ErrorMessage>网络异常！请稍后再试</ErrorMessage><SellerId>2015061901</SellerId></Header></Package></PackageList>'''
        return str(ReXML)

    def EchoLog(self, msg="", content="", status=1):
        if status == 0:
            print("\n")
            print("++++++++++++++++++++++++++++<-[start %s start]->++++++++++++++++++++++++" % msg)
            print(content)
            print("++++++++++++++++++++++++++++<-[end %s end]->++++++++++++++++++++++++++++" % msg)
        else:
            pass


class Sign(object):
    gm = "MIGeMA0GCSqGSIb3DQEBAQUAA4GMADCBiAKBgFFijWSnyWvAIvX6eD2nSUSki0HgPEGCujkVRqWaob6RB3W4FyqD2mgzOP10sEZBRJl1uTEl24L6Z5TlLuvr1nGReZgV347W0lWvmTn3N4fihChozGwys05nAUL4nweFGuAvBmrs1BnZbXUo+E7qn5THINVB7NUzsElFaJ2VpgQ9AgMBAAE="
    sm = "MIICdAIBADANBgkqhkiG9w0BAQEFAASCAl4wggJaAgEAAoGAUWKNZKfJa8Ai9fp4PadJRKSLQeA8QYK6ORVGpZqhvpEHdbgXKoPaaDM4/XSwRkFEmXW5MSXbgvpnlOUu6+vWcZF5mBXfjtbSVa+ZOfc3h+KEKGjMbDKzTmcBQvifB4Ua4C8GauzUGdltdSj4TuqflMcg1UHs1TOwSUVonZWmBD0CAwEAAQKBgAVUxFhUmWAijOe6CYhYXfdOJAUjsC7GZnZ4y1DryS6Xh3qRnYreaj8rI8+OhkGD4v9+c6whg7iXuJNLVACGSVzCNOPVZky+yKoCJSennQicU4V8HDb0LQBHfrr1DRkbutRkmpeurN7iSGc4CoJKyUruCDNI77jjDwZI6E0WlYLNAkEAlFfvBLc9AOAcY65Tgy8wbKlXZhO9aDLiDIYbRvKpeGyZ570kaMadKy1m1xHD//RKzcRneLdHuVhEjcfgLdwqiwJBAIxysqaHEPN/zW8H8/Gi1a4FKpmMbpqPbGIsS202Z+YphsY+WII7EneM84TIaJxWY9XAxUIF6tCi9I+juMLPjVcCQCv3ZAAhzxLTWZaxtE7NTaznA+BdOWYIrrbHiI4endvzVCo7BO+I7kw9yJ01xsG1xfX2oDRHHhrw7mCXPPpapsECQGxSYjtR3N8Q6O8DoT/yqP9oeKyoxP1sNNma9CmtVoEL8iigGT+IM/wEuCTnNNevQZyw6vK7AZoctKa8TVnjHk0CQHvrL7NiVMEZslghODofveFPaLBXBfcfPb5UYe3BEnje9jrqa5vMfh+8XwxvJSeiLRgJhTB+6mB6Rvy9BE7mWt0="
    # sm1 = "MIICdAIBADANBgkqhkiG9w0BAQEFAASCAl4wggJaAgEAAoGAUWKNZKfJa8Ai9fp4PadJRKSLQeA8QYK6ORVGpZqhvpEHdbgXKoPaaDM4/XSwRkFEmXW5MSXbgvpnlOUu6+vWcZF5mBXfjtbSVa+ZOfc3h+KEKGjMbDKzTmcBQvifB4Ua4C8GauzUGdltdSj4TuqflMcg1UHs1TOwSUVonZWmBD0CAwEAAQKBgAVUxFhUmWAijOe6CYhYXfdOJAUjsC7GZnZ4y1DryS6Xh3qRnYreaj8rI8+OhkGD4v9+c6whg7iXuJNLVACGSVzCNOPVZky+yKoCJSennQicU4V8HDb0LQBHfrr1DRkbutRkmpeurN7iSGc4CoJKyUruCDNI77jjDwZI6E0WlYLNAkEAlFfvBLc9AOAcY65Tgy8wbKlXZhO9aDLiDIYbRvKpeGyZ570kaMadKy1m1xHD//RKzcRneLdHuVhEjcfgLdwqiwJBAIxysqaHEPN/zW8H8/Gi1a4FKpmMbpqPbGIsS202Z+YphsY+WII7EneM84TIaJxWY9XAxUIF6tCi9I+juMLPjVcCQCv3ZAAhzxLTWZaxtE7NTaznA+BdOWYIrrbHiI4endvzVCo7BO+I7kw9yJ01xsG1xfX2oDRHHhrw7mCXPPpapsECQGxSYjtR3N8Q6O8DoT/yqP9oeKyoxP1sNNma9CmtVoEL8iigGT+IM/wEuCTnNNevQZyw6vK7AZoctKa8TVnjHk0CQHvrL7NiVMEZslghODofveFPaLBXBfcfPb5UYe3BEnje9jrqa5vMfh+8XwxvJSeiLRgJhTB+6mB6Rvy9BE7mWt0="
    def rsa_sign(self, data):
        pri_key = RSA.importKey(base64.b64decode(self.sm))
        pkcs = PKCS1_v1_5.new(pri_key)
        digest = MD5.new(data)
        return base64.b64encode(pkcs.sign(digest))

    def rsa_verify(self, data, sign):
        pubkey = RSA.importKey(base64.b64decode(self.gm))
        digest = MD5.new(data)
        pkcs = MD5.new(pubkey)
        return pkcs.verify(digest, base64.b64decode(sign))
