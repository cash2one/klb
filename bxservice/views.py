# -*- coding:utf-8 -*-
from django.shortcuts import *
from bxservice.zhonghua import *
from bxservice.ansheng import *
from bxservice.yangguang import *
from bxservice.common import *
from bxservice.common import BXDBAction
from bxservice.models import *
from LYZ.klb_class import *
from urllib import unquote
from bxservice.ZhongHuaAction import *
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
#　保险公司回调接口
def PayCallback(request, a="zh"):
    if request.method == "POST":
        xml = request.REQUEST.get("xml", "")
        if a == "zh" or a == "newzh":
            ZH = ZhongHuaAction()
            CallBack = ZH.CallBack(xml)
            return HttpResponse(CallBack, content_type="application/xml")
        if a == "as" or a == "newas":
            AS = AnSheng()
            CallBack = AS.CallBack(xml)
            return HttpResponse(CallBack, content_type="application/xml")
        if a == "yg" or a == "newyg":
            YG = YangGuang()
            CallBack = YG.CallBack(xml=xml)
            return HttpResponse(CallBack, content_type="application/xml")
        else:
            pass
        return HttpResponse("!")

    else:
        xml = '<?xml version="1.0" encoding="utf-8" standalone="yes"?><INSUREQRET><MAIN><SERIALDECIMAL>NULL</SERIALDECIMAL><TRANSRDATE></TRANSRDATE><RESULTCODE>0001</RESULTCODE><ERR_INFO>请用POST提交数据</ERR_INFO><BUSINESS_CODE>NULL</BUSINESS_CODE></MAIN></INSUREQRET>'
        return HttpResponse(xml, content_type="application/xml")
        # return render_to_response('web/bxpaycallback.html', {}, context_instance=RequestContext(request))
def PayCallback_AS(request, ):
    if request.method == 'POST':
        xml=request.REQUEST.get("xml",'')
        AS = AnSheng()
        CallBack = AS.CallBack(xml)
        return HttpResponse(CallBack, content_type="application/xml")
    else:
        xml = '<?xml version="1.0" encoding="utf-8" standalone="yes"?><INSUREQRET><MAIN><SERIALDECIMAL>NULL</SERIALDECIMAL><TRANSRDATE></TRANSRDATE><RESULTCODE>0001</RESULTCODE><ERR_INFO>请用POST提交数据</ERR_INFO><BUSINESS_CODE>NULL</BUSINESS_CODE></MAIN></INSUREQRET>'
        return HttpResponse(xml, content_type="application/xml")
# 存入浮动回调信息
def IsReadCallback(request):
    # if request.method == 'GET':
        flag = request.REQUEST.get('flag','')
        orderno = request.REQUEST.get('orderno','')
        businessCode = request.REQUEST.get("businessCode",'')
        if flag == '' or flag == None:
            return HttpResponse("0001")
        if orderno == '' or orderno == None:
            return HttpResponse("0001")
        if businessCode == '' or businessCode == None:
            return HttpResponse("0001")
        ZH = ZhongHuaAction()
        # try:
        RE = ZH.IsRead(flag=flag,orderno=orderno,businessCode=businessCode)
        # except:
        #     return HttpResponse("0001")
        return HttpResponse(orderno)
    # else:
    #     return HttpResponse("0001")
# 点击阅读确定费率浮动告知单
def ConfirmFeiLv(request):
    KLBPrint = PrintJson()
    if request.method == 'POST':
        orderno = request.REQUEST.get("order_id",'')
        M = request.REQUEST.get('M','')
        print(request.REQUEST.items())
        Confirm = ConfirmRate(Order_id=orderno)
        RE = Confirm.Confirm(M=M)
        J = KLBPrint.echo(msg="数据返回", data=RE, error=0)
        return HttpResponse(J)
# 读取浮动信息
def GetRead(request):
    KLBPrint = PrintJson()
    if request.method == 'POST':
        orderno = request.REQUEST.get('order_id','')
        M = request.REQUEST.get('M','')
        BDAction = BXDBAction()
        RE = BDAction.GetRead(orderno=orderno,M=M)
        R = KLBPrint.echo(msg="数据返回", data=RE, error=0)
        return HttpResponse(R)
    else:
        return  HttpResponse("!")
