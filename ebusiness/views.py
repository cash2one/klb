# -*- coding:utf-8 -*-
from django.shortcuts import *
from ebusiness.forms import initVehicleBaseInfoForm,EditInfoForm
from LYZ.klb_class import KLBCode,PingAn,GetCarVin,UrlCode,KLBOAuth
from ebusiness.models import vin_as_car_yg
from bxservice.ZhongHuaAction import *
from bxservice.ansheng import *
from bxservice.yangguang import *
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
import re

'''
$名称:录入车辆信息
$参数:
'''

def initVehicleBaseInfo(request):
    TempDict = {}
    Code = KLBCode()
    #获取设定样式
    style = request.REQUEST.get("style","")
    #获取渠道码
    sn = request.REQUEST.get("sn","")
    urldata = dict(request.GET.items())
    #判断提交方式
    if request.method == "POST":
        URL = UrlCode()
        initForms = initVehicleBaseInfoForm(request.POST)
        if initForms.is_valid():
            #如果数据存在数据库，就直接取出车辆I，跳转比价
            IsSet = initForms.IsSet()
            if IsSet:
                car = Code.encode(str(IsSet['id']))
                urldata.update({"car":car})
                GoUrl = "/ebusiness/initQuotation/?"+URL.Encode(urldata)
                return HttpResponsePermanentRedirect(GoUrl)
            #如果不存在，获取城市编码
            else:
                CarInfoList = initForms.GetCarInfo()
                cityCode = initForms.GetCityCode()#获取城市编码
                if cityCode == "":
                    TempDict.update({"licenseNo_error":"车牌号码不正确或该地区暂不支持"})
                elif CarInfoList:
                    cityCode = (cityCode=="") and cityCode or Code.encode(str(cityCode))
                    ownerName = Code.encode(str(initForms.cleaned_data["ownerName"]))#车主姓名
                    licenseNo = Code.encode(str(initForms.cleaned_data["licenseNo"]))#车牌号码
                    engine = Code.encode(str(initForms.cleaned_data["engine"]))#车牌号码
                    vin = Code.encode(str(initForms.cleaned_data["vin"]))#车架号
                    InDB = {
                        "CarList":CarInfoList,
                        "cityCode":cityCode,
                        "ownerName":ownerName,
                        "licenseNo":licenseNo,
                        "engine":engine,
                        "vin":vin,
                        "style":style,
                        "sn":sn
                    }

                    TempDict.update(InDB)
                    return render_to_response('ebusiness/selectCarList.html', TempDict, context_instance=RequestContext(request))
                else:
                    TempDict.update({"vin_error":"车架号不正确，请更换车架号重试！"})


        TempDict.update({"forms":initForms})
    else:
        initForms = initVehicleBaseInfoForm()
        TempDict.update({"forms":initForms})
    return render_to_response('ebusiness/initVehicleBaseInfo.html', TempDict, context_instance=RequestContext(request))


'''
$名称:选择车辆品牌型号
$参数:
'''

def selectCerList(request):
    from bxservice.common import BXDBAction
    KCode = KLBCode()
    DBAction = BXDBAction()
    URL = UrlCode()
    style = request.REQUEST.get("style","")#样式
    cityCode = request.REQUEST.get("cityCode","")#城市代码
    sn = request.REQUEST.get("sn","")#渠道代码
    ownerName = request.REQUEST.get("ownerName","")#车主姓名
    licenseNo = request.REQUEST.get("licenseNo","")#车牌号码
    engine = request.REQUEST.get("engine","")#发动机号
    vin = request.REQUEST.get("vin","")#车架号
    car = request.REQUEST.get("car","")#车辆code
    href = request.REQUEST.get("href","")#来源地址
    urldata = {
        "style":style,
        "sn":sn,
    }
    if request.method == "POST":
        kwargs = {
            "licenseno": KCode.decode(licenseNo),
            "ownername": KCode.decode(ownerName),
            "citycode": KCode.decode(cityCode),
            "vin": KCode.decode(vin),
            "engine": KCode.decode(engine),
            "user_id": ""
        }
        CarID = DBAction.CreateCarVin(**kwargs)
        getCar = vin_as_car_yg.objects.get(id=KCode.decode(car))
        kwargs = {
            'user_id': "",
            "car_id": CarID,
            "key": getCar.key,
            "vehiclefgwcode": getCar.vehicleFgwCode,
            "value": getCar.value,
            "bxtype": "sinosig",
        }
        DBAction.CreateCarInfo(**kwargs)
        CarID =  KCode.encode(str(CarID))
        urldata.update({"car":CarID})
        GoUrl = "/ebusiness/initQuotation/?"+URL.Encode(urldata)
        return HttpResponsePermanentRedirect(GoUrl)
    else:
        return HttpResponse("<script>window.history.go(-1);</script>")
