# -*- coding:utf-8 -*-
from django.shortcuts import *
from LYZ.common import makeNew
from common import *
import datetime, random, urllib, urllib2, time
from LYZ.settings import *
from suds.client import *
import sys, xmltodict
import json
import re
import dicttoxml
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from xml.etree import ElementTree

reload(sys)
sys.setdefaultencoding('utf-8')


class ZhongHuaAction(object):
    # 测试地址
    # URL = "http://220.171.28.152:9080/nsp/services/NetSalePlatform?wsdl"
    # 生产支付地址
    URL = "http://e.cic.cn/nsp/services/NetSalePlatform?wsdl"
    WAP_URL = "http://e.cic.cn/nsp/payment/wapPayment.do?orderNo="
    # 测试支付地址
    # PAY_URL = "http://220.171.28.152:9080/nsp/payment/payment.do?orderNo="
    PAY_URL = "http://e.cic.cn/nsp/payment/payment.do?orderNo="
    # 用户名测试
    # USER_NAME = "ECUser"
    # 生产
    USER_NAME = "cicns_KLB"
    # 密码测试
    # USER_PSW = "EC100"
    # 生产
    USER_PSW = "cicnsKLB2015"
    # 渠道代码
    CHANNELCODE = "001501"

    def __init__(self, citycode="", licenseNo="", ownerName="", vin="", engineNo="", user_id=""):
        self.citycode = citycode
        self.licenseNo = licenseNo
        self.ownerName = ownerName
        self.vin = vin
        self.engineNo = engineNo
        self.user_id = user_id
        self.citycode = citycode
        self.licenseNo = licenseNo

        self.firstRegisterDate = str((datetime.date.today() + datetime.timedelta(days=-365 * 2)).strftime("%Y-%m-%d"))
        # 商业保险起期
        self.bizBeginDate = str((datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"))
        # 交强险起期
        self.forceBeginDate = str((datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"))
        self.SessionID = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + str(
            random.randint(100000000000000000, 999999999999999999))
        self.AddTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 初始化soap连接
        self.client = Client(self.URL, location=self.URL, cache=None)
        # 生成用户身份证
        self.ownerid = makeNew()

    # 1030基本信息录入接口
    def Get_1030(self):
        SendVal = (
            self.citycode,
            self.licenseNo,
            '0'  # 是否为新车
        )
        # 判断值是否为空
        for i in SendVal:
            if i == "" or i == None:
                return False
        Re1030 = self.Send(Interface=1030, SendVal=SendVal)
        return Re1030

    def Get_1031(self):
        """
        车辆车型查询接口

        Args:
            pam (list): 传入参数
            SendVal (tuple):  需要向保险服务器提交的数据

        Returns:
          str: 返回结果

        """
        if self.vin <> "" or self.vin <> None:
            GetCar = GetCarInfo(Value=self.vin)
            YGinfo = GetCar.GetInfo_YG()
            try:
                vehicleModelName = (YGinfo == False) and "" or YGinfo['vehicleFgwCode']
            except:
                vehicleModelName = (YGinfo == False) and "" or YGinfo['vehiclefgwcode']

        else:
            vehicleModelName = ""
        try:
            GetRE = GetregisterDate()
            self.firstRegisterDateNEW = GetRE.GetregisterDate(licenseno=self.licenseNo,vin=self.vin,engineNo=self.engineNo,CityCode=self.citycode)
            # print(self.firstRegisterDateNEW)
        except:
            self.firstRegisterDateNEW=self.firstRegisterDate
        #     print(111)
        if self.citycode == '440300':
            RT = {}
            RELIST = {"error":"1","msg":"该城市不可投保"}
            CarInfo = RELIST
            ERR = "1"
            JinBaoMsg = ""
            ORDER = ""
            self.EchoLog("1031出错了", "该城市不可投保")
            return ERR, CarInfo, RT
        SendVal = (
            self.citycode,  # 地区编码
            self.licenseNo,  # 车牌号码
            self.ownerName,  # 行驶证车主
            self.engineNo,  # 发动机号
            self.vin,  # 车架号
            vehicleModelName,  # 品牌型号
            self.firstRegisterDateNEW,  # 车辆初始登记日期
        )

        RT = self.Send(Interface=1031, SendVal=SendVal)
        RTDICT = xmltodict.parse(RT, encoding="utf-8")
        # 获取是否有出错信息
        RESULTCODE = RTDICT['INSUREQRET']['MAIN']['RESULTCODE']
        # 获取错误提示
        ERROR_INFO = RTDICT['INSUREQRET']['MAIN']['ERR_INFO']
        # 判断是否查询车型库出错
        ERR = (RESULTCODE <> "0000") and 1 or 0
        if ERR:
            # ERROR_INFO = "对不起！您的爱车暂时不支持投保！"
            RELIST = {"error":"1","msg":ERROR_INFO}
            CarInfo = RELIST
            self.EchoLog("1031出错了", ERROR_INFO)

            return ERR, CarInfo, RT
        else:
            # CarArrAll = RTDICT['INSUREQRET']['VHLMODEL_LIST']
            CarInfoArr = GetCarInfo(Value=self.vin)
            ZHInfo = CarInfoArr.GetDBSelect(type="sinosig")
            K = ZHInfo['key']
            try:
                for i in range(len(RTDICT['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'])):
                    NEWDICT = RTDICT['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][i]
                    CarArrAll = ''
                    if K == NEWDICT['C_VEHICLE_CODE']:
                        CarArrAll = RTDICT['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][i]
                        CarInfo = CarArrAll

                if CarArrAll=='':
                    CarArrAll = RTDICT['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]
                    CarInfo = CarArrAll
            except:
                if K == RTDICT['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['C_VEHICLE_CODE']:
                    CarArrAll = RTDICT['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']
                    CarInfo = CarArrAll
                else:
                    CarArrAll = RTDICT['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']
                    CarInfo = CarArrAll
            # try:
            #     CarInfo = CarArrAll['VHLMODEL'][0]
            # except:
            #
            #     CarInfo = CarArrAll['VHLMODEL']
            if "C_MARKET_TIMESTAMP" in CarInfo:
                pass
            else:
                CarInfo['C_MARKET_TIMESTAMP'] = str(
                    (datetime.date.today() + datetime.timedelta(days=-365 * 3)).strftime("%Y%m"))

        # 返回信息
        '''
        ERR: 是否有错  1为有错，0为没错
        CarInfo :一条车辆信息(dict)
        RT: 保险公司返回的xml全部信息
        '''
        return ERR, CarInfo, RT

    # 车险承保方案信息接口
    def Get_1032(self,bizBeginDate=''):
        print(bizBeginDate)
        if bizBeginDate <> '':
            bizBeginDate = bizBeginDate
        else:
            bizBeginDate = self.bizBeginDate
        ERR, CarInfo, RT = self.Get_1031()
        if ERR:
            bizBeginDate = ''
            firstRegisterDate=''
            RELIST = CarInfo
            RE = False
            ORDER = False
            JinBaoMsg = False
            return ERR, ORDER, RELIST, RE, JinBaoMsg,bizBeginDate,firstRegisterDate
        JinBaoMsg = {"HUAHEN": None, "SHESHUI": None, "ZIRAN": None}

        SendVal = (
            self.citycode,  # 地区编码
            bizBeginDate,  # 商业险保单起期
            time.strftime('%Y-%m-%d'),  # 录单日期
            '',  # 服务专员
            '',  # 机构代码
            '',  # 业务来源
            '',  # 服务代码
            self.licenseNo,  # 车牌号码
            "0",  # 是否新车
            self.ownerName,  # 车主姓名
            '',  #
            self.engineNo,  # 发动机号
            self.vin,  # 车架号
            self.firstRegisterDateNEW,  # 车辆初始登记日期
            CarInfo['C_VEHICLE_CODE'],  # 车型代码（车型编码）
            CarInfo['C_MODEL_DESC'],  # 车型描述
            CarInfo['C_VEHICLE_BRAND'],  # 品牌名称
            CarInfo['C_VEHICLE_NAME'],  # 车型名称
            CarInfo['C_VEHICLE_FAMILY'],  # 车系名称（车型库车系）
            CarInfo['C_IMPORT_FLAG'],  # 车型种类 (国产/进口/合资)
            CarInfo['N_LIMIT_LOAD_PERSON'],  # 核定载客人数
            CarInfo['C_WHOLE_WEIGHT'],  # 整备质量
            CarInfo['N_VEHICLE_TONNAGE'],  # 载重量
            CarInfo['C_EXT_MSR'],  # 排气量
            CarInfo['C_MARKET_TIMESTAMP'],  # 上市年份
            CarInfo['N_VEHICLE_PRICE']  # 新车购置价
        )
        RE = self.Send(Interface=1032, SendVal=SendVal)
        REDICT = xmltodict.parse(RE, encoding="utf-8")
        # 获取是否有出错信息
        BASE = REDICT['INSUREQRET']['BASE']
        RESULTCODE = REDICT['INSUREQRET']['MAIN']['RESULTCODE']
        # 获取错误提示
        ERROR_INFO = REDICT['INSUREQRET']['MAIN']['ERR_INFO']
        # 判断是否查询车型库出错
        ERR = (RESULTCODE <> "0000") and 1 or 0
        try:
            bizBeginDate = BASE['C_LAST_BUS_END']
            firstRegisterDate = BASE['C_LAST_TRA_END']
        except:
            bizBeginDate = ''
            firstRegisterDate=''
        if ERR:
            if BASE <> None:
                if BASE.has_key('C_LAST_BUS_END'):
                    ERR, ORDER, RELIST, RE, JinBaoMsg,bizBeginDate,firstRegisterDate=self.Get_1032(bizBeginDate=BASE['C_LAST_BUS_END'])
                    return ERR, ORDER, RELIST, RE, JinBaoMsg,bizBeginDate,firstRegisterDate
                else:
                    RELIST = {"error":"1","msg":ERROR_INFO}
                    self.EchoLog("1032出错了", ERROR_INFO)
                    ORDER = False
                    return ERR, ORDER, RELIST, RE, JinBaoMsg,bizBeginDate,firstRegisterDate
            else:
                RELIST = {"error": "1", "msg": ERROR_INFO}
                self.EchoLog("1032出错了", ERROR_INFO)
                ORDER = False
                return ERR, ORDER, RELIST, RE, JinBaoMsg,bizBeginDate,firstRegisterDate
        else:
            try:
                RELIST = REDICT['INSUREQRET']['KIND_LIST']['KIND']
                ORDER = REDICT['INSUREQRET']['BASE']['C_ORDER_NO']
                for i in range(len(RELIST)):
                    try:
                        if RELIST[i]['C_KIND_CDE'] == "030025":
                            JinBaoMsg['HUAHEN'] = None
                            break
                        else:
                            JinBaoMsg['HUAHEN'] = "禁保"
                    except:
                        JinBaoMsg['HUAHEN'] = "禁保"
                        break
                for i in range(len(RELIST)):
                    try:
                        if RELIST[i]['C_KIND_CDE'] == "030065":
                            JinBaoMsg['SHESHUI'] = None
                            break
                        else:
                            JinBaoMsg['SHESHUI'] = "禁保"
                    except:
                        JinBaoMsg['SHESHUI'] = "禁保"
                        break
                for i in range(len(RELIST)):
                    try:
                        if RELIST[i]['C_KIND_CDE'] == "030012":
                            JinBaoMsg['ZIRAN'] = None
                            break
                        else:
                            JinBaoMsg['ZIRAN'] = "禁保"
                    except:
                        JinBaoMsg['ZIRAN'] = "禁保"
                        break
            except:
                RELIST = False
                ORDER = False
        return ERR, ORDER, RELIST, RE, JinBaoMsg,bizBeginDate,firstRegisterDate

    # 车辆报价接口
    '''

    CHESHUN='',  # 机动车损失险
    SANZHE='1',  # 第三者责任险
    SHIJI='',    # 人员责任（司机）
    CHENGKE='',  # 人员险（乘客）
    DAOQIANG='', # 盗抢
    ZIRAN='',    # 自燃险
    BOLI='',     # 玻璃破碎险
    DAOQIANG_BJ='',  # 不计盗抢
    CHESHUN_BJ='',   # 不计车损
    SANZHE_BJ='',    # 不计三者
    SHIJI_BJ='',     # 不计司机
    CHENGKE_BJ='',   # 不计乘客
    BAOE_SZ='50000', # 三者险保额
    BAOE_CK='',      # 责任险乘客保额
    BAOE_SJ='',      # 责任险司机保额
    HUAHEN='',       # 划痕险
    SHESHUI='',      # 涉水险
    FUJIA_BJ =''     # 附加不计免赔
    '''

    def Get_1033(self, CHESHUN='0', SANZHE='50000', SHIJI='0', CHENGKE='0', DAOQIANG='0', ZIRAN='0', BOLI='0',
                 DAOQIANG_BJ='0', CHESHUN_BJ='0', SANZHE_BJ='0', SHIJI_BJ='0', CHENGKE_BJ='0', HUAHEN='0', SHESHUI='0',
                 FUJIA_BJ='0', JIAOQIANG='0',firstRegisterDate='',bizBeginDate=''):
        DictIn = {
        "CHESHUN": CHESHUN,
        "SANZHE":  SANZHE,
        "DAOQIANG":  DAOQIANG,
        'SHIJI':  SHIJI,
        "CHENGKE":  CHENGKE,
        "BOLI":  BOLI,
        "HUAHEN":  HUAHEN,
        "ZIRAN":  ZIRAN,
        "SHESHUI":  SHESHUI,
        "CHESHUN_BJ":  CHESHUN_BJ,
        "SANZHE_BJ":  SANZHE_BJ,
        "DAOQIANG_BJ":  DAOQIANG_BJ,
        "SHIJI_BJ":  SHIJI_BJ,
        "CHENGKE_BJ":  CHENGKE_BJ,
        "FUJIA_BJ":  FUJIA_BJ,
        "JIAOQIANG":  JIAOQIANG,
        "bizBeginDate":bizBeginDate,
        }
        try:
            if DictIn['bizBeginDate'] == "" or DictIn['bizBeginDate'] == None:
                bizBeginDateNEW = self.bizBeginDate
            else:
                bizBeginDateNEW = DictIn['bizBeginDate']
        except:
            bizBeginDateNEW = self.bizBeginDate
        ERR, ORDER, RELIST, RE, JinBaoMsg,bizBeginDate,firstRegisterDate = self.Get_1032(bizBeginDate=bizBeginDateNEW)
        if ERR:
            ORDER = False
            REDICT = RELIST
            RE = False
            return ERR, ORDER, REDICT, RE,JinBaoMsg

        if firstRegisterDate == '':
            firstRegisterDate = (JIAOQIANG == '0') and '' or bizBeginDateNEW
        else:
            firstRegisterDate = firstRegisterDate
        if bizBeginDate == '':
            bizBeginDate = bizBeginDateNEW
        else:
            bizBeginDate = bizBeginDate
        if self.citycode == '120100' or self.citycode == '830100':
            TAX_PAYERNAME = self.ownerName
            TAX_PAYERNO = self.ownerid
            TAX_AUTHCDE = '10100'
        else:
            TAX_PAYERNAME = ''
            TAX_PAYERNO = ''
            TAX_AUTHCDE = ''
        if JinBaoMsg['HUAHEN'] == None:
            pass
        else:
            HUAHEN = '0'
        if JinBaoMsg['SHESHUI'] == None:
            pass
        else:
            SHESHUI = '0'
        if JinBaoMsg['ZIRAN'] == None:
            pass
        else:
            ZIRAN = '0'
        try:
            if int(SANZHE) > 1:
                BAOE_SZ = SANZHE
                SANZHE = "1"
            else:
                SANZHE = "0"
                BAOE_CK = ''
                BAOE_SJ = ''
                BAOE_SZ = ""
                SANZHE_BJ = "0"
                CHESHUN_BJ = "0"
                SHIJI_BJ = "0"
        except:
            BAOE_CK = ''
            BAOE_SJ = ''
            BAOE_SZ = ""
            SANZHE_BJ = "0"
            SANZHE = "0"
            CHESHUN_BJ = "0"
            SHIJI_BJ = "0"
        try:
            if int(SHIJI) > 1:
                BAOE_SJ = SHIJI
                SHIJI = "1"
            else:
                BAOE_SJ = ''
                SHIJI = '0'
                SHIJI_BJ = '0'
        except:
            BAOE_SJ = ''
            SHIJI = '0'
            SHIJI_BJ = '0'
        try:
            if int(CHENGKE) > 1:
                BAOE_CK = CHENGKE
                CHENGKE = '1'
            else:
                BAOE_CK = ''
                CHENGKE = '0'
                CHENGKE_BJ = '0'
        except:
            BAOE_CK = ''
            CHENGKE = '0'
            CHENGKE_BJ = '0'
        try:
            if int(HUAHEN) > 1:
                BAOE_HUAHEN = HUAHEN
                HUAHEN = '1'
            else:
                BAOE_HUAHEN = ''
                HUAHEN = '0'
        except:
            BAOE_HUAHEN = ''
            HUAHEN = '0'
        HUAHEN = (HUAHEN == '0') and -1 or HUAHEN
        SHESHUI = (SHESHUI == '0') and -1 or SHESHUI
        CHESHUN = (CHESHUN == '0') and -1 or CHESHUN
        SANZHE = (SANZHE == '0') and -1 or SANZHE
        SHIJI = (SHIJI == '0') and -1 or SHIJI
        CHENGKE = (CHENGKE == '0') and -1 or CHENGKE
        DAOQIANG = (DAOQIANG == '0') and -1 or DAOQIANG
        BAOE_ZIRAN = ""
        BAOE_CHESUN = ""
        BAOE_DABQIANG = ""

        for i in range(len(RELIST)):
            # 获取车损险价格
            if RELIST[i]['C_KIND_CDE'] == "030006":
                JGSTR = RELIST[i]['N_DEFAULT_AMT']
                BAOE_CHESUN = (CHESHUN == '1') and JGSTR or ''
            # 获取盗抢险价格
            if RELIST[i]['C_KIND_CDE'] == "030059":
                JGSTR = RELIST[i]['N_DEFAULT_AMT']
                BAOE_DABQIANG = (DAOQIANG == '1') and JGSTR or ''
            # 获自然价格
            if RELIST[i]['C_KIND_CDE'] == "030012":
                JGSTR = RELIST[i]['N_DEFAULT_AMT']
                BAOE_ZIRAN = (ZIRAN == '1') and JGSTR or ''
            # 获乘客取座位数
            if RELIST[i]['C_KIND_CDE'] == '030072':
                CHENGKE_SEAT_NUM = RELIST[i]['N_SEAT_NUM']
        Interface = (JIAOQIANG == '0') and 1033 or 1034
        businesscode = (JIAOQIANG == '0') and '11' or '12'

        if JIAOQIANG == '0':
            TAX_PAYERNAME = ''
            TAX_PAYERNO = ''
            TAX_AUTHCDE = ''
        ZIRAN = (ZIRAN == '0') and -1 or ZIRAN
        BOLI = (BOLI == '0') and '-1' or BOLI
        BOLI = (BOLI == '1') and '0' or BOLI
        BOLI = (BOLI == '2') and '1' or BOLI
        DAOQIANG_BJ = (DAOQIANG_BJ == '0') and -1 or DAOQIANG_BJ
        CHESHUN_BJ = (CHESHUN_BJ == '0') and -1 or CHESHUN_BJ
        SANZHE_BJ = (SANZHE_BJ == '0') and -1 or SANZHE_BJ
        SHIJI_BJ = (SHIJI_BJ == '0') and -1 or SHIJI_BJ
        CHENGKE_BJ = (CHENGKE_BJ == '0') and -1 or CHENGKE_BJ
        BAOE_SHESHUI = (SHESHUI == '1') and '50000' or ''
        BAOE_BJ_CHESUN = (CHESHUN_BJ == '1') and '0' or ''
        BAOE_BJ_CHENGKE = (CHENGKE_BJ == '1') and '0' or ''
        BAOE_BJ_SIJI = (SHIJI_BJ == '1') and '0' or ''
        BAOE_BJ_DAOQIANG = (DAOQIANG_BJ == '1') and '0' or ''
        BAOE_BJ_SANZHE = (SANZHE_BJ == '1') and '0' or ''
        BAOE_BOLI = (BOLI == '1') and '1' or '0'
        if BOLI == '-1':
            BAOE_BOLI = ''
        BAOE_CK = (CHENGKE == '1') and BAOE_CK or ''  # 乘客保额
        BAOE_SZ = (SANZHE == '1') and BAOE_SZ or ''  # 第三者责任险保额
        CODE_CHESHUN = (CHESHUN == '1') and '030006' or ''  # 车损险
        CODE_ZERENSANZHE = (SANZHE == '1') and '030018' or ''  # 三者险
        CODE_DAOQIANG = (DAOQIANG == '1') and '030059' or ''  # 盗抢险
        CODE_ZERENSIJI = (SHIJI == '1') and '030070' or ''  # 责任险（司机）
        CODE_ZERENCK = (CHENGKE == '1') and '030072' or ''  # 责任险（乘客）
        CODE_BOLI = (BOLI == '1' or BOLI == '0') and '030004' or ''  # 玻璃单独破碎
        CODE_ZIRAN = (ZIRAN == '1') and '030012' or ''  # 自燃险
        CODE_SHESHUI = (SHESHUI == '1') and '030065' or ''  # 发动机涉水险
        CODE_HUAHEN = (HUAHEN == '1') and '030025' or ''  # 划痕险
        CODE_BJ_CHESHUN = (CHESHUN_BJ == '1') and '031901' or ''  # 不计车损
        CODE_BJ_SHANZHE = (SANZHE_BJ == '1') and '031902' or ''  # 不计三者
        CODE_BJ_DAOQIANG = (DAOQIANG_BJ == '1') and '030106' or ''  # 不计盗抢
        CODE_BJ_SIJI = (SHIJI_BJ == '1') and '033531' or ''  # 不计司机
        CODE_BJ_CHENGKE = (CHENGKE_BJ == '1') and '033532' or ''  # 不计乘客

        SendVal = (
            self.citycode,  # 地区编码
            ORDER,  # 订单号
            bizBeginDate,  # 商业保单起期
            '',  # 商业保单止期
            firstRegisterDate,  # 交强险起期
            '',  # 交强险止期
            '1',  # 是否约省
            '1',
            CODE_CHESHUN,  # 机动车损失险
            # CHESHUN,  # 是否投保
            BAOE_CHESUN,
            '2',
            CODE_ZERENCK,  # 责任险（乘客）
            BAOE_CK,  # 保额/限额(元)
            CHENGKE_SEAT_NUM,
            '3',
            CODE_ZERENSIJI,  # 责任险（司机）
            BAOE_SJ,  # 保额/限额(元)
            '4',
            CODE_ZERENSANZHE,  # 第三者责任险
            BAOE_SZ,  # 保额
            '5',
            CODE_BJ_SHANZHE,  # 不计三者险
            # SANZHE_BJ,  # 是否投保
            BAOE_BJ_SANZHE,  #
            '6',
            CODE_DAOQIANG,  # 机动车盗抢险
            # DAOQIANG,
            BAOE_DABQIANG,  # 投保限额
            '7',
            CODE_BJ_DAOQIANG,  # 不计盗抢
            # DAOQIANG_BJ,
            BAOE_BJ_DAOQIANG,
            '8',
            CODE_BJ_SIJI,  # 不计司机
            # SHIJI_BJ,
            BAOE_BJ_SIJI,
            '9',
            CODE_BJ_CHENGKE,  # 不计乘客
            # CHENGKE_BJ,
            BAOE_BJ_CHENGKE,
            '10',
            CODE_BOLI,  # 玻璃单独破碎险
            # BOLI,
            BAOE_BOLI,  # 玻璃保额
            '11',
            CODE_ZIRAN,  # 自然损失险
            # ZIRAN,
            BAOE_ZIRAN,
            '12',
            CODE_BJ_CHESHUN,  # 不计车损
            # CHESHUN_BJ,
            BAOE_BJ_CHESUN,
            '13',
            CODE_SHESHUI,  # 涉水险
            # SHESHUI,
            BAOE_SHESHUI,
            '14',
            CODE_HUAHEN,  # 划痕险
            # HUAHEN,
            BAOE_HUAHEN,
            '',  # 车主证件号码
            '',  # 购车发票开具日期
            '',  # 车辆来历凭证种类
            '',  # 车辆来历凭证编号
            '',  # 开具车辆来历凭证所载日期
            TAX_PAYERNAME,
            TAX_PAYERNO,
            TAX_AUTHCDE,
        )
        RE = self.Send(Interface=Interface, SendVal=SendVal)
        self.EchoLog(msg='1033', content=RE)
        REDICT_F = xmltodict.parse(RE, encoding="utf-8")
        RESULTCODE = REDICT_F['INSUREQRET']['MAIN']['RESULTCODE']
        # 获取错误提示
        ERROR_INFO = REDICT_F['INSUREQRET']['MAIN']['ERR_INFO']
        # 判断是否查询车型库出错
        ERR = (RESULTCODE <> "0000") and 1 or 0

        if ERR:
             ERROR_INFO = ''.join(re.findall(r'(?<=\[)[\S\s]*(?=\])',ERROR_INFO))
             ERROR_INFO = ''.join(re.findall(r'[0-9]',ERROR_INFO))
             if ERROR_INFO == '' or ERROR_INFO == None:
                 REDICT = {"error": "1", "msg": REDICT_F['INSUREQRET']['MAIN']['ERR_INFO']}
                 self.EchoLog("1033出错了", REDICT_F['INSUREQRET']['MAIN']['ERR_INFO'])
                 ORDER = False
                 return ERR, ORDER, REDICT, RE, JinBaoMsg
             else:
                 T = str(int(ERROR_INFO[8:]) + 1)
                 T = T[:4] + "-" + T[4:]
                 T = T[:7] + "-" + T[7:] + " 00:00:00"
                 DictIn['firstRegisterDate'] = T
                 DictIn['bizBeginDate'] = T
                 ERR, ORDER, REDICT, RE, JinBaoMsg = self.Get_1033(**DictIn)
                 return ERR, ORDER, REDICT, RE, JinBaoMsg
        KIND_LIST = REDICT_F['INSUREQRET']['KIND_LIST']['KIND']
        REDICT = {
            "Session_ID": REDICT_F['INSUREQRET']['MAIN']['SERIALDECIMAL'],
            "ORDER_ID": ORDER,
            "TotalPremium": "0",
            "BizPremium": REDICT_F['INSUREQRET']['BASE']['N_REAL_PRM'],
            "bizPremium": REDICT_F['INSUREQRET']['BASE']['N_REAL_PRM'],
            "InsuranceGift": "暂无礼品",
            "klbGift": "暂无礼品",
            "VehicleLoss": "0",  # 车损
            "ZeRenCK": "0",  # 责任险乘客
            "ZeRenSJ": "0",  # 责任险司机
            "SanZhe": "0",  # 三者
            "BuJiSZ": "0",  # 不计免赔三者
            "DaoQiang": "0",  # 盗抢险
            "BuJiDQ": "0",  # 不计盗抢
            "BuJiSJ": "0",  # 不计司机
            "BuJiCK": "0",  # 不计乘客
            "BUJiCS": "0",  # 不计车损
            "BUJIZR": "0",  # 不计自燃
            "BoLiPS": "0",  # 玻璃破碎
            "ZiRan": "0",  # 自然
            "totalPremium": "0",
            "BuJiMPZJ": "0",
            "ForePremium": "0",  # 交强险总计
            "SheShui": "0",
            "HuaHen": "0",
            "forcePremium": "0",
            "forcePre": "0",
            "VehTaxPremium": "0",
        }
        try:
            REDICT['ForePremium'] = round(float(REDICT_F['INSUREQRET']['BASE']['N_TRAFF_REAL_PRM']) + float(
                REDICT_F['INSUREQRET']['BASE']['N_TAX_PRM']), 2)
            REDICT['forcePremium'] = round(float(REDICT_F['INSUREQRET']['BASE']['N_TRAFF_REAL_PRM']) + float(
                REDICT_F['INSUREQRET']['BASE']['N_TAX_PRM']), 2)
            REDICT['forcePre'] = REDICT_F['INSUREQRET']['BASE']['N_TRAFF_REAL_PRM']
            REDICT['VehTaxPremium'] = REDICT_F['INSUREQRET']['BASE']['N_TAX_PRM']
        except:
            pass
        try:
            REDICT['TotalPremium'] = round(float(REDICT_F['INSUREQRET']['BASE']['N_REAL_PRM']) + float(
                REDICT_F['INSUREQRET']['BASE']['N_TRAFF_REAL_PRM']) + float(
                REDICT_F['INSUREQRET']['BASE']['N_TAX_PRM']), 2)
            REDICT['totalPremium'] = round(float(REDICT_F['INSUREQRET']['BASE']['N_REAL_PRM']) + float(
                REDICT_F['INSUREQRET']['BASE']['N_TRAFF_REAL_PRM']) + float(
                REDICT_F['INSUREQRET']['BASE']['N_TAX_PRM']), 2)
        except:
            REDICT['TotalPremium'] = REDICT_F['INSUREQRET']['BASE']['N_REAL_PRM']
            REDICT['totalPremium'] = REDICT_F['INSUREQRET']['BASE']['N_REAL_PRM']
        if JinBaoMsg['HUAHEN'] == None:
            pass
        else:
            REDICT["HuaHen"] = "不支持"
        if JinBaoMsg['SHESHUI'] == None:
            pass
        else:
            REDICT["SheShui"] = "不支持"
        if JinBaoMsg['ZIRAN'] == None:
            pass
        else:
            REDICT["ZiRan"] = "不支持"
        for i in range(len(KIND_LIST)):
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "030006":
                    REDICT['VehicleLoss'] = KIND_LIST[i]['N_PRM']
            except:
                pass
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "030072":
                    REDICT['ZeRenCK'] = KIND_LIST[i]['N_PRM']
            except:
                pass
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "030070":
                    REDICT['ZeRenSJ'] = KIND_LIST[i]['N_PRM']
            except:
                pass
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "030018":
                    REDICT['SanZhe'] = KIND_LIST[i]['N_PRM']
            except:
                pass
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "031902":
                    REDICT['BuJiSZ'] = KIND_LIST[i]['N_PRM']
            except:
                pass
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "030059":
                    REDICT['DaoQiang'] = KIND_LIST[i]['N_PRM']
            except:
                pass
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "030106":
                    REDICT['BuJiDQ'] = KIND_LIST[i]['N_PRM']
            except:
                pass
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "033531":
                    REDICT['BuJiSJ'] = KIND_LIST[i]['N_PRM']
            except:
                pass
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "033532":
                    REDICT['BuJiCK'] = KIND_LIST[i]['N_PRM']
            except:
                pass
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "031901":
                    REDICT['BUJiCS'] = KIND_LIST[i]['N_PRM']
            except:
                pass
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "030004":
                    REDICT['BoLiPS'] = KIND_LIST[i]['N_PRM']
            except:
                pass
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "030012":
                    REDICT['ZiRan'] = KIND_LIST[i]['N_PRM']
            except:
                REDICT['ZiRan'] = "禁保"
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "031903":
                    REDICT['BUJIZR'] = KIND_LIST[i]['N_PRM']
            except:
                pass
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "030065":
                    REDICT['SheShui'] = KIND_LIST[i]['N_PRM']
            except:
                REDICT['SheShui'] = "禁保"
            try:
                if KIND_LIST[i]['C_KIND_CDE'] == "030025":
                    REDICT['HuaHen'] = KIND_LIST[i]['N_PRM']
            except:
                REDICT['HuaHen'] = "禁保"
        REDICT['BuJiMPZJ'] = round(float(REDICT['BuJiSZ']) + float(REDICT['BuJiDQ']) + float(REDICT['BuJiSJ']) + float(
            REDICT['BuJiCK']) + float(REDICT['BUJiCS']) + float(REDICT['BUJIZR']), 2)
        InCreatePay = BXDBAction()
        InCreatePay.CreatePayInfo(
            vin=self.vin,
            user_id=self.user_id,
            Session_ID=self.SessionID,
            ORDER_ID=ORDER,
            C_APP_NAME=self.ownerName,
            C_APP_IDENT_NO="",
            C_APP_TEL="",
            C_APP_ADDR="",
            C_APP_EMAIL="",
            C_INSRNT_NME=self.ownerName,
            C_INSRNT_IDENT_NO="",
            C_INSRNT_TEL="",
            C_INSRNT_ADDR="",
            C_INSRNT_EMAIL="",
            C_CONTACT_NAME ="",
            C_ADDRESS="",
            C_CONTACT_TEL ="",
            C_IDET_NAME=self.ownerName,
            C_IDENT_NO="",
            C_DELIVERY_PROVINCE="",
            C_DELIVERY_CITY="",
            C_DELIVERY_DISTRICT="",
            businesscode=businesscode,
            bxgs_type = "cic",
            status = '0',
            flag = True
        )
        CreatePrice = BXDBAction()
        CreatePrice.CreatPriceinfo_zh(
                            vin = self.vin,
                            biztotalpremium = REDICT['TotalPremium'],
                            vehicletaxpremium = REDICT['VehTaxPremium'],
                            forcepremium = REDICT['forcePre'],
                            bizbegindate = bizBeginDate,
                            forcebegindate = firstRegisterDate,
                            kind_030004 = REDICT['BoLiPS'],
                            kind_030006 = REDICT['VehicleLoss'],
                            kind_030012 = REDICT['ZiRan'],
                            kind_030018 = REDICT['SanZhe'],
                            kind_030025 = REDICT['HuaHen'],
                            kind_030059 = REDICT['DaoQiang'],
                            kind_030065 = REDICT['SheShui'],
                            kind_030070 = REDICT['ZeRenSJ'],
                            kind_030072 = REDICT['ZeRenCK'],
                            kind_030106 = REDICT['BuJiDQ'],
                            kind_030125 = '',
                            kind_031901 = REDICT['BUJiCS'],
                            kind_031902 = REDICT['BuJiSZ'],
                            kind_031903 = REDICT['BUJIZR'],
                            kind_031911 = '',
                            kind_033531 = REDICT['BuJiSJ'],
                            kind_033532 = REDICT['BuJiCK'],
                            kind_033535 = '',
                            ownername = self.ownerName
        )
        return ERR, ORDER, REDICT, RE,JinBaoMsg

    '''
    ORDER_ID, # 订单号
    C_APP_NAME,  # 投保人姓名
    C_APP_SEX,  # 投保人性别
    C_APP_IDENT_NO,  # 投保人证件号码
    C_APP_TEL,  # 投保人电话
    C_APP_ADDR,  # 投保人地址
    C_APP_EMAIL,  # 投保人邮箱
    C_APP_ZIPCODE,  # 投保人邮编
    C_INSRNT_NME,  # 被保险人姓名
    C_INSRNT_SEX,  # 别保险人性别
    C_INSRNT_IDENT_NO,  # 被保险人证件号码
    C_INSRNT_TEL,  # 被保险人电话
    C_INSRNT_ADDR,  # 被保险人地址
    C_INSRNT_EMAIL,  # 被保险人邮箱
    C_INSRNT_ZIPCODE,  # 被保险人邮编
    C_CONTACT_NAME,  # 联系人姓名
    C_CONTACT_TEL,  # 联系人电话
    C_CONTACT_EMAIL,  # 联系人邮箱
    C_DELIVERY_PROVINCE,  # 配送地址省代码
    C_DELIVERY_CITY,  # 配送地址市代码
    C_DELIVERY_DISTRICT,  # 配送地址区代码
    C_ADDRESS,  # 收件地址
    C_IDET_NAME,  # 行驶证车主
    C_IDENT_NO,  # 证件号
    '''

    def Get_1036(self, Session_ID, ORDER_ID='',vin='', C_APP_NAME='', C_APP_IDENT_NO='', C_APP_TEL='', C_APP_ADDR='',
                 C_APP_EMAIL='', C_APP_ZIPCODE='', C_INSRNT_NME='', C_INSRNT_IDENT_NO='', C_INSRNT_TEL='',
                 C_INSRNT_ADDR='', C_INSRNT_EMAIL='', C_INSRNT_ZIPCODE='', C_CONTACT_NAME='', C_CONTACT_TEL='',
                 C_CONTACT_EMAIL='', C_DELIVERY_PROVINCE='', C_DELIVERY_CITY='', C_DELIVERY_DISTRICT='', C_ADDRESS='',
                 C_IDET_NAME='', C_IDENT_NO='',ID=''):
        try:
            # 根据投保人身份证号判断投保人性别 (倒数第二位为奇数是男性，偶数是女性)
            C_APP_SEX = (int(C_APP_IDENT_NO[16:-1]) % 2 == 0) and '1062' or '1061'
            # 根据被保险人身份证号判断投保人性别
            C_INSRNT_SEX = (int(C_INSRNT_IDENT_NO[16:-1]) % 2 == 0) and '1062' or '1061'
        except:
            C_APP_SEX = "1061"
            C_INSRNT_SEX = "1061"
        if C_DELIVERY_PROVINCE.encode('utf-8') == '0':
            C_DELIVERY_PROVINCE = ""
        if C_DELIVERY_CITY.encode('utf-8') == '0':
            C_DELIVERY_CITY = ''
        if C_DELIVERY_DISTRICT.encode('utf-8') == '0':
            C_DELIVERY_DISTRICT = ''
        SendVal = (
            ORDER_ID,  # 订单号
            C_APP_NAME,  # 投保人姓名
            C_APP_SEX,  # 投保人性别
            C_APP_IDENT_NO,  # 投保人证件号码
            C_APP_TEL,  # 投保人电话
            C_APP_ADDR,  # 投保人地址
            C_APP_EMAIL,  # 投保人邮箱
            C_APP_ZIPCODE,  # 投保人邮编
            C_INSRNT_NME,  # 被保险人姓名
            C_INSRNT_SEX,  # 别保险人性别
            C_INSRNT_IDENT_NO,  # 被保险人证件号码
            C_INSRNT_TEL,  # 被保险人电话
            C_INSRNT_ADDR,  # 被保险人地址
            C_INSRNT_EMAIL,  # 被保险人邮箱
            C_INSRNT_ZIPCODE,  # 被保险人邮编
            C_CONTACT_NAME,  # 联系人姓名
            C_CONTACT_TEL,  # 联系人电话
            C_CONTACT_EMAIL,  # 联系人邮箱
            C_DELIVERY_PROVINCE,  # 配送地址省代码
            C_DELIVERY_CITY,  # 配送地址市代码
            C_DELIVERY_DISTRICT,  # 配送地址区代码
            C_ADDRESS,  # 收件地址
            C_IDET_NAME,  # 行驶证车主
            C_IDENT_NO,  # 证件号
        )
        RE = self.Send(Interface=1036, SendVal=SendVal, SessionID=Session_ID)
        REDICT = xmltodict.parse(RE, encoding="utf-8")
        # 获取是否有出错信息
        RESULTCODE = REDICT['INSUREQRET']['MAIN']['RESULTCODE']
        # 获取错误提示
        ERROR_INFO = REDICT['INSUREQRET']['MAIN']['ERR_INFO']
        ERR = (RESULTCODE <> "0000") and 1 or 0
        if ERR:
            REDICT = {"error":"1","msg":ERROR_INFO}
            self.EchoLog("1036出错了", ERROR_INFO)
            return ERR, REDICT
        else:
              InCreatePay = BXDBAction()
              Info = InCreatePay.CreatePayInfo(
                vin=vin,
                user_id=self.user_id,
                Session_ID=Session_ID,
                ORDER_ID=ORDER_ID,
                C_APP_NAME=C_APP_NAME,
                C_APP_IDENT_NO=C_APP_IDENT_NO,
                C_APP_TEL=C_APP_TEL,
                C_APP_ADDR=C_APP_ADDR,
                C_APP_EMAIL=C_APP_EMAIL,
                C_INSRNT_NME=C_INSRNT_NME,
                C_INSRNT_IDENT_NO=C_INSRNT_IDENT_NO,
                C_INSRNT_TEL=C_INSRNT_TEL,
                C_INSRNT_ADDR=C_INSRNT_ADDR,
                C_INSRNT_EMAIL=C_INSRNT_EMAIL,
                C_CONTACT_NAME =C_CONTACT_NAME,
                C_CONTACT_TEL = C_CONTACT_TEL,
                C_ADDRESS=C_ADDRESS,
                C_IDET_NAME=C_IDET_NAME,
                C_IDENT_NO=C_IDENT_NO,
                C_DELIVERY_PROVINCE=C_DELIVERY_PROVINCE,
                C_DELIVERY_CITY=C_DELIVERY_CITY,
                C_DELIVERY_DISTRICT=C_DELIVERY_DISTRICT,
                bxgs_type = "cic",
                status = "1",
                flag=True
            )
        # 返回信息
        '''
        ERR: 是否有错  1为有错，0为没错
        RE: 保险公司返回的xml全部信息
        '''
        if Info == False:
            ERROR_INFO="投保人与被保险人必须一致"
            REDICT = {"error":"1","msg":ERROR_INFO}
            self.EchoLog("1036出错了", ERROR_INFO)
            ERR='1'
            return ERR, REDICT
        return ERR, REDICT

    # 车险投保确认
    def Get_1037(self, Session_ID, ORDER_ID='',vin='', C_APP_NAME='', C_APP_IDENT_NO='', C_APP_TEL='', C_APP_ADDR='',
                 C_APP_EMAIL='', C_APP_ZIPCODE='', C_INSRNT_NME='', C_INSRNT_IDENT_NO='', C_INSRNT_TEL='',
                 C_INSRNT_ADDR='', C_INSRNT_EMAIL='', C_INSRNT_ZIPCODE='', C_CONTACT_NAME='', C_CONTACT_TEL='',
                 C_CONTACT_EMAIL='', C_DELIVERY_PROVINCE='', C_DELIVERY_CITY='', C_DELIVERY_DISTRICT='', C_ADDRESS='',
                 C_IDET_NAME='', C_IDENT_NO=''):
        # cdq 20150906修改
        ERR, REDICT = self.Get_1036(Session_ID=Session_ID, ORDER_ID=ORDER_ID,vin=vin, C_APP_NAME=C_APP_NAME, C_APP_IDENT_NO=C_APP_IDENT_NO, C_APP_TEL=C_APP_TEL, C_APP_ADDR=C_APP_ADDR,
                 C_APP_EMAIL=C_APP_EMAIL, C_APP_ZIPCODE=C_APP_ZIPCODE, C_INSRNT_NME=C_INSRNT_NME, C_INSRNT_IDENT_NO=C_INSRNT_IDENT_NO, C_INSRNT_TEL=C_INSRNT_TEL,
                 C_INSRNT_ADDR=C_INSRNT_ADDR, C_INSRNT_EMAIL=C_INSRNT_EMAIL, C_INSRNT_ZIPCODE=C_INSRNT_ZIPCODE, C_CONTACT_NAME=C_CONTACT_NAME, C_CONTACT_TEL=C_CONTACT_TEL,
                 C_CONTACT_EMAIL=C_CONTACT_EMAIL, C_DELIVERY_PROVINCE=C_DELIVERY_PROVINCE, C_DELIVERY_CITY=C_DELIVERY_CITY, C_DELIVERY_DISTRICT=C_DELIVERY_DISTRICT, C_ADDRESS=C_ADDRESS,
                 C_IDET_NAME=C_IDET_NAME, C_IDENT_NO=C_IDENT_NO)
        if ERR:
            return ERR, REDICT
        SendVal = (

            ORDER_ID.encode('utf-8'),  # 订单号
        )
        RE = self.Send(Interface=1037, SendVal=SendVal, SessionID=Session_ID)
        REDICT = xmltodict.parse(RE, encoding="utf-8")
        # 获取是否有出错信息
        RESULTCODE = REDICT['INSUREQRET']['MAIN']['RESULTCODE']
        # 获取错误提示
        ERROR_INFO = REDICT['INSUREQRET']['MAIN']['ERR_INFO']
        ERR = (RESULTCODE <> "0000") and 1 or 0
        if ERR:
            REDICT = {"error":"1","msg":ERROR_INFO}
            self.EchoLog("1037出错了", ERROR_INFO)
        return ERR, REDICT

    # 车险申请购买
    def Get_1038(self, Session_ID, ORDER_ID='',vin='', C_APP_NAME='', C_APP_IDENT_NO='', C_APP_TEL='', C_APP_ADDR='',
                 C_APP_EMAIL='', C_APP_ZIPCODE='', C_INSRNT_NME='', C_INSRNT_IDENT_NO='', C_INSRNT_TEL='',
                 C_INSRNT_ADDR='', C_INSRNT_EMAIL='', C_INSRNT_ZIPCODE='', C_CONTACT_NAME='', C_CONTACT_TEL='',
                 C_CONTACT_EMAIL='', C_DELIVERY_PROVINCE='', C_DELIVERY_CITY='', C_DELIVERY_DISTRICT='', C_ADDRESS='',
                 C_IDET_NAME='', C_IDENT_NO='',IsterInfo='',ID=''):
        ERR, REDICT = self.Get_1037(Session_ID=Session_ID, ORDER_ID=ORDER_ID,vin=vin, C_APP_NAME=C_APP_NAME, C_APP_IDENT_NO=C_APP_IDENT_NO, C_APP_TEL=C_APP_TEL, C_APP_ADDR=C_APP_ADDR,
                 C_APP_EMAIL=C_APP_EMAIL, C_APP_ZIPCODE=C_APP_ZIPCODE, C_INSRNT_NME=C_INSRNT_NME, C_INSRNT_IDENT_NO=C_INSRNT_IDENT_NO, C_INSRNT_TEL=C_INSRNT_TEL,
                 C_INSRNT_ADDR=C_INSRNT_ADDR, C_INSRNT_EMAIL=C_INSRNT_EMAIL, C_INSRNT_ZIPCODE=C_INSRNT_ZIPCODE, C_CONTACT_NAME=C_CONTACT_NAME, C_CONTACT_TEL=C_CONTACT_TEL,
                 C_CONTACT_EMAIL=C_CONTACT_EMAIL, C_DELIVERY_PROVINCE=C_DELIVERY_PROVINCE, C_DELIVERY_CITY=C_DELIVERY_CITY, C_DELIVERY_DISTRICT=C_DELIVERY_DISTRICT, C_ADDRESS=C_ADDRESS,
                 C_IDET_NAME=C_IDET_NAME, C_IDENT_NO=C_IDENT_NO)
        if ERR:
            PAY_URL = False
            return ERR, REDICT, PAY_URL
        SendVal = (
            ORDER_ID.encode('GBK'),  # 订单号
                  )
        RE = self.Send(Interface=1038, SendVal=SendVal, SessionID=Session_ID)
        REDICT = xmltodict.parse(RE, encoding='utf-8')
        if IsterInfo:
            PAY_URL = self.WAP_URL + str(ORDER_ID)
        else:
            PAY_URL = self.PAY_URL + str(ORDER_ID)
        # 获取是否有出错信息
        RESULTCODE = REDICT['INSUREQRET']['MAIN']['RESULTCODE']
        # 获取错误提示
        ERROR_INFO = REDICT['INSUREQRET']['MAIN']['ERR_INFO']

        ERR = (RESULTCODE <> "0000") and 1 or 0
        if ERR:
            REDICT = {"error":"1","msg":ERROR_INFO}
            PAY_URL = False
            self.EchoLog("1038出错了", ERROR_INFO)
            return ERR, REDICT, PAY_URL
        #投保单号
        C_PROPOSAL_NO_BIZ,C_PROPOSAL_NO_FORCE = self.GetBaoDan(REDICT['INSUREQRET']['POLICY_LIST']['POLICY'])
        InCreatePay = BXDBAction()
        InCreatePay.CreatePayInfo(
            flag=False,
            c_proposal_no_biz=C_PROPOSAL_NO_BIZ,
            c_proposal_no_force=C_PROPOSAL_NO_FORCE,
            vin=vin,
            C_IDET_NAME = C_IDET_NAME

        )
        return ERR, REDICT, PAY_URL
    def GetBaoDan(self,REDICT):
        try:
            for i in range(len(REDICT)):
                if REDICT[i]['BUSINESS_CODE'] == '11':
                    C_PROPOSAL_NO_BIZ = REDICT[i]['C_PROPOSAL_NO']
                if REDICT[i]['BUSINESS_CODE'] == '12':
                    C_PROPOSAL_NO_FORCE = REDICT[i]['C_PROPOSAL_NO']
            return C_PROPOSAL_NO_BIZ,C_PROPOSAL_NO_FORCE
        except:
            if REDICT['BUSINESS_CODE'] == '11':
                C_PROPOSAL_NO_BIZ = REDICT['C_PROPOSAL_NO']
                C_PROPOSAL_NO_FORCE = ""
            if REDICT['BUSINESS_CODE'] == '12':
                C_PROPOSAL_NO_BIZ = ""
                C_PROPOSAL_NO_FORCE = REDICT['C_PROPOSAL_NO']
            return C_PROPOSAL_NO_BIZ,C_PROPOSAL_NO_FORCE
    # 回调接口
    def CallBack(self, xml):
        BDAction = BXDBAction()
        BDAction.CreatCallBackLog(xml=xml,bxgs='cic',interface_type='')
        try:
            REDICT = xmltodict.parse(xml.encode('utf-8'), encoding='utf-8')
        except:
            ERROR = "XML格式不正确"
            RESULTCODE = "0001"
            SessionID = "NULL"
            BusinessCode = "NULL"
            RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
            return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
            # 支付回调
        if REDICT['INSUREQ']['MAIN']['TRANSRNO'] == "1039":
            return self.CallBack_1039(REDICT,xml=xml)
            # 保单通知回调
        if REDICT['INSUREQ']['MAIN']['TRANSRNO'] == "1040":
            return self.CallBack_1040(REDICT,xml=xml)

    def CallBack_1039(self, REDICT,xml):
        BDAction = BXDBAction()
        BDAction.CreatCallBackLog(xml=xml,bxgs='cic',interface_type='1039')
        ERROR = "交易成功"
        RESULTCODE = "0000"
        SessionID = ""
        BusinessCode = ""
        try:
            if REDICT['INSUREQ']['MAIN']['SERIALDECIMAL'] == '' or REDICT['INSUREQ']['MAIN']['SERIALDECIMAL'] == None:
                SessionID = "NULL"
                RESULTCODE = '0001'
                ERROR = "SERIALDECIMAL不能为空"
                BusinessCode = 'NULL'
                RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
                return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
            else:
                SessionID = REDICT['INSUREQ']['MAIN']['SERIALDECIMAL']
        except:
            pass
        try:
            if REDICT['INSUREQ']['BASE']['C_ORDER_NO'] == "" or REDICT['INSUREQ']['BASE']['C_ORDER_NO'] == None:  # 订单号
                SessionID = SessionID
                RESULTCODE = '0001'
                ERROR = "C_ORDER_NO不能为空"
                BusinessCode = 'NULL'
                RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
                return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
            else:
                ORDER_ID = REDICT['INSUREQ']['BASE']['C_ORDER_NO']
        except:
            pass
        try:
            if REDICT['INSUREQ']['PAY_INFO']['C_PAY_TRANSNO'] == "" or REDICT['INSUREQ']['PAY_INFO'][
                'C_PAY_TRANSNO'] == None:  # 支付流水号
                SessionID = SessionID
                RESULTCODE = '0001'
                ERROR = "C_PAY_TRANSNO不能为空"
                BusinessCode = 'NULL'
                RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
                return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
            else:
                C_PAY_TRANSNO = REDICT['INSUREQ']['PAY_INFO']['C_PAY_TRANSNO']
        except:
            pass
        try:
            if REDICT['INSUREQ']['PAY_INFO']['C_PAY_AMT'] == "" or REDICT['INSUREQ']['PAY_INFO'][
                'C_PAY_AMT'] == None:  # 支付金额
                SessionID = SessionID
                RESULTCODE = '0001'
                ERROR = "C_PAY_AMT不能为空"
                BusinessCode = 'NULL'
                RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
                return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
            else:
                C_PAY_AMT = REDICT['INSUREQ']['PAY_INFO']['C_PAY_AMT']
        except:
            pass
        try:
            if REDICT['INSUREQ']['PAY_INFO']['C_PAY_STAUS'] == "" or REDICT['INSUREQ']['PAY_INFO'][
                'C_PAY_STAUS'] == None:  # 支付状态
                SessionID = SessionID
                RESULTCODE = '0001'
                ERROR = "C_PAY_STAUS不能为空"
                BusinessCode = 'NULL'
                RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
                return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
            else:
                C_PAY_STAUS = REDICT['INSUREQ']['PAY_INFO']['C_PAY_STAUS']
        except:
            pass
        try:
            # if REDICT['INSUREQ']['PAY_INFO']['C_DESC'] == "" or REDICT['INSUREQ']['PAY_INFO'][
            #     'C_DESC'] == None:  # 支付描述
            #     SessionID = SessionID
            #     RESULTCODE = '0001'
            #     ERROR = "C_DESC不能为空"
            #     BusinessCode = 'NULL'
            #     RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
            #     return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
            # else:
                C_DESC = REDICT['INSUREQ']['PAY_INFO']['C_DESC']
        except:
            C_DESC = ''
        try:
            #     if REDICT['INSUREQ']['HEAD']['BUSINESS_CODE'] == "" or REDICT['INSUREQ']['HEAD'][
            #         'BUSINESS_CODE'] == None:  # 交易码
            #         SessionID = SessionID
            #         RESULTCODE = '0001'
            #         ERROR = "BUSINESS_CODE不能为空"
            #         BusinessCode = 'NULL'
            #         RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
            #         return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
            #     else:
            BusinessCode = REDICT['INSUREQ']['HEAD']['BUSINESS_CODE']
        except:
            BusinessCode = ''
        InCreatePay = BXDBAction()
        InCreatePay.CreateCallback(
                C_PAY_TRANSNO = C_PAY_TRANSNO,
                ORDER_ID = ORDER_ID,
                C_PAY_AMT = C_PAY_AMT,
                C_PAY_STAUS = C_PAY_STAUS,
                C_DESC = C_DESC,
                C_STAUS = "",
                C_MESSAGE = "",
                C_POLICY_NO_BIZ = "",
                C_POLICY_NO_FORCE = "",
                BusinessCode =BusinessCode,
            )
        RE = self.ReContent(SessionID, BusinessCode, ERROR, RESULTCODE)
        return HttpResponse(RE.encode('utf-8'), content_type="application/xml")

    def CallBack_1040(self, REDICT,xml):
        BDAction = BXDBAction()
        BDAction.CreatCallBackLog(xml=xml,bxgs='cic',interface_type='1040')
        ERROR = "交易成功"
        RESULTCODE = "0000"
        SessionID = ""
        BusinessCode = ""
        try:
            if REDICT['INSUREQ']['MAIN']['SERIALDECIMAL'] == '' or REDICT['INSUREQ']['MAIN']['SERIALDECIMAL'] == None:
                SessionID = "NULL"
                RESULTCODE = '0001'
                ERROR = "SERIALDECIMAL不能为空"
                BusinessCode = 'NULL'
                RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
                return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
            else:
                SessionID = REDICT['INSUREQ']['MAIN']['SERIALDECIMAL']
        except:
            pass
        try:
            if REDICT['INSUREQ']['BASE']['C_ORDER_NO'] == "" or REDICT['INSUREQ']['BASE']['C_ORDER_NO'] == None:  # 订单号
                SessionID = SessionID
                RESULTCODE = '0001'
                ERROR = "C_ORDER_NO不能为空"
                BusinessCode = 'NULL'
                RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
                return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
            else:
                ORDER_ID = REDICT['INSUREQ']['BASE']['C_ORDER_NO']
        except:
            pass
        try:
            if REDICT['INSUREQ']['BASE']['C_STAUS'] == "" or REDICT['INSUREQ']['BASE']['C_STAUS'] == None:  # 支付状态
                SessionID = SessionID
                RESULTCODE = '0001'
                ERROR = "C_STAUS不能为空"
                BusinessCode = 'NULL'
                RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
                return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
            else:
                C_STAUS = REDICT['INSUREQ']['BASE']['C_STAUS']
        except:
            pass
        try:
            # if REDICT['INSUREQ']['BASE']['C_MESSAGE'] == "" or REDICT['INSUREQ']['BASE']['C_MESSAGE'] == None:  # 支付状态
            #     SessionID = SessionID
            #     RESULTCODE = '0001'
            #     ERROR = "C_MESSAGE不能为空"
            #     BusinessCode = 'NULL'
            #     RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
            #     return HttpResponse(RE.encode('utf-8'), content_type="application/xml")
            # else:
                C_MESSAGE = REDICT['INSUREQ']['BASE']['C_MESSAGE']
        except:
            C_MESSAGE =''
        try:
            if REDICT['INSUREQ']['POLICY_LIST'] == "" or \
                            REDICT['INSUREQ']['POLICY_LIST'] == None:  # 支付状态
                SessionID = SessionID
                RESULTCODE = '0001'
                ERROR = "POLICY_LIST不能为空"
                BusinessCode = 'NULL'
                RE = self.ReContent(SessionID, RESULTCODE, BusinessCode, ERROR)
                return HttpResponse(RE.encode('utf-8'), content_type="application/xml")

            else:
                RELIST = REDICT['INSUREQ']['POLICY_LIST']['POLICY']
                try:
                    for i in range(len(RELIST)):
                        if RELIST[i]['BUSINESS_CODE'] == "11":
                                BizPolicyNo = RELIST[i]['C_POLICY_NO']  # 保单号
                        if RELIST[i]['BUSINESS_CODE'] == "12":
                                ForcePolicyNo = RELIST[i]['C_POLICY_NO']  # 保单号
                except:
                    if RELIST['BUSINESS_CODE'] == "11":
                            BizPolicyNo = RELIST['C_POLICY_NO']
                            ForcePolicyNo = ''
                    if RELIST['BUSINESS_CODE'] == "12":
                            ForcePolicyNo = RELIST['C_POLICY_NO']  # 保单号
                            BizPolicyNo = ''
        except:
            pass
        InCreatePay = BXDBAction()
        InCreatePay.CreateCallback(
            ORDER_ID=ORDER_ID,
            C_STAUS=C_STAUS,
            C_MESSAGE=C_MESSAGE,
            C_POLICY_NO_BIZ=BizPolicyNo,
            C_POLICY_NO_FORCE=ForcePolicyNo,
        )
        RE = self.ReContent(SessionID, BusinessCode, ERROR, RESULTCODE)
        return HttpResponse(RE.encode('utf-8'), content_type="application/xml")

    def ReContent(self, SessionID, RESULTCODE, BusinessCode, ERROR):
        SendVal = (SessionID,
                   self.AddTime,
                   RESULTCODE,
                   ERROR,
                   BusinessCode)

        file = WEB_ROOT + "/bxxml/zhonghua/" + str(1039) + ".xml"
        Val = open(file).read()
        XMLVal = Val % SendVal
        return XMLVal
    # 判断用户是否阅读浮动告知单
    def IsRead(self,flag,orderno,businessCode):
        if flag == "1":
            BDBAction = BXDBAction()
            BDBAction.IsRead(flag=flag,orderno=orderno,businesscode=businessCode)
            return "成功"
        else:
            return "0001"
    def Send(self, Interface, SendVal, SessionID=False):
        # 判断如果sessid是否传值，如果有，取传值
        if SessionID:
            SessID = SessionID
        else:
            SessID = self.SessionID

        # 头部认证信息
        InVal = (self.USER_NAME,
                 self.USER_PSW,
                 SessID,
                 self.AddTime,
                 self.CHANNELCODE,
                 )

        # 组合替换字段
        SendVal = InVal + SendVal
        # 打开文件
        file = WEB_ROOT + "/bxxml/zhonghua/" + str(Interface) + ".xml"
        Val = open(file).read()
        XMLVal = Val % SendVal
        self.EchoLog(content=XMLVal)
        # 发送XML
        response = self.client.service.getRequest(content=XMLVal)
        self.EchoLog(msg=Interface, content=response)
        return response

    def EchoLog(self, msg="", content="", status=0):
        if status == 0:
            print("++++++++++++++++++++++++++++start %s start++++++++++++++++++++++++" % msg)
            print(content)
            print("++++++++++++++++++++++++++++end %s end++++++++++++++++++++++++" % msg)
        else:
            pass

    def TestlicenseNo(self, licenseNo="", status=1):
        if status == 0:
            Lic = [
                {"licenseNo": "津A", "cityCode": "120100"},
                {"licenseNo": "冀A", "cityCode": "130100"}
            ]
            r = random.randint(0, 1)
            m = Lic[r]['licenseNo']
            cityCode = Lic[r]['cityCode']
            licenseNo = str(m) + licenseNo.decode('utf-8')[2:7].encode('utf-8')
            return cityCode, licenseNo
        else:
            return None, None