# 读取保险公司回调信息 返回订单号
def GetCallBack(request):
    KLBPrint = PrintJson()
    if request.method == "POST":
        Session_ID = request.REQUEST.get('Session_ID',"")
        bxgs = request.REQUEST.get('bxgs',"")
        BDAction = BXDBAction()
        RE = BDAction.GetCallBackInfo(sessionid=Session_ID,bxgs=bxgs)
        J = KLBPrint.echo(msg="数据返回", data=RE, error=0)
        return HttpResponse(J)
    else:
        RE = {'error':'1',}
        J = KLBPrint.echo(msg="数据返回", data=RE, error=0)
        return HttpResponse(J)
# 读取 保险公司回调信息
def GetPolicy(request):
    KLBPrint = PrintJson()
    print(request.REQUEST.items())
    if request.method == "POST":
        PolicyNO = request.REQUEST.get("PolicyNO","")
        bxgs = request.REQUEST.get("bxgs","")
        DB = BXDBAction()
        DG = DB.GetPolicyNo(PolicyNO=PolicyNO,bxgs=bxgs)
        print(DG)
        print(type(DG))
        J = KLBPrint.echo(msg="数据返回", data=DG, error=0)
        return HttpResponse(J, content_type="application/json")
    else:
        RE = {'error':'1'}
        J = KLBPrint.echo(msg="数据返回", data=RE, error=0)
        return HttpResponse(J, content_type="application/json")
# 判断数据库中是否有用户信息
def VINIsSet(request):
    KLBPrint = PrintJson()
    licenseNo = request.REQUEST.get("licenseNo", "")
    cityCode = request.REQUEST.get("cityCode", "")
    ownerName = request.REQUEST.get("ownerName", "")
    DBAction = BXDBAction()
    IsTure = DBAction.IsSet(licenseno=licenseNo, citycode=cityCode, ownername=ownerName)
    if IsTure:
        R = KLBPrint.echo(msg="数据返回", data=IsTure, error=0)
    else:
        R = KLBPrint.echo(msg="没有找到", data={}, error=1)
    return HttpResponse(R)

def GetVIN(request):
    # 初始化加密解密类
    ENCODE = FengChaoCrypt()

    licenseNo = str(request.REQUEST.get("licenseNo", "")).encode("utf-8")
    cityCode = str(request.REQUEST.get("cityCode", "")).encode("utf-8")
    ownerName = str(request.REQUEST.get("ownerName", "")).encode("utf-8")
    db = {"licenseNo": ENCODE.AESencrypt(licenseNo), "ownerName": ENCODE.AESencrypt(ownerName),
          "cityCode": ENCODE.AESencrypt(cityCode)}

    KLBPrint = PrintJson()
    # 获取北京地区的车牌号码VIN和发动机号


    if request.method == "POST":

        try:
            action = Yo(licenseNo, ownerName)
            err, vin, engine = action.sure()
            db.update({"vin_noen": vin, "vin": ENCODE.AESencrypt(vin), "engine": ENCODE.AESencrypt(engine)})
            BDBAction = BXDBAction()
            BDBAction.CreateCarVin(**db)
            R = KLBPrint.echo(msg="数据返回", data=db, error=0)

        except:
            R = KLBPrint.echo(msg="未获得VIN", data=db, error=1)
        return HttpResponse(R)
    else:
        R = KLBPrint.echo(msg="未获得VIN", data={}, error=1)
        return HttpResponse(R)