'''
$名称:保费试算
$参数:
'''

def initQuotation(request):
    KCode = KLBCode()
    URL = UrlCode()
    TempDictArr = dict(request.REQUEST.items())
    car = TempDictArr.get("car","")#车辆code
    style = TempDictArr.get("style","")#样式
    sn = TempDictArr.get("sn","")#渠道代码
    if car=="" or car ==None:
        return HttpResponsePermanentRedirect("/ebusiness/?%s"%URL.Encode(TempDictArr))
    TempDict = {"id":KCode.decode(str(car)),"style":style,"sn":sn}
    return render_to_response('ebusiness/initQuotation1.html', TempDict, context_instance=RequestContext(request))

'''
$名称:填写投保资料
$参数:
'''

def editInfo(request):
    KCode = KLBCode()
    TempDict = {}
    company = request.REQUEST.get("company","")#保险公司
    id = request.REQUEST.get("car","")#车辆ID
    sn = request.REQUEST.get("sn","")
    CarInfo = bxcarvin.objects.get(id=KCode.decode(str(id)))
    revin = KCode.encode(CarInfo.vin)
    editForms = EditInfoForm()
    bxgs = KCode.decode(str(company))
    if bxgs == "zh":
        if id <> "" and id <> None:
            PayInfo =CarInfo.bxpayinfo_set.values()[0]
            # 确认浮动告知单
            Confirm = ConfirmRate(Order_id=PayInfo['order_id'])
            Confirm.Confirm(M='11')
            Confirm.Confirm(M='12')
            TempDict.update({"PayInfo": PayInfo})
            TempDict.update({"company": "zh","sn":sn, "openwin": "1", "orderNo": PayInfo['order_id'],
                             "businessCode": PayInfo['businesscode'], "vin": revin})
    if bxgs == "as":
        TempDict.update({"bxgs": "as", "openwin": "","sn":sn, "vin": revin})
    if bxgs == "yg":
        TempDict.update({"bxgs": "yg", "openwin": "","sn":sn, "vin": revin})
    TempDict.update({"forms": editForms})
    TempDict.update({'id': id})
    return render_to_response('ebusiness/editInfo.html', TempDict, context_instance=RequestContext(request))
