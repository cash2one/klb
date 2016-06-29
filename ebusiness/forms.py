# -*- coding:utf-8 -*-
from django import forms
from bxservice.models import bxcarvin
from LYZ.settings import STATIC_ROOT
import json, urllib2, urllib, random,re
from ebusiness.models import vin_as_car_yg

class initVehicleBaseInfoForm(forms.Form):
    licenseNo = forms.RegexField(regex=u"^[\u4e00-\u9fa5]{1}[A-Z0-9]{6}$",
                                 error_messages={'invalid': '车牌格式不对', 'required': '车牌不能为空'}, label='车牌号码：',
                                 widget=forms.TextInput(
                                     attrs={"class": "form-control no-right-border", "id": "licenseNo", "placeholder": "请输入车牌号码"}))
    ownerName = forms.RegexField(regex=u"^[\u4e00-\u9fa5]{2,5}$",
                                 error_messages={'invalid': '车主姓名格式不正确', 'required': '车主姓名不能为空'}, label='车主姓名：',
                                 widget=forms.TextInput(
                                     attrs={"class": "form-control", "id": "ownerName", "placeholder": "请输入车主姓名"}))
    vin = forms.RegexField(regex="^[0-9a-zA-Z]{17}$", error_messages={'invalid': '车架号格式不正确', 'required': '车架号不能为空'},
                           label='车架号：', widget=forms.TextInput(
            attrs={"class": "form-control no-right-border form-focus-purple","id": "vin", "placeholder": "请输入车架号"}))
    engine = forms.CharField(required=True, error_messages={'invalid': '发动机号格式不正确', 'required': '发动机号格式不正确'},
                             label='发动机号：', widget=forms.TextInput(
            attrs={"class": "form-control", "id": "engine", "placeholder": "请输入发动机号"}))

    # 判断是否存在数据库
    def IsSet(self):
        licenseNo = self.cleaned_data.get('licenseNo')
        ownerName = self.cleaned_data.get('ownerName')
        CarIsSet = bxcarvin.objects.filter(licenseno=licenseNo, ownername=ownerName)
        if CarIsSet.count() > 0:
            return CarIsSet.values()[0]
        else:
            return False

    # 获取城市代码
    def GetCityCode(self):
        JsonPath = "%sjavascripts/cityListJson.json" % STATIC_ROOT
        readFile = open(JsonPath, mode="r").read()
        JsonCode = json.loads(readFile)
        # 车牌号
        licenseNo = self.cleaned_data.get('licenseNo')
        licenseNoNew = licenseNo.decode('utf8')[0:1].encode('utf8')
        cityCode = ""
        ZXList = [
            {'cararealiense': "京", "id": "110100"},
            {'cararealiense': "津", "id": "120100"},
            {'cararealiense': "沪", "id": "310100"},
            {'cararealiense': "渝", "id": "500100"}
        ]
        for i in range(len(ZXList)):
            if licenseNoNew == ZXList[i]['cararealiense']:
                cityCode = ZXList[i]['id']
                break

        if cityCode == "":
            licenseNoNew = licenseNo.decode('utf8')[0:2].encode('utf8')
            print(licenseNoNew)
            for n in range(len(JsonCode['dictionary'])):
                if licenseNoNew == JsonCode['dictionary'][n]['cararealiense']:
                    cityCode = JsonCode['dictionary'][n]['id']
                    break

        return cityCode

    def GetCarInfo(self):
        vin = self.cleaned_data.get('vin')
        GetVIN = vin_as_car_yg.objects.filter(vin=vin)
        if GetVIN.count()>0:
            return GetVIN
        else:
            try:
                YGURL = "http://chexian.sinosig.com/Partner/netVehicleModel.action"
                ygdata = {
                    "searchCode": vin,
                    "searchType": "1",
                    "encoding": "utf-8",
                    "isSeats": "1",
                    "pageSize": "100",
                    "callback": str(random.randint(100000, 999999))

                }
                req_header = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                    'Accept': 'text/html;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'gzip',
                    'Connection': 'close',
                    'Host': 'chexian.sinosig.com',
                    'Referer': 'chexian.sinosig.com'
                }

                req = urllib2.Request(YGURL, urllib.urlencode(ygdata), req_header)
                CarListJson = urllib2.urlopen(req).read()
                CarInfoList = re.sub(r'([a-zA-Z_0-9\.]*\()|(\);?$)', '', CarListJson)
                CarInfoJson = json.loads(CarInfoList)
                CarInfo = CarInfoJson['rows']

            except:
                CarInfo =  False

            if CarInfo and len(CarInfo)>0:
                for c in range(len(CarInfo)):
                    vin_as_car_yg.objects.get_or_create(vehicleFgwCode=CarInfo[c]['vehicleFgwCode'],value=CarInfo[c]['value'],key=CarInfo[c]['key'],vin=vin)
                GetVIN = vin_as_car_yg.objects.filter(vin=vin)
                return GetVIN

            else:
                return False