# 返回各个保险公司价格
def PriceList(request):
    # 获取保险公司名字
    '''
    company='as' 安盛
    company='yg' 阳光
    company='zh' 中华
    '''
    DBAction = BXDBAction()
    # 初始化转换json格式类
    KLBJSON = PrintJson()
    id = request.REQUEST.get("id", "")
    company = request.REQUEST.get("company", "")
    # 用户ID
    user_id = request.user.is_authenticated() and request.user.id or False
    # 行驶城市
    drivCity = request.REQUEST.get("drivCity","")

    # 如果数据库存在该车主信息，直接读取数据库内容
    if id and id <> "":
        CarIn = DBAction.IsSet(id=id)
        CarCon = DBAction.ReCarInfo(cid=id)
        licenseNo = CarIn.licenseno
        ownerName = CarIn.ownername
        vin = CarIn.vin
        engine = CarIn.engine
        cityCode = CarIn.citycode
        if CarCon:
            key = CarCon['key']
            vehicleFgwCode = CarCon['vehiclefgwcode']
            carvalue = CarCon['value']
        else:
            key = unquote(request.REQUEST.get("carkey", ""))
            vehicleFgwCode = unquote(request.REQUEST.get("vehiclefgwcode", ""))
            carvalue = unquote(request.REQUEST.get("value", ""))

    # 如果数据库没有查到该车的信息,则接收用户输入的值
    else:

        # 初始化加密解密类
        ENCODE = FengChaoCrypt()

        # 车牌号
        licenseNo = ENCODE.AESdecrypt(request.REQUEST.get("licenseno", ""))
        # 车主姓名
        ownerName = ENCODE.AESdecrypt(str(request.REQUEST.get("ownername", "")))
        # 手机号码
        mobilePhone = request.REQUEST.get("mobilephone", "")
        # 城市
        cityCode = ENCODE.AESdecrypt(request.REQUEST.get("citycode", ""))
        # 车主身份证
        # idCode = ENCODE.AESdecrypt(request.REQUEST.get("idcode", ""))


        # vin
        vin = request.REQUEST.get("vin", "")
        # 发动机号
        engine = request.REQUEST.get("engine", "")

        # 如果用户直接通过系统获取到VIN和发动机号，action＝"a"用户手动输入action则为b
        action = request.REQUEST.get("a", "")
        # 这三个是用户选择的阳光的车型信息
        key = unquote(request.REQUEST.get("carkey", ""))
        vehicleFgwCode = unquote(request.REQUEST.get("vehiclefgwcode", ""))
        carvalue = unquote(request.REQUEST.get("value", ""))

        # 如果action为a，需要对vin和发动机号进行解密
        if action == "a":
            vin = ENCODE.AESdecrypt(vin)
            engine = ENCODE.AESdecrypt(engine)
    # #第三方存入数据库的车型
    # if id=="" or id==None:
    #     NewDBAction = BXDBAction()
    #     CarID = NewDBAction.CreateCarVin(user_id=user_id,licenseno=licenseNo,ownername=ownerName,citycode=cityCode,vin=vin,engine=engine)
    #     NewDBAction.CreateCarInfo(user_id=user_id,car_id=CarID,key=key,vehiclefgwcode=vehicleFgwCode,value=carvalue,bxtype="sinosig")

    # 调用保险公司接口


    # 这里开始调用各个保险公司的类
    changbx = request.REQUEST.get("chang", "")

    CHESHUN = request.REQUEST.get("CHESHUN", "")
    SANZHE = request.REQUEST.get("SANZHE", "")
    DAOQIANG = request.REQUEST.get("DAOQIANG", "")
    SHIJI = request.REQUEST.get("SHIJI", "")
    CHENGKE = request.REQUEST.get("CHENGKE", "")
    BOLI = request.REQUEST.get("BOLI", "")
    HUAHEN = request.REQUEST.get("HUAHEN", "")
    ZIRAN = request.REQUEST.get("ZIRAN", "")
    SHESHUI = request.REQUEST.get("SHESHUI", "")
    CHESHUN_BJ = request.REQUEST.get("CHESHUN_BJ", "")
    SANZHE_BJ = request.REQUEST.get("SANZHE_BJ", "")
    DAOQIANG_BJ = request.REQUEST.get("DAOQIANG_BJ", "")
    SHIJI_BJ = request.REQUEST.get("SHIJI_BJ", "")
    CHENGKE_BJ = request.REQUEST.get("CHENGKE_BJ", "")
    FUJIA_BJ = request.REQUEST.get("FUJIA_BJ", "")
    JIAOQIANG = request.REQUEST.get("JIAOQIANG", "")
    DictIn = {
        "CHESHUN": (CHESHUN == None or CHESHUN == "") and "0" or CHESHUN,
        "SANZHE": (SANZHE == None or SANZHE == "") and "0" or SANZHE,
        "DAOQIANG": (DAOQIANG == None or DAOQIANG == "") and "0" or DAOQIANG,
        'SHIJI': (SHIJI == None or SHIJI == "") and "0" or SHIJI,
        "CHENGKE": (CHENGKE == None or CHENGKE == "") and "0" or CHENGKE,
        "BOLI": (BOLI == None or BOLI == "") and "0" or BOLI,
        "HUAHEN": (HUAHEN == None or HUAHEN == "") and "0" or HUAHEN,
        "ZIRAN": (ZIRAN == None or ZIRAN == "") and "0" or ZIRAN,
        "SHESHUI": (SHESHUI == None or SHESHUI == "") and "0" or SHESHUI,
        "CHESHUN_BJ": (CHESHUN_BJ == None or CHESHUN_BJ == "") and "0" or CHESHUN_BJ,
        "SANZHE_BJ": (SANZHE_BJ == None or SANZHE_BJ == "") and "0" or SANZHE_BJ,
        "DAOQIANG_BJ": (DAOQIANG_BJ == None or DAOQIANG_BJ == "") and "0" or DAOQIANG_BJ,
        "SHIJI_BJ": (SHIJI_BJ == None or SHIJI_BJ == "") and "0" or SHIJI_BJ,
        "CHENGKE_BJ": (CHENGKE_BJ == None or CHENGKE_BJ == "") and "0" or CHENGKE_BJ,
        "FUJIA_BJ": (FUJIA_BJ == None or FUJIA_BJ == "") and "0" or FUJIA_BJ,
        "JIAOQIANG": (JIAOQIANG == None or JIAOQIANG == "") and "0" or JIAOQIANG,
    }
    if company == "as":
        AS = AnSheng(cityCode=cityCode, licenseNo=licenseNo, ownerName=ownerName, mobilePhone='', engine=engine,
                     vin=vin, user_id=user_id)
        if changbx == '1':
            ErrorMessage, REDICT, X = AS.Get_110(**DictIn)
        else:
            ErrorMessage, REDICT, X = AS.Get_110(CHESHUN="1", SANZHE='50000', DAOQIANG='0', SHIJI='10000', CHENGKE='10000', BOLI='0',
                JIAOQIANG='1', ZIRAN='0', HUAHEN='0', SHESHUI='0', CHESHUN_BJ='0', SANZHE_BJ='0', DAOQIANG_BJ='0',
                SHIJI_BJ='0', CHENGKE_BJ='0', FUJIA_BJ='0')
        J = KLBJSON.echo(msg="数据返回", error=0, data=REDICT)
        return HttpResponse(J, content_type="application/json")

    if company == "zh":

        ZH = ZhongHuaAction(citycode=cityCode, licenseNo=licenseNo, ownerName=ownerName, vin=vin, engineNo=engine,
                            user_id=user_id)

        if changbx == "1":
            ERR, ORDER, REDICT, RE, JinBaoMsg = ZH.Get_1033(**DictIn)
        else:

            ERR, ORDER, REDICT, RE, JinBaoMsg = ZH.Get_1033(CHESHUN='1', SANZHE='50000', SHIJI='10000',
                                                            CHENGKE='10000',
                                                            DAOQIANG='0', ZIRAN='0', BOLI='0', DAOQIANG_BJ='0',
                                                            CHESHUN_BJ='0',
                                                            SANZHE_BJ='0', SHIJI_BJ='0', CHENGKE_BJ='0', HUAHEN='0',
                                                            SHESHUI='0',
                                                            FUJIA_BJ='0', JIAOQIANG='1')

        J = KLBJSON.echo(msg="数据返回", error=0, data=REDICT)
        return HttpResponse(J, content_type="application/json")
    if company == "yg":
        YG = YangGuang(cityCode=cityCode,licenseNo=licenseNo,ownerName=ownerName,vin=vin,engine=engine,mobilePhone="",user_id="",drivCity=drivCity)
        if changbx == "1":
            Result,REDICT,ErrorMessage= YG.Get_110(**DictIn)
        else:
            Result,REDICT,ErrorMessage = YG.Get_110(CHESHUN='1', SANZHE='50000', SHIJI='10000',CHENGKE='10000',
                                                    DAOQIANG='0', ZIRAN='0', BOLI='0', DAOQIANG_BJ='0',CHESHUN_BJ='0',
                                                    SANZHE_BJ='0', SHIJI_BJ='0', CHENGKE_BJ='0', HUAHEN='0',
                                                    SHESHUI='0',FUJIA_BJ='0', JIAOQIANG='1')
        J = KLBJSON.echo(msg="数据返回", error=0, data=REDICT)
        return HttpResponse(J, content_type="application/json")