def ConfirmInsure(request):
    '''向保险公司提交投保信息
        company = 'as'
        company = 'zh'
        company = 'yg'
    '''
    KCode = KLBCode()
    TempDict ={}
    agent = request.META.get('HTTP_USER_AGENT',"")
    bxgs = request.REQUEST.get("company","")
    id = request.REQUEST.get("id","")
    C_APP_NAME = request.REQUEST.get("C_APP_NAME","")
    C_APP_IDENT_NO = request.REQUEST.get("C_APP_IDENT_NO","")
    C_APP_TEL = request.REQUEST.get("C_APP_TEL","")
    C_APP_ADDR = request.REQUEST.get("C_APP_ADDR","")
    C_APP_EMAIL = request.REQUEST.get("C_APP_EMAIL","")
    C_CONTACT_TEL = request.REQUEST.get("C_CONTACT_TEL","")
    C_CONTACT_NAME = request.REQUEST.get("C_CONTACT_NAME","")
    C_ADDRESS = request.REQUEST.get("C_ADDRESS","")
    vin = request.REQUEST.get("vin", "")
    Session_ID = request.REQUEST.get("Session_ID", "")
    ORDER_ID = request.REQUEST.get("ORDER_ID", "")
    Verify = request.REQUEST.get("yzm","")
    # 判断是否为移动端
    Ister = IsTerminal(agent=agent)
    IsterInfo = Ister.IsTer()
    VinNew =  KCode.decode(vin)
    bxgs = KCode.decode(str(bxgs))
    ID = KCode.decode(id)
    if request.method == "POST":
        if request.REQUEST.get("action",'') == 'yzm':
            YG = YangGuang()
            if Verify <> "":
                Result, REDICT, PAY_URL, ErrorMessage = YG.Get_126(vin=VinNew,ownername=KCode.decode(C_APP_NAME), IsterInfo=IsterInfo, Verify=Verify,ID=ID)
                if not REDICT.has_key('error') :
                    TempDict.update({"URL":PAY_URL})
                    return HttpResponsePermanentRedirect(PAY_URL)
                else:
                    return render_to_response('ebusiness/error.html')
            else:
                TempDict.update({"yzm":"1"})
                TempDict.update({"company":'yg',"vin":vin})
                return render_to_response('ebusiness/editInfo.html', TempDict,
                                      context_instance=RequestContext(request))
        editForms = EditInfoForm(request.POST)
        if editForms.is_valid():
            if bxgs == "zh":
                REDICT = {"Session_ID": KCode.decode(str(Session_ID)),
                          "ORDER_ID": KCode.decode(str(ORDER_ID)),
                          "vin": VinNew,
                          "C_APP_NAME": C_APP_NAME,  # 投保人姓名
                          "C_APP_IDENT_NO": C_APP_IDENT_NO,  # 投保人证件号码
                          "C_APP_TEL": C_APP_TEL,  # 投保人电话
                          "C_APP_ADDR": C_APP_ADDR,  # 投保人地址
                          "C_APP_EMAIL": C_APP_EMAIL,  # 投保人邮箱
                          "C_INSRNT_NME": C_APP_NAME,  # 被保险人姓名
                          "C_INSRNT_IDENT_NO": C_APP_IDENT_NO,  # 被保险人证件号码
                          "C_INSRNT_TEL": C_APP_TEL,  # 被保险人电话
                          "C_INSRNT_ADDR": C_APP_ADDR,  # 被保险人地址
                          "C_INSRNT_EMAIL": C_APP_EMAIL,  # 被保险人邮箱
                          "C_DELIVERY_PROVINCE": "",  # 配送地址省代码
                          "C_DELIVERY_CITY": "",  # 配送地址市代码
                          "C_DELIVERY_DISTRICT": "",  # 区代码
                          "C_CONTACT_NAME": C_CONTACT_NAME,
                          "C_CONTACT_TEL": C_CONTACT_TEL,
                          "C_ADDRESS": C_ADDRESS,  # 收件地址
                          "C_IDET_NAME": C_APP_NAME,  # 车主姓名
                          "C_IDENT_NO": C_APP_IDENT_NO,  # 身份证号
                          "IsterInfo": IsterInfo,
                          "ID":ID
                          }
                ZH = ZhongHuaAction()
                ERR, REDICT, PAY_URL = ZH.Get_1038(**REDICT)
            if bxgs == "as":
                REDICT = {
                    "vin": VinNew,
                    "applicantname": C_APP_NAME,  # 投保人姓名
                    "applicantidno": C_APP_IDENT_NO,  # 投保人证件号码
                    "applicantmobile": C_APP_TEL,  # 投保人电话
                    # "C_APP_ADDR": C_APP_ADDR,  # 投保人地址
                    "applicantemail": C_APP_EMAIL,  # 投保人邮箱
                    "insuredname": C_APP_NAME,  # 被保险人姓名
                    "insuredidno": C_APP_IDENT_NO,  # 被保险人证件号码
                    "insuredmobile": C_APP_TEL,  # 被保险人电话
                    # "C_INSRNT_ADDR": C_INSRNT_ADDR,  # 被保险人地址
                    # "C_INSRNT_EMAIL": C_INSRNT_EMAIL,  # 被保险人邮箱
                    "addresseeprovince": "",  # 配送地址省代码
                    "addresseecity": "",  # 配送地址市代码
                    "addresseetown": "",  # 区代码
                    "addresseename": C_CONTACT_NAME,
                    "addresseemobile": C_CONTACT_TEL,
                    "addresseedetails": C_ADDRESS,  # 收件地址
                    "ownername": C_APP_NAME,  # 车主姓名
                    "owneridno": C_APP_IDENT_NO,  # 身份证号
                    "IsterInfo": IsterInfo,
                    "ID":ID
                }
                AS = AnSheng()
                X, REDICT, ErrorMessage, PAY_URL = AS.Get_115(**REDICT)
            if bxgs == "yg":
                REDICT = {
                    "vin": VinNew,
                    "applicantname": C_APP_NAME,  # 投保人姓名
                    "applicantidno": C_APP_IDENT_NO,  # 投保人证件号码
                    "applicantmobile": C_APP_TEL,  # 投保人电话
                    # "C_APP_ADDR": C_APP_ADDR,  # 投保人地址
                    "applicantemail": C_APP_EMAIL,  # 投保人邮箱
                    "insuredname": C_APP_NAME,  # 被保险人姓名
                    "insuredidno": C_APP_IDENT_NO,  # 被保险人证件号码
                    "insuredmobile": C_APP_TEL,  # 被保险人电话
                    "insuredaddresseeDetails": C_APP_ADDR,  # 被保险人地址
                    "insuredEmail": C_APP_EMAIL,  # 被保险人邮箱
                    "addresseeprovince": "",  # 配送地址省代码
                    "addresseecity": "",  # 配送地址市代码
                    "addresseetown": "",  # 区代码
                    "addresseename": C_CONTACT_NAME,
                    "addresseemobile": C_CONTACT_TEL,
                    "addresseedetails": C_ADDRESS,  # 收件地址
                    "ownername": C_APP_NAME,  # 车主姓名
                    "owneridno": C_APP_IDENT_NO,  # 身份证号
                    "IsterInfo": IsterInfo,
                    "ID":ID
                }
                YG = YangGuang()
                Result, REDICT, PAY_URL, ErrorMessage = YG.Get_120(**REDICT)
            if not REDICT.has_key('error') :
                    TempDict.update({"URL":PAY_URL})
                    return HttpResponsePermanentRedirect(PAY_URL)

            elif REDICT['error'] == '2':
                TempDict = REDICT
                TempDict.update({"yzm":"1"})
                TempDict.update({"company":'yg',"vin":vin,'ownername':C_APP_NAME})

                return render_to_response('ebusiness/editInfo.html', TempDict,
                                      context_instance=RequestContext(request))
            else:
                print(REDICT['msg'])
                return render_to_response('ebusiness/error.html')

        else:
            TempDict.update({"forms": editForms})
            TempDict.update({'id': id})
            return render_to_response('ebusiness/editInfo.html', TempDict, context_instance=RequestContext(request))

