# -*- coding:utf-8 -*-
from LYZ.common import makeNew
from common import *
import datetime, random, urllib, urllib2, time
from LYZ.settings import *
from suds.client import *
import sys, xmltodict
import json
import re
import dicttoxml

reload(sys)
sys.setdefaultencoding('utf-8')


# 中华保险
class ZhongHua(object):
    # 测试地址
    TEST_URL = "http://220.171.28.152:9080/nsp/services/NetSalePlatform?wsdl"
    # 测试支付地址
    TEST_PAY_URL = "http://220.171.28.152:9080/nsp/payment/payment.do?orderNo="
    # 阳光车型查询地址
    YG_SEACH_URL = "http://chexian.sinosig.com/Partner/netVehicleModel.action?page=1&pageSize=6&searchCode=&searchType=1&encoding=utf-8&isSeats=1&callback=jQuery111206209229775800245_1441631982195&_=1441631982199"


    # 用户名
    USER_NAME = "ECUser"
    # 密码
    USER_PSW = "EC100"
    # 渠道代码
    CHANNELCODE = "001501"

    def __init__(self,
                 citycode,
                 licenseNo,
                 ownerName,
                 vin,
                 engineNo,
                 vehicleModelName,
                 ):
        self.citycode = citycode
        self.licenseNo = licenseNo
        self.ownerName = ownerName
        self.vin = vin
        self.engineNo = engineNo
        self.vehicleModelName = vehicleModelName
        # 车辆注册日期
        self.firstRegisterDate = str((datetime.date.today() + datetime.timedelta(days=-365 * 2)).strftime("%Y-%m-%d"))
        # 商业保险起期
        self.bizBeginDate = str((datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"))
        # 交强险起期
        self.forceBeginDate = str((datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"))
        self.SessionID = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + str(
            random.randint(100000000000000000, 999999999999999999))
        self.AddTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.client = Client(self.TEST_URL, location=self.TEST_URL, cache=None)
        self.my1030 = None  # 接收用户信息
        self.my1031 = None  # 1031接口返回字典
        self.my1031s = None  # 接收用户输信息
        self.my1032 = None  # 1032接口返回字典
        self.my1033 = None  # 1033接口返回字典(订单号,保费)
        self.my1038 = None  # 1038接口返回投保单号
        self.my1033bx = None  # 1033险别信息
        self.ownerid = makeNew()

    # 1030基本信息录入接口
    def Get_1030(self):
        # cdq20150907 修改
        SendVal = (
            self.citycode,
            self.licenseNo,
            '0'
        )
        X = self.Send(Interface=1030, SendVal=SendVal)
        self.my1030 = SendVal
        return self.Send(Interface=1030, SendVal=SendVal)

    # 车辆车型查询接口
    def Get_1031(self, **pam):
        """
        车辆车型查询接口

        Args:
            pam (list): 传入参数
            SendVal (tuple):  需要向保险服务器提交的数据

        Returns:
          str: 返回结果

        """
        SendVal = (
            self.citycode,  # 地区编码
            self.licenseNo,  # 车牌号码
            self.ownerName,  # 行驶证车主
            self.engineNo,  # 发动机号
            self.vin,  # 车架号
            self.vehicleModelName,  # 品牌型号
            self.firstRegisterDate,  # 车辆初始登记日期
        )
        self.my1031s = SendVal
        self.RT = self.Send(Interface=1031, SendVal=SendVal)
        self.my1031 = xmltodict.parse(self.RT, encoding='utf-8')
        return self.RT

    # 车险承保方案信息接口
    def Get_1032(self, **pam):
        # cdq20150907 修改
        DBAction = BXDBAction()
        try:
            SendVal = (
                self.my1031s[0],  # 地区编码
                self.bizBeginDate,  # 商业险保单起期
                time.strftime('%Y-%m-%d'),  # 录单日期
                '',  # 服务专员
                '',  # 机构代码
                '',  # 业务来源
                '',  # 服务代码
                self.my1031s[1],  # 车牌号码
                self.my1030[2],  # 是否新车
                self.my1031s[2],  # 车主姓名
                '',  #
                self.my1031s[3],  # 发动机号
                self.my1031s[4],  # 车架号
                self.my1031s[6],  # 车辆初始登记日期
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]['C_VEHICLE_CODE'],  # 车型代码（车型编码）
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]['C_MODEL_DESC'],  # 车型描述
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]['C_VEHICLE_BRAND'],  # 品牌名称
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]['C_VEHICLE_NAME'],  # 车型名称
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]['C_VEHICLE_FAMILY'],  # 车系名称（车型库车系）
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]['C_IMPORT_FLAG'],  # 车型种类 (国产/进口/合资)
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]['N_LIMIT_LOAD_PERSON'],  # 核定载客人数
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]['C_WHOLE_WEIGHT'],  # 整备质量
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]['N_VEHICLE_TONNAGE'],  # 载重量
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]['C_EXT_MSR'],  # 排气量
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]['C_MARKET_TIMESTAMP'],  # 上市年份
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL'][0]['N_VEHICLE_PRICE'],  # 新车购置价
            )
        except KeyError:
            SendVal = (
                self.my1031s[0],  # 地区编码
                self.bizBeginDate,  # 商业险保单起期
                time.strftime('%Y-%m-%d'),  # 录单日期
                '',  # 服务专员
                '',  # 机构代码
                '',  # 业务来源
                '',  # 服务代码
                self.my1031s[1],  # 车牌号码
                self.my1030[2],  # 是否新车
                self.my1031s[2],  # 车主姓名
                '',  #
                self.my1031s[3],  # 发动机号
                self.my1031s[4],  # 车架号
                self.my1031s[6],  # 车辆初始登记日期
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['C_VEHICLE_CODE'],  # 车型代码（车型编码）
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['C_MODEL_DESC'],  # 车型描述
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['C_VEHICLE_BRAND'],  # 品牌名称
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['C_VEHICLE_NAME'],  # 车型名称
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['C_VEHICLE_FAMILY'],  # 车系名称（车型库车系）
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['C_IMPORT_FLAG'],  # 车型种类 (国产/进口/合资)
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['N_LIMIT_LOAD_PERSON'],  # 核定载客人数
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['C_WHOLE_WEIGHT'],  # 整备质量
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['N_VEHICLE_TONNAGE'],  # 载重量
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['C_EXT_MSR'],  # 排气量
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['C_MARKET_TIMESTAMP'],  # 上市年份
                self.my1031['INSUREQRET']['VHLMODEL_LIST']['VHLMODEL']['N_VEHICLE_PRICE'],  # 新车购置价
            )
        finally:
            try:
                self.X = self.Send(Interface=1032, SendVal=SendVal)
                self.my1032 = xmltodict.parse(self.X, encoding='utf-8')
                DBAction.CreateTBSJinfo(licenseno=self.licenseNo,
                                        order_id=self.my1032['INSUREQRET']['BASE']['C_ORDER_NO'],
                                        biz_begin_date=self.bizBeginDate,
                                        biz_end_date='',
                                        traff_begin_date='',
                                        traff_end_date='',
                                        cs_traff_amt=self.my1032['INSUREQRET']['KIND_LIST']['KIND'][0]['N_DEFAULT_AMT'],
                                        dq_traff_amt=self.my1032['INSUREQRET']['KIND_LIST']['KIND'][4]['N_DEFAULT_AMT'],
                                        zr_traff_amt=self.my1032['INSUREQRET']['KIND_LIST']['KIND'][11]['N_DEFAULT_AMT'],
                                        first_register_date=self.firstRegisterDate
                                        )
                return self.X
            except:
                a = ('问题出现在1031接口')
                print(a.encode('GBK') + (self.RT).encode('GBK'))

    # 车辆报价接口
    def Get_1033(self,
                 licenseNo='',
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
                 ):
        DBAction = BXDBAction()
        CARINFO,TBSJINFO = DBAction.GetTBSJinfo(licenseno=licenseNo, bxtype="cic")
        HUAHEN = (HUAHEN == '0') and ''or HUAHEN
        SHESHUI = (SHESHUI == '0') and ''or SHESHUI
        CHESHUN = (CHESHUN == '0') and '' or CHESHUN
        BAOE_CHESUN = (CHESHUN == '1') and TBSJINFO['cs_traff_amt'] or ''
        SANZHE = (SANZHE == '0') and '' or SANZHE
        SHIJI = (SHIJI == '0') and '' or SHIJI
        CHENGKE = (CHENGKE == '0') and '' or CHENGKE
        DAOQIANG = (DAOQIANG == '0') and '' or DAOQIANG
        BAOE_DABQIANG = (DAOQIANG == '1') and TBSJINFO['dq_traff_amt'] or ''
        ZIRAN = (ZIRAN == '0') and '' or ZIRAN
        BAOE_ZIRAN = (ZIRAN == '1') and TBSJINFO['zr_traff_amt'] or ''
        BOLI = (BOLI == '0') and '' or BOLI
        DAOQIANG_BJ = (DAOQIANG_BJ == '0') and '' or DAOQIANG_BJ
        CHESHUN_BJ = (CHESHUN_BJ == '0') and '' or CHESHUN_BJ
        SANZHE_BJ = (SANZHE_BJ == '0') and '' or SANZHE_BJ
        SHIJI_BJ = (SHIJI_BJ == '0') and '' or SHIJI_BJ
        CHENGKE_BJ = (CHENGKE_BJ == '0') and '' or CHENGKE_BJ
        BAOE_BJ_CHESUN = (CHESHUN_BJ == '1') and '0' or ''
        BAOE_BJ_CHENGKE = (CHENGKE_BJ == '1') and '0' or ''
        BAOE_BJ_SIJI = (SHIJI_BJ == '1') and '0' or ''
        BAOE_BJ_DAOQIANG = (DAOQIANG_BJ == '1') and '0' or ''
        BAOE_BJ_SANZHE = (SANZHE_BJ == '1') and '0' or ''
        BAOE_BOLI = (BOLI == '1') and '0' or ''
        BAOE_CK = (CHENGKE == '1') and BAOE_CK or ''  # 乘客保额
        BAOE_SZ = (SANZHE == '1') and BAOE_SZ or ''  # 第三者责任险保额
        BAOE_SJ = (SHIJI == '1') and BAOE_SJ or ''  # 司机保额
        CODE_CHESHUN = (CHESHUN == '1') and '030006' or ''  # 车损险
        CODE_ZERENSANZHE = (SANZHE == '1') and '030018' or ''  # 三者险
        CODE_DAOQIANG = (DAOQIANG == '1') and '030059' or ''  # 盗抢险
        CODE_ZERENSIJI = (SHIJI == '1') and '030070' or ''  # 责任险（司机）
        CODE_ZERENCK = (CHENGKE == '1') and '030072' or ''  # 责任险（乘客）
        CODE_BOLI = (BOLI == '1') and '030004' or ''  # 玻璃单独破碎
        CODE_ZIRAN = (ZIRAN == '1') and '030012' or ''  # 自燃险
        CODE_BJ_CHESHUN = (CHESHUN_BJ == '1') and '031901' or ''  # 不计车损
        CODE_BJ_SHANZHE = (SANZHE_BJ == '1') and '031902' or ''  # 不计三者
        CODE_BJ_DAOQIANG = (DAOQIANG_BJ == '1') and '030106' or ''  # 不计盗抢
        CODE_BJ_SIJI = (SHIJI_BJ == '1') and '033531' or ''  # 不计司机
        CODE_BJ_CHENGKE = (CHENGKE_BJ == '1') and '030072' or ''  # 不计乘客
        SendVal = (
            CARINFO['citycode'],  # 地区编码
            TBSJINFO['order_id'],  # 订单号
            TBSJINFO['biz_begin_date'],  # 商业保单起期
            '',  # 商业保单止期
            '',  # 交强险起期
            '',  # 交强险止期
            '1',  # 是否约省
            '1',
            CODE_CHESHUN,  # 机动车损失险
            CHESHUN,  # 是否投保
            BAOE_CHESUN,
            '2',
            CODE_ZERENCK,  # 责任险（乘客）
            BAOE_CK,  # 保额/限额(元)
            '3',
            CODE_ZERENSIJI,  # 责任险（司机）
            BAOE_SJ,  # 保额/限额(元)
            '4',
            CODE_ZERENSANZHE,  # 第三者责任险
            BAOE_SZ,  # 保额
            '5',
            CODE_BJ_SHANZHE,  # 不计三者险
            SANZHE_BJ,  # 是否投保
            BAOE_BJ_SANZHE,  #
            '6',
            CODE_DAOQIANG,  # 机动车盗抢险
            DAOQIANG,
            BAOE_DABQIANG,  # 投保限额
            '7',
            CODE_BJ_DAOQIANG,  # 不计盗抢
            DAOQIANG_BJ,
            BAOE_BJ_DAOQIANG,
            '8',
            CODE_BJ_SIJI,  # 不计司机
            SHIJI_BJ,
            BAOE_BJ_SIJI,
            '9',
            CODE_BJ_CHENGKE,  # 不计乘客
            CHENGKE_BJ,
            BAOE_BJ_CHENGKE,
            '10',
            CODE_BOLI,  # 玻璃单独破碎险
            BOLI,
            BAOE_BOLI,  # 玻璃保额
            '11',
            CODE_ZIRAN,  # 自然损失险
            ZIRAN,
            BAOE_ZIRAN,
            '12',
            CODE_BJ_CHESHUN,  # 不计车损
            CHESHUN,
            BAOE_BJ_CHESUN,
            self.ownerid,  # 车主证件号码
            '',  # 购车发票开具日期
            '',  # 车辆来历凭证种类
            '',  # 车辆来历凭证编号
            '',  # 开具车辆来历凭证所载日期
            CARINFO['ownername'],  # 驾驶员名称
            self.ownerid, # 驾驶证号(身份证号)makeNew()自动生成身份证号
            TBSJINFO['first_register_date']  # 初次领证日期
        )
        self.my1033bx = SendVal
        X = self.Send(Interface=1033, SendVal=SendVal)
        print(X)
        self.my1033 = xmltodict.parse(X, encoding='utf-8')
        Q = self.ReArr(X)
        return Q






    #  投保信息校验接口
    def Get_1036(self, licenseno='',**pam):
        # cdq 20150906 修改
        DBAction = BXDBAction()
        CARINFO,TBSJINFO = DBAction.GetTBSJinfo(licenseno=licenseno, bxtype="cic")
        SendVal = (
            TBSJINFO['order_id'],  # 订单号
            CARINFO['ownername'],  # 投保人姓名
            pam['C_APP_SEX'],  # 投保人性别
            pam['C_APP_IDENT_TYPE'],  # 投保人证件类型
            pam['C_APP_IDENT_NO'],  # 投保人证件号码
            pam['C_APP_TEL'],  # 投保人电话
            pam['C_APP_ADDR'],  # 投保人地址
            pam['C_APP_EMAIL'],  # 投保人邮箱
            pam['C_APP_ZIPCODE'],  # 投保人邮编
            pam['C_INSRNT_NME'],  # 被保险人姓名
            pam['C_INSRNT_SEX'],  # 别保险人性别
            pam['C_INSRNT_IDENT_TYPE'],  # 被保险人证件类型
            pam['C_INSRNT_IDENT_NO'],  # 被保险人证件号码
            pam['C_INSRNT_TEL'],  # 被保险人电话
            pam['C_INSRNT_ADDR'],  # 被保险人地址
            pam['C_INSRNT_EMAIL'],  # 被保险人邮箱
            pam['C_INSRNT_ZIPCODE'],  # 被保险人邮编
            pam['C_CONTACT_NAME'],  # 联系人姓名
            pam['C_CONTACT_TEL'],  # 联系人电话
            pam['C_CONTACT_EMAIL'],  # 联系人邮箱
            pam['C_DELIVERY_PROVINCE'],  # 配送地址省代码
            pam['C_DELIVERY_CITY'],  # 配送地址市代码
            pam['C_DELIVERY_DISTRICT'],  # 配送地址区代码
            pam['C_ADDRESS'],  # 收件地址
            CARINFO['ownername'],  # 行驶证车主
            pam['C_IDENT_TYPE'],  # 证件类型
            pam['C_IDENT_NO']  # 证件号

        )
        X = self.Send(Interface=1036, SendVal=SendVal)

        return X

    # 车险投保确认
    def Get_1037(self, licenseno=''):
        # cdq 20150906修改
        DBAction = BXDBAction()
        CARINFO,TBSJINFO = DBAction.GetTBSJinfo(licenseno=licenseno, bxtype="cic")
        SendVal = (

            TBSJINFO['order_id'],  # 订单号
            ''  # 任意字段(不加Type为unicode)
        )
        X = self.Send(Interface=1037, SendVal=SendVal)
        print X
        return X

    # 车险申请购买
    def Get_1038(self, licenseno=''):
        # cdq 20150906修改
        DBAction = BXDBAction()
        CARINFO,TBSJINFO = DBAction.GetTBSJinfo(licenseno=licenseno, bxtype="cic")
        SendVal = (

            TBSJINFO['order_id'],  # 订单号
            ''  # 任意字段(不加Type为unicode 报错)
        )
        X = self.Send(Interface=1038, SendVal=SendVal)
        self.my1038 = xmltodict.parse(X, encoding='utf-8')
        return (X)

    def Send(self, Interface, SendVal):
        # 头部认证信息
        InVal = (self.USER_NAME,
                 self.USER_PSW,
                 self.SessionID,
                 self.AddTime,
                 self.CHANNELCODE,
                 )

        # 组合替换字段
        SendVal = InVal + SendVal
        # 打开文件
        file = WEB_ROOT + "/bxxml/zhonghua/" + str(Interface) + ".xml"
        Val = open(file).read()

        # 替换变量
        XMLVal = Val % SendVal
        print(XMLVal)
        # 发送XML
        response = self.client.service.getRequest(content=XMLVal)
        return response

    # 截取返回的XMl中报价的数据并返回报价字典
    # cdq 20150910 修改
    def ReArr(self, data):
        Data = data.replace("\n", "")
        # 替换空格
        result, number = re.subn(">(\s{1,})<", "><", Data)
        TotalPremium = re.findall('<N_REAL_PRM>(.*?)</N_REAL_PRM>', result.encode('UTF-8'))
        VehicleLoss = re.findall(
            '<C_KIND_CDE>030006</C_KIND_CDE><C_KIND_NAME>机动车损失保险</C_KIND_NAME><N_AMT>(.*?)</N_AMT><N_PRM>(.*?)</N_PRM><N_BEN_PRM>(.*?)</N_BEN_PRM>',
            result.encode('UTF-8'))
        ZeRenCK = re.findall(
            '<C_KIND_CDE>030072</C_KIND_CDE><C_KIND_NAME>机动车车上人员责任保险（乘客）</C_KIND_NAME><N_SEAT_NUM>(.*?)</N_SEAT_NUM><N_AMT>(.*?)</N_AMT><N_PRM>(.*?)</N_PRM><N_BEN_PRM>(.*?)</N_BEN_PRM>',
            result.encode('UTF-8'))
        ZeRenSJ = re.findall(
            '<C_KIND_CDE>030070</C_KIND_CDE><C_KIND_NAME>机动车车上人员责任保险（司机）</C_KIND_NAME><N_SEAT_NUM>1</N_SEAT_NUM><N_AMT>(.*?)</N_AMT><N_PRM>(.*?)</N_PRM><N_BEN_PRM>(.*?)</N_BEN_PRM>',
            result.encode('UTF-8'))
        SanZhe = re.findall(
            '<C_KIND_CDE>030018</C_KIND_CDE><C_KIND_NAME>机动车第三者责任保险</C_KIND_NAME><N_AMT>(.*?)</N_AMT><N_PRM>(.*?)</N_PRM><N_BEN_PRM>(.*?)</N_BEN_PRM>',
            result.encode('UTF-8'))
        BuJiSZ = re.findall(
            '<C_KIND_CDE>031902</C_KIND_CDE><C_KIND_NAME>不计免赔特约条款（三者险）</C_KIND_NAME><N_AMT>(.*?)</N_AMT><N_PRM>(.*?)</N_PRM><N_BEN_PRM>(.*?)</N_BEN_PRM>',
            result.encode('UTF-8'))
        DaoQiang = re.findall(
            '<C_KIND_CDE>030059</C_KIND_CDE><C_KIND_NAME>机动车全车盗窃保险</C_KIND_NAME><N_AMT>(.*?)</N_AMT><N_PRM>(.*?)</N_PRM><N_BEN_PRM>(.*?)</N_BEN_PRM>',
            result.encode('UTF-8'))
        BuJiDQ = re.findall(
            '<C_KIND_CDE>030106</C_KIND_CDE><C_KIND_NAME>不计免赔特约条款（盗抢险）</C_KIND_NAME><N_AMT>(.*?)</N_AMT><N_PRM>(.*?)</N_PRM><N_BEN_PRM>(.*?)</N_BEN_PRM>',
            result.encode('UTF-8'))
        BuJiSJ = re.findall(
            '<C_KIND_CDE>033531</C_KIND_CDE><C_KIND_NAME>不计免赔特约条款（车上人员司机）</C_KIND_NAME><N_AMT>(.*?)</N_AMT><N_PRM>(.*?)</N_PRM><N_BEN_PRM>(.*?)</N_BEN_PRM>',
            result.encode('UTF-8'))
        BuJiCK = re.findall(
            '<C_KIND_CDE>033532</C_KIND_CDE><C_KIND_NAME>不计免赔特约条款（车上人员乘客）</C_KIND_NAME><N_AMT>(.*?)</N_AMT><N_PRM>(.*?)</N_PRM><N_BEN_PRM>(.*?)</N_BEN_PRM>',
            result.encode('UTF-8'))
        BUJiCS = re.findall(
            '<C_KIND_CDE>031901</C_KIND_CDE><C_KIND_NAME>不计免赔特约条款（车损险）</C_KIND_NAME><N_AMT>(.*?)</N_AMT><N_PRM>(.*?)</N_PRM><N_BEN_PRM>(.*?)</N_BEN_PRM>',
            result.encode('UTF-8'))
        BoLiPS = re.findall(
            '<C_KIND_CDE>030004</C_KIND_CDE><C_KIND_NAME>玻璃单独破碎险</C_KIND_NAME><N_AMT>(.*?)</N_AMT><N_PRM>(.*?)</N_PRM><N_BEN_PRM>(.*?)</N_BEN_PRM>',
            result.encode('UTF-8'))
        ZiRan = re.findall(
            '<C_KIND_CDE>030012</C_KIND_CDE><C_KIND_NAME>自燃损失险</C_KIND_NAME><N_AMT>(.*?)</N_AMT><N_PRM>(.*?)</N_PRM><N_BEN_PRM>(.*?)</N_BEN_PRM>',
            result.encode('UTF-8'))

        ReDict = {'TotalPremium': ' 0',  # 保费合计
                  'BizPremium': ' 0',  # 商业险总计
                  'ForePremium': '0',  # 交强险总计
                  'InsuranceGift': '暂无礼品',  # 保险公司礼品
                  'klbGift': '暂无礼品',  # 卡来宝礼品
                  'bizPremium': '0',  # 商业险总计
                  'VehicleLoss': '0',  # 车辆损失险
                  'SanZhe': '0',  # 第三者责任险
                  'DaoQiang': '0',  # 盗抢险
                  'ZeRenSJ': '0',  # 车上人员责任险（司机）
                  'ZeRenCK': '0',  # 车上人员责任险（乘客）
                  'BoLiPS': '0',  # 玻璃单独破碎险
                  'HuaHen': '暂不支持',  # 划痕险
                  'ZiRan': '0',  # 自燃险
                  'SheShui': '0',  # 涉水险
                  'BuJiMPZJ': '0',  # 不计免赔总计
                  'BUJiCS': '0',  # 不计车损
                  'BuJiSZ': '0',  # 不计三者
                  'BuJiDQ': '0',  # 不计盗抢
                  'BuJiSJ': '0',  # 不计司机
                  'BuJiCK': '0',  # 不计乘客
                  'forcePremium': '暂不支持',  # 交强总计
                  'forcePre': '暂不支持',  # 交强险
                  'VehTaxPremium': '暂不支持',  # 车船税
                  'totalPremium': '0',  # 保险合计
                  'ORDER_ID': '0'  # 订单号
                  }
        try:
            ReDict['ORDER_ID'] = self.my1032['INSUREQRET']['BASE']['C_ORDER_NO']
        except:
            pass
        try:
            ReDict['DaoQiang'] = DaoQiang[0][2]
        except:
            pass
        try:
            ReDict['BuJiSZ'] = BuJiSZ[0][2]
        except:
            pass
        try:
            ReDict['BuJiDQ'] = BuJiDQ[0][2]
        except:
            pass
        try:
            ReDict['BuJiSJ'] = BuJiSJ[0][2]
        except:
            pass
        try:
            ReDict['BuJiCK'] = BuJiCK[0][2]
        except:
            pass
        try:
            ReDict['BUJiCS'] = BUJiCS[0][2]
        except:
            pass
        try:
            ReDict['BuJiMPZJ'] = float(BuJiSZ[0][2]) + float(BuJiDQ[0][2]) + float(BuJiSJ[0][2]) + float(
                BuJiCK[0][2]) + float(BUJiCS[0][2])
        except:
            pass
        try:
            ReDict['BoLiPS'] = BoLiPS[0][2]
        except:
            pass
        try:
            ReDict['ZiRan'] = ZiRan[0][2]
        except:
            pass
        try:
            ReDict['TotalPremium'] = TotalPremium
        except:
            pass
        try:
            ReDict['BizPremium'] = TotalPremium
        except:
            pass
        try:
            ReDict['VehicleLoss'] = VehicleLoss[0][2]
        except:
            pass
        try:
            ReDict['ZeRenCK'] = ZeRenCK[0][3]
        except:
            pass
        try:
            ReDict['ZeRenSJ'] = ZeRenSJ[0][2]
        except:
            pass
        try:
            ReDict['SanZhe'] = SanZhe[0][2]
        except:
            pass
        try:
            ReDict['bizPremium'] = TotalPremium
        except:
            pass
        try:
            ReDict['totalPremium'] = TotalPremium
        except:
            pass
        return ReDict


class KLBNet(Object):
    GetCarInfoUrl = "http://chexian.sinosig.com/Net/vehicleStandard.action"
    GetCarInfoUrl1 = "http://chexian.sinosig.com/Net/vehicleModel.action"

    def GetCarInfo(self, q="", t=0, v=1):
        t = int(t)
        if t == 0:
            para = {
                "limit": "0",
                "timestamp": int(time.time()) * 1000,
                "queryVehicle": q.upper(),
                "frameNo": "",
                "id": "",
                "frameNoFlag": "true",
            }
            postData = urllib.urlencode(para)
            req = urllib2.Request(self.GetCarInfoUrl, postData)
        else:
            postData = urllib.urlencode({"vehicleFgwCode": q, "isGetValue": v})
            req = urllib2.Request(self.GetCarInfoUrl1, postData)
        resp = urllib2.urlopen(req).read()
        return resp