class EditInfoForm(forms.Form):
    #投保人
    C_APP_NAME = forms.RegexField(
        regex=u"^[\u4e00-\u9fa5]{2,5}$",
        error_messages={'invalid': '投保人姓名格式不正确', 'required': '投保人姓名不能为空'},
        label='投保人姓名：',
        widget=forms.TextInput(attrs={"class": "form-control", "id": "C_APP_NAME", "placeholder": "填写投保人姓名"})
    )
    #投保人身份证
    C_APP_IDENT_NO = forms.RegexField(
        regex="^(\d{6})(\d{4})(\d{2})(\d{2})(\d{3})([0-9]|X)$",
        error_messages={'invalid': '投保人身份证格式不正确', 'required': '投保人身份证不能为空'},
        label='投保人身份证：',
        widget=forms.TextInput(attrs={"class": "form-control", "id": "C_APP_IDENT_NO", "placeholder": "填写投保人身份证"})
    )
    #投保人联系电话
    C_APP_TEL = forms.RegexField(
        regex="^((\d{11})|^((\d{7,8})|(\d{4}|\d{3})-(\d{7,8})|(\d{4}|\d{3})-(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1})|(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1}))$)",
        error_messages={'invalid': '投保人联系电话格式不正确', 'required': '投保人联系电话不能为空'},
        label='投保人联系电话：',
        widget=forms.TextInput(attrs={"class": "form-control", "id": "C_APP_TEL", "placeholder": "填写投保人联系电话"})
    )
    # 投保人地址
    C_APP_ADDR = forms.RegexField(
        regex=u"^[\u4e00-\u9fa5]",
        error_messages={'invalid': '投保人地址格式不正确', 'required': '投保人地址不能为空'},
        label='投保人地址：',
        widget=forms.TextInput(attrs={"class": "form-control", "id": "C_APP_ADDR", "placeholder": "填写投保人地址"})
    )
    # 投保人邮箱
    C_APP_EMAIL = forms.EmailField(
        required=True,
        error_messages={'invalid': '投保人邮箱格式不正确', 'required': '投保人邮箱不能为空'},
        label='投保人邮箱：',
        widget=forms.TextInput(attrs={"class": "form-control", "id": "C_APP_EMAIL", "placeholder": "填写投保人邮箱"})
    )
    # 收件人手机号
    C_CONTACT_TEL  = forms.RegexField(
        regex="^((\d{11})|^((\d{7,8})|(\d{4}|\d{3})-(\d{7,8})|(\d{4}|\d{3})-(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1})|(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1}))$)",
        error_messages={'invalid': '收件人手机号格式不正确', 'required': '收件人手机号不能为空'},
        label='收件人手机号：',
        widget=forms.TextInput(attrs={"class": "form-control", "id": "C_CONTACT_TEL", "placeholder": "填写收件人手机号"})
    )
    # 收件人
    C_CONTACT_NAME  = forms.RegexField(
        regex=u"^[\u4e00-\u9fa5]{2,5}$",
        error_messages={'invalid': '收件人格式不正确', 'required': '收件人不能为空'},
        label='收件人：',
        widget=forms.TextInput(attrs={"class": "form-control", "id": "C_CONTACT_NAME", "placeholder": "填写收件人姓名"})
    )
    # 详细收货地址
    C_ADDRESS  = forms.RegexField(
        regex=u"^[\u4e00-\u9fa5]",
        error_messages={'invalid': '详细收货地址格式不正确', 'required': '详细收货地址不能为空'},
        label='详细收货地址：',
        widget=forms.TextInput(attrs={"class": "form-control", "id": "C_ADDRESS", "placeholder": "填写详细收货地址"})
    )