# 手动建立vin存进数据库
def CerateCarVin(request):

    KLBJSON = PrintJson()
    DBAction = BXDBAction()
    ENCODE = FengChaoCrypt()
    user_id = request.user.is_authenticated() and request.user.id or False
    key = unquote(request.REQUEST.get("key", ""))
    vehicleFgwCode = unquote(request.REQUEST.get("vehiclefgwcode", ""))
    carvalue = unquote(request.REQUEST.get("value", ""))
    vin = request.REQUEST.get("vin", "")
    engine = request.REQUEST.get("engine", "")

    # 车牌号
    licenseNo = ENCODE.AESdecrypt(request.REQUEST.get("licenseno", ""))
    # 车主姓名
    ownerName = ENCODE.AESdecrypt(request.REQUEST.get("ownername", ""))
    # 城市
    cityCode = ENCODE.AESdecrypt(request.REQUEST.get("citycode", ""))
    action = request.REQUEST.get("a", "")
    if action == "a":
        vin = ENCODE.AESdecrypt(vin)
        engine = ENCODE.AESdecrypt(engine)

    if bxcarvin.objects.filter(vin=vin, engine=engine).count() < 1:
        kwargs = {
            "licenseno": licenseNo,
            "ownername": ownerName,
            "citycode": cityCode,
            "vin": vin,
            "engine": engine,
            "user_id": user_id
        }
        CarID = DBAction.CreateCarVin(**kwargs)
        '''
        将阳光返回的车型存入数据库
        '''
        kwargs = {
            'user_id': user_id,
            "car_id": CarID,
            "key": key,
            "vehiclefgwcode": vehicleFgwCode,
            "value": carvalue,
            "bxtype": "sinosig",
        }
        DBAction.CreateCarInfo(**kwargs)
    else:
        pass

    J = KLBJSON.echo(msg="数据返回", error=0, data={})
    return HttpResponse(J, content_type="application/json")