def auto(request):
    KLBJSON = PrintJson()
    ID = ['9','16','41','53','60','76','17']
    try:
        i = random.randint(0,len(ID))
        CarIN = bxcarvin.objects.get(id=ID[i])
    except:
        CarIN = bxcarvin.objects.get(id=ID[0])
    db = {"licenseNo":CarIN.licenseno,
          "engine":CarIN.engine,
          "ownerName":CarIN.ownername,
          "vin":CarIN.vin}
    J = KLBJSON.echo(msg="数据返回",error=0,  data=db)
    return HttpResponse(J, content_type="application/json")

def GetVIN(request):

    licenseNo = request.REQUEST.get("n1","")
    ownerName =  request.REQUEST.get("n2","")
    action = request.REQUEST.get("a","")
    re_licenseNo = re.match(u"^[\u4e00-\u9fa5]{1}[A-Z0-9]{6}$", licenseNo)
    re_ownerName = re.match(u"^[\u4e00-\u9fa5]{2,5}$", ownerName)
    JSON = PrintJson()
    if re_licenseNo and re_ownerName :

        VIN = GetCarVin(licenseNo=licenseNo,ownerName=ownerName)
        INDB = VIN.isInDB()
        if INDB:
            TempDict={"n1":INDB['vin'],"n2":INDB['engine']}
            J = JSON.echo(msg="数据返回",error=0,  data=TempDict)
            return HttpResponse(J, content_type="application/json")
        #a1为阳光
        if action=="a1":
            YGVIN = VIN.GetYangGuang()
            if YGVIN:
                TempDict={"n1":YGVIN['vin'],"n2":YGVIN['engine']}
                J = JSON.echo(msg="数据返回",error=0,  data=TempDict)
                return HttpResponse(J, content_type="application/json")
            else:
                J = JSON.echo(msg="格式错误",error=1)
                return HttpResponse(J, content_type="application/json")

    else:
        J = JSON.echo(msg="格式错误",error=1)
        return HttpResponse(J, content_type="application/json")

'''
用户个人中心
'''
@login_required(login_url="/ebusiness/")
def UserCenter(request):
    TempDict={}
    return render_to_response('ebusiness/UserCenter.html', TempDict, context_instance=RequestContext(request))