def TestZhongHua(request):
    from bxservice.ZhongHuaAction import ZhongHuaAction
    from bxservice.ansheng import AnSheng
    from bxservice.yangguang import YangGuang
    if request.method == "POST":
        citycode = request.REQUEST.get("citycode", "")
        licenseNo = request.REQUEST.get("licenseNo", "")
        ownerName = request.REQUEST.get("ownerName", "")
        vin = request.REQUEST.get("vin", "")
        engineNo = request.REQUEST.get("engineNo", "")
        xml = request.REQUEST.get("xml", "")
        action = request.REQUEST.get("action", "")

        if action == "1030":
            InDict = {"citycode": citycode, "licenseNo": licenseNo, "ownerName": ownerName, "vin": vin,
                      "engineNo": engineNo}
            ZH = ZhongHuaAction(**InDict)
            CONT1030 = ZH.Get_1030()
            return HttpResponse(CONT1030, content_type="application/xml")
        if action == "1031":
            InDict = {"citycode": citycode, "licenseNo": licenseNo, "ownerName": ownerName, "vin": vin,
                      "engineNo": engineNo}
            ZH = ZhongHuaAction(**InDict)
            ERR, CarInfo, CONT1030 = ZH.Get_1031()
            return HttpResponse(CONT1030, content_type="application/xml")
        if action == "1032":
            InDict = {"citycode": citycode, "licenseNo": licenseNo, "ownerName": ownerName, "vin": vin,
                      "engineNo": engineNo}
            ZH = ZhongHuaAction(**InDict)
            ERR, ORDER, RELIST, CONT1032 = ZH.Get_1032()

            return HttpResponse(CONT1032, content_type="application/xml")
        if action == "1033":
            InDict = {"citycode": citycode, "licenseNo": licenseNo, "ownerName": ownerName, "vin": vin,
                      "engineNo": "036018"}
            ZH = ZhongHuaAction(**InDict)
            ERR, ORDER, REDICT, RE,JinBaoMsg = ZH.Get_1033()

            return HttpResponse(RE, content_type="application/xml")
        if action == '1036':
            ZH = ZhongHuaAction()
            ZH.Get_1036()
        if action == '1039':
            ZH = ZhongHuaAction()
            RE = ZH.CallBack(xml=xml)
            return HttpResponse(RE, content_type="application/xml")
        if action == '1':
            AS = AnSheng()
            RE = AS.CallBack(xml=xml)
            return HttpResponse(RE, content_type="application/xml")

        if action == "2":
            Y = YangGuang(cityCode=citycode,licenseNo=licenseNo,ownerName=ownerName,vin=vin,engine=engineNo,mobilePhone="",user_id="")
            Result,REDICT,ErrorMessage = Y.Get_110()
            return HttpResponse(Result, content_type="application/xml")
        if action == "3":
            Y = YangGuang()
            RE = Y.CallBack(xml=xml)
            return HttpResponse(RE, content_type="application/xml")
        if action == '4':
            ZH = ZhongHuaAction()
            flag = request.REQUEST.get('flag','')
            orderno = request.REQUEST.get("orderno",'')
            businessCode = request.REQUEST.get("businessCode",'')
            RE = ZH.IsRead(flag=flag,orderno=orderno,businessCode=businessCode)
            return HttpResponse(RE)
        if action == '11':
            DB = BXDBAction()
            DG  = DB.GetPolicyNo(PolicyNO='12345',bxgs='as')
            print (type(DG))
            print(DG)
            return HttpResponse(DG)
    else:
        return render_to_response('web/TestZhongHua.html', {}, context_instance=RequestContext(request))

def ConfirmTouBao(request):
    '''
    提交投保信息
    :param request:
    :return:
    '''

    # 输出json
    KLBJSON = PrintJson()
    agent = request.META.get('HTTP_USER_AGENT',"")
    bxgs = request.REQUEST.get("bxgs", "")
    Session_ID = request.REQUEST.get("Session_ID", "")
    ORDER_ID = request.REQUEST.get("ORDER_ID", "")
    C_APP_NAME = request.REQUEST.get("C_APP_NAME", "")
    C_APP_IDENT_NO = request.REQUEST.get("C_APP_IDENT_NO", "")
    C_APP_TEL = request.REQUEST.get("C_APP_TEL", "")
    C_APP_ADDR = request.REQUEST.get("C_APP_ADDR", "")
    C_APP_EMAIL = request.REQUEST.get("C_APP_EMAIL", "")
    C_INSRNT_NME = request.REQUEST.get("C_INSRNT_NME", "")
    C_INSRNT_IDENT_NO = request.REQUEST.get("C_INSRNT_IDENT_NO", "")
    C_INSRNT_TEL = request.REQUEST.get("C_INSRNT_TEL", "")
    C_INSRNT_ADDR = request.REQUEST.get("C_INSRNT_ADDR", "")
    C_INSRNT_EMAIL = request.REQUEST.get("C_INSRNT_EMAIL", "")
    C_CONTACT_NAME = request.REQUEST.get("C_CONTACT_NAME", "")
    C_CONTACT_TEL = request.REQUEST.get("C_CONTACT_TEL", "")
    C_ADDRESS = request.REQUEST.get("C_ADDRESS", "")
    C_IDET_NAME = request.REQUEST.get("C_IDET_NAME", "")
    C_IDENT_NO = request.REQUEST.get("C_IDENT_NO", "")
    C_DELIVERY_PROVINCE = request.REQUEST.get("C_DELIVERY_PROVINCE", "")
    C_DELIVERY_CITY = request.REQUEST.get("C_DELIVERY_CITY", "")
    C_DELIVERY_DISTRICT = request.REQUEST.get("C_DELIVERY_DISTRICT", "")
    vin = request.REQUEST.get("vin", "")
    # 判断是否为移动端
    INFO = request.REQUEST.items()
    Ister = IsTerminal(agent=agent)
    IsterInfo = Ister.IsTer()
    # IsNull = Ister.IsNull(INFO=INFO)
    # if IsNull:
    #     REDICT={'error':'1','msg':"请输入正确信息"}
    #     URL = ''
    #     J = KLBJSON.echo(msg="数据返回", error=0, url=URL, data=REDICT)
    #     return  HttpResponse(J, content_type="application/json")
    if bxgs == "zh":
        Session_ID = request.REQUEST.get("Session_ID", "")
        ORDER_ID = request.REQUEST.get("ORDER_ID", "")
        C_APP_NAME = request.REQUEST.get("C_APP_NAME", "")
        C_APP_IDENT_NO = request.REQUEST.get("C_APP_IDENT_NO", "")
        C_APP_TEL = request.REQUEST.get("C_APP_TEL", "")
        C_APP_ADDR = request.REQUEST.get("C_APP_ADDR", "")
        C_APP_EMAIL = request.REQUEST.get("C_APP_EMAIL", "")
        C_INSRNT_NME = request.REQUEST.get("C_INSRNT_NME", "")
        C_INSRNT_IDENT_NO = request.REQUEST.get("C_INSRNT_IDENT_NO", "")
        C_INSRNT_TEL = request.REQUEST.get("C_INSRNT_TEL", "")
        C_INSRNT_ADDR = request.REQUEST.get("C_INSRNT_ADDR", "")
        C_INSRNT_EMAIL = request.REQUEST.get("C_INSRNT_EMAIL", "")
        C_CONTACT_NAME = request.REQUEST.get("C_CONTACT_NAME", "")
        C_ADDRESS = request.REQUEST.get("C_ADDRESS", "")
        C_IDET_NAME = request.REQUEST.get("C_IDET_NAME", "")
        C_IDENT_NO = request.REQUEST.get("C_IDENT_NO", "")
        C_DELIVERY_PROVINCE = request.REQUEST.get("C_DELIVERY_PROVINCE", "")
        C_DELIVERY_CITY = request.REQUEST.get("C_DELIVERY_CITY", "")
        C_DELIVERY_DISTRICT = request.REQUEST.get("C_DELIVERY_DISTRICT", "")
        vin = request.REQUEST.get("vin", "")

        REDICT = {"Session_ID": Session_ID,
                  "ORDER_ID": ORDER_ID,
                  "vin": vin,
                  "C_APP_NAME": C_APP_NAME,  # 投保人姓名
                  "C_APP_IDENT_NO": C_APP_IDENT_NO,  # 投保人证件号码
                  "C_APP_TEL": C_APP_TEL,  # 投保人电话
                  "C_APP_ADDR": C_APP_ADDR,  # 投保人地址
                  "C_APP_EMAIL": C_APP_EMAIL,  # 投保人邮箱
                  "C_INSRNT_NME": C_INSRNT_NME,  # 被保险人姓名
                  "C_INSRNT_IDENT_NO": C_INSRNT_IDENT_NO,  # 被保险人证件号码
                  "C_INSRNT_TEL": C_INSRNT_TEL,  # 被保险人电话
                  "C_INSRNT_ADDR": C_INSRNT_ADDR,  # 被保险人地址
                  "C_INSRNT_EMAIL": C_INSRNT_EMAIL,  # 被保险人邮箱
                  "C_DELIVERY_PROVINCE": C_DELIVERY_PROVINCE,  # 配送地址省代码
                  "C_DELIVERY_CITY": C_DELIVERY_CITY,  # 配送地址市代码
                  "C_DELIVERY_DISTRICT": C_DELIVERY_DISTRICT,  # 区代码
                  "C_CONTACT_NAME": C_CONTACT_NAME,
                  "C_CONTACT_TEL": C_CONTACT_TEL,
                  "C_ADDRESS": C_ADDRESS,  # 收件地址
                  "C_IDET_NAME": C_IDET_NAME,  # 车主姓名
                  "C_IDENT_NO": C_IDENT_NO,  # 身份证号
                  "IsterInfo":IsterInfo
                  }

        ZH = ZhongHuaAction()
        ERR, REDICT, PAY_URL = ZH.Get_1038(**REDICT)
        J = KLBJSON.echo(msg="数据返回", error=0, url=PAY_URL, data=REDICT)
        return HttpResponse(J, content_type="application/json")
    if bxgs == "as":
        REDICT = {
            "vin": vin,
            "applicantname": C_APP_NAME,  # 投保人姓名
            "applicantidno": C_APP_IDENT_NO,  # 投保人证件号码
            "applicantmobile": C_APP_TEL,  # 投保人电话
            # "C_APP_ADDR": C_APP_ADDR,  # 投保人地址
            "applicantemail": C_APP_EMAIL,  # 投保人邮箱
            "insuredname": C_INSRNT_NME,  # 被保险人姓名
            "insuredidno": C_INSRNT_IDENT_NO,  # 被保险人证件号码
            "insuredmobile": C_INSRNT_TEL,  # 被保险人电话
            # "C_INSRNT_ADDR": C_INSRNT_ADDR,  # 被保险人地址
            # "C_INSRNT_EMAIL": C_INSRNT_EMAIL,  # 被保险人邮箱
            "addresseeprovince": C_DELIVERY_PROVINCE,  # 配送地址省代码
            "addresseecity": C_DELIVERY_CITY,  # 配送地址市代码
            "addresseetown": C_DELIVERY_DISTRICT,  # 区代码
            "addresseename": C_CONTACT_NAME,
            "addresseemobile": C_CONTACT_TEL,
            "addresseedetails": C_ADDRESS,  # 收件地址
            "ownername": C_INSRNT_NME,  # 车主姓名
            "owneridno": C_INSRNT_IDENT_NO,  # 身份证号
            "IsterInfo": IsterInfo
        }
        AS = AnSheng()
        X, REDICT, ErrorMessage, PayUrl = AS.Get_115(**REDICT)
        J = KLBJSON.echo(msg="数据返回", error=0, url=PayUrl, data=REDICT)
        return HttpResponse(J, content_type="application/json")
    if bxgs == "yg":
        REDICT = {
            "vin": vin,
            "applicantname": C_APP_NAME,  # 投保人姓名
            "applicantidno": C_APP_IDENT_NO,  # 投保人证件号码
            "applicantmobile": C_APP_TEL,  # 投保人电话
            # "C_APP_ADDR": C_APP_ADDR,  # 投保人地址
            "applicantemail": C_APP_EMAIL,  # 投保人邮箱
            "insuredname": C_INSRNT_NME,  # 被保险人姓名
            "insuredidno": C_INSRNT_IDENT_NO,  # 被保险人证件号码
            "insuredmobile": C_INSRNT_TEL,  # 被保险人电话
            "insuredaddresseeDetails": C_INSRNT_ADDR,  # 被保险人地址
            "insuredEmail": C_INSRNT_EMAIL,  # 被保险人邮箱
            "addresseeprovince": C_DELIVERY_PROVINCE,  # 配送地址省代码
            "addresseecity": C_DELIVERY_CITY,  # 配送地址市代码
            "addresseetown": C_DELIVERY_DISTRICT,  # 区代码
            "addresseename": C_CONTACT_NAME,
            "addresseemobile": C_CONTACT_TEL,
            "addresseedetails": C_ADDRESS,  # 收件地址
            "ownername": C_INSRNT_NME,  # 车主姓名
            "owneridno": C_INSRNT_IDENT_NO,  # 身份证号
            "IsterInfo":IsterInfo
        }
        Verify = request.REQUEST.get("Verify","")
        YG = YangGuang()
        if Verify <> "":
            Result,REDICT,URL,ErrorMessage = YG.Get_126(vin=vin,ownername=C_INSRNT_NME,IsterInfo=IsterInfo,Verify=Verify)
        else:
            Result,REDICT,URL,ErrorMessage = YG.Get_120(**REDICT)
        J = KLBJSON.echo(msg="数据返回",url=URL,error=0,  data=REDICT)
        return HttpResponse(J, content_type="application/json")
    J = KLBJSON.echo(msg="数据返回", error=0)


    return HttpResponse(J, content_type="application/json")
