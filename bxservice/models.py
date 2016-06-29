# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
#车辆表
class bxcarvin(models.Model):
    user = models.ForeignKey(User,null=True,blank=True,verbose_name="用户ID")
    licenseno = models.CharField(max_length=255,null=True,blank=True,default="",verbose_name="车牌号")
    ownername = models.CharField(max_length=255,null=True,blank=True,default="",verbose_name="车主姓名")
    vin = models.CharField(max_length=255,null=True,blank=True,default="",verbose_name="Vin")
    engine = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="发动机号")
    citycode = models.CharField(max_length=255,default='110100',null=True,blank=True,verbose_name="城市编码")
    idcode = models.CharField(max_length=255,default='',null=True,blank=True,verbose_name="车主身份证")
    drivCity = models.CharField(max_length=255,default='',null=True,blank=True,verbose_name="行驶城市")
    class Meta:
        verbose_name = '车辆VIN表'
        verbose_name_plural = '车辆vin表'
    def __unicode__(self):
        return self.id

class bxcarinfo(models.Model):
    user = models.ForeignKey(User,null=True,blank=True,verbose_name="用户ID")
    car = models.ForeignKey(bxcarvin,verbose_name="车ID")
    key = models.CharField(max_length=255,default='',null=True,blank=True,verbose_name="key")
    vehiclefgwcode = models.CharField(max_length=255,default='',null=True,blank=True,verbose_name="vehicleFgwCode")
    value = models.CharField(max_length=255,default='',null=True,blank=True,verbose_name="车辆信息")
    bxtype = models.CharField(max_length=255,default='sinosig',null=True,blank=True,verbose_name="保险公司接口")#sinosig = 阳光 axatp = 安盛 cic=中华

    class Meta:
        verbose_name = '车辆信息'
        verbose_name_plural = '车辆信息'
    def __unicode__(self):
        return self.value

class bxpriceinfo(models.Model):
    user = models.ForeignKey(User,null=True,blank=True,verbose_name="用户ID")
    car = models.ForeignKey(bxcarvin,verbose_name="车ID")
    bxtype = models.CharField(default="",max_length=40,null=True,verbose_name="保险公司类型")
    order_id = models.CharField(max_length=255,default="",verbose_name="订单号")
    biz_begin_date = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业保险起期")
    biz_end_date = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业保险止期")
    traff_begin_date = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交强保险起期")
    traff_end_date = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交强保险止期")
    cs_traff_amt = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车损限额")
    dq_traff_amt = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="盗抢限额")
    zr_traff_amt = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="自然限额")
    first_register_date = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="初次领证日期")
    class Meta:
        verbose_name = '车辆算价信息'
        verbose_name_plural = '车辆算价信息'


class bxzhpriceinfo(models.Model):
    car = models.ForeignKey(bxcarvin,verbose_name="车ID")
    biztotalpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险保费")
    vehicletaxpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车船税")
    forcepremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交强险")
    bizbegindate = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险起始日期")
    forcebegindate =  models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交强险起始日期")
    kind_030004 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="玻璃单独破碎险")
    kind_030006 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="机动车损失保险")
    kind_030012 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="自燃损失险")
    kind_030018 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="机动车第三者责任保险")
    kind_030025 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车身划痕损失险")
    kind_030059 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="机动车盗抢保险")
    kind_030065 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="涉水发动机损坏险")
    kind_030070 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="机动车车上人员责任保险（司机）")
    kind_030072 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="机动车车上人员责任保险（乘客）")
    kind_030106 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔特约条款（盗抢险）")
    kind_030125 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔特约条款（涉水发动机损坏险")
    kind_031901 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔特约条款（车损险）")
    kind_031902 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔特约条款（三者险）")
    kind_031903 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔特约条款（自燃险）")
    kind_031911 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔特约条款（车身划痕险）")
    kind_033531 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔特约条款（车上人员司机）")
    kind_033532 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔特约条款（车上人员乘客）")
    kind_033535 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="指定专修厂特约条款")
    class Meta:
        verbose_name = '中华车辆算价信息'
        verbose_name_plural = '中华车辆算价信息'

class bxpayinfo(models.Model):
    car = models.ForeignKey(bxcarvin,verbose_name="车ID")
    order_id = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="订单号")
    session_id = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="Session")
    app_name = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人姓名")
    app_ident_no = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人身份证号")
    app_tel = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人电话")
    app_addr = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人地址")
    app_email = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人邮箱")
    insrnt_name = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人姓名")
    insrnt_ident_no = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人身份证号")
    insrnt_tel = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人电话")
    insrnt_addr = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人地址")
    insrnt_email = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人邮箱")
    contact_name = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="收件人姓名")
    contact_tel = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="联系人电话")
    address = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="收件地址")
    idet_name = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="行驶证车主")
    ident_no = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="行驶证号(身份证号)")
    delivery_province = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="配送省份代码")
    delivery_city = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="配送城市代码")
    delivery_district = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="配送区县代码")
    businesscode = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交易类型")
    bxgs_type = models.CharField(max_length=255,default="cic",null=True,blank=True,verbose_name="保险公司类型")#sinosig = 阳光 axatp = 安盛 cic=中华
    status = models.CharField(default="0",max_length=255,null=True,blank=True,verbose_name="订单状态")
    c_proposal_no_biz = models.CharField(default="0",max_length=255,null=True,blank=True,verbose_name="订单状态")
    c_proposal_no_force = models.CharField(default="0",max_length=255,null=True,blank=True,verbose_name="订单状态")
    class Meta:
        verbose_name = '中华投保信息表'
        verbose_name_plural = '中华投保信息表'

class bxzhcallbackinfo(models.Model):
    mm = models.ForeignKey(bxpayinfo,verbose_name="ID")
    order_id = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="订单号")
    pay_transn = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="支付流水号")
    pay_amt = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="支付金额")
    pay_staus = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="支付状态")
    pay_desc = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="支付描述")
    chengbao_staus = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="承保状态")
    message = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="提示信息")
    biz_policy_no = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="保单号（商业）")
    force_policy_no = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="保单号（交强）")
    businesscode = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交易类型")
    class Meta:
        verbose_name = '中华回调信息表'
        verbose_name_plural = '中华回调信息表'

class bxashebaoinfo(models.Model):
    car = models.ForeignKey(bxcarvin,verbose_name="车ID")
    session_id = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="Session")
    tborder_id = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="本地订单号")
    item_id = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="产品ID")
    insuredname = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人姓名")
    insuredidno = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人证件号")
    insuredmobile = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人电话")
    insuredidtype = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人证件类型")
    insuredgender = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人性别")
    insuredbirthday =  models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人生日")
    ownername = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车主姓名")
    owneridno = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车主证件号")
    ownermobile = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车主电话")
    owneremail = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车主邮箱")
    owneridtype = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="证件类型")
    ownergender = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车主性别")
    ownerbirthday = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车主生日")
    ownerage = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车主年龄")
    addresseename = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="收件人姓名")
    addresseemobile = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="收件人电话")
    addresseeprovince = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="省份代码")
    addresseecity = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="城市代码")
    addresseetown = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="区县代码")
    addresseedetails = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="详细地址")
    applicantname = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人姓名")
    applicantidno = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人证件号")
    applicantmobile = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人电话")
    applicantemail = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人邮箱")
    applicantbirthday = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人生日")
    applicantgender = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人性别")
    applicantidtype =  models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人证件类型")
    bxgs_type = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="保险公司类型")
    status = models.CharField(default="0",max_length=255,null=True,blank=True,verbose_name="订单状态")
    proposalno_biz = models.CharField(default="0",max_length=255,null=True,blank=True,verbose_name="商业保单")
    proposalno_force = models.CharField(default="0",max_length=255,null=True,blank=True,verbose_name="交强保单")
    class Meta:
        verbose_name = '安盛核保信息表'
        verbose_name_plural = '安盛核保信息表'

    # 安盛报价返回信息
class bxaspriceinfo(models.Model):
    car = models.ForeignKey(bxcarvin,verbose_name="车ID")
    bizflag = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="是否投保商业险")
    forceflag = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="是否投保交强险")
    cov_200 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车损险")
    cov_600 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="第三者责任险")
    cov_701 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="司机责任险")
    cov_702 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="乘客责任险")
    cov_500 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="盗抢险")
    cov_290 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="涉水险")
    cov_231 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="玻璃险")
    cov_210 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="划痕险")
    cov_310 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="自燃损失险")
    cov_900 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险特约条款")
    cov_910 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险(不计免赔合并")
    cov_911 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（车损险）")
    cov_912 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（三者险）")
    cov_921 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（机动车盗抢险）")
    cov_922 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（车身划痕损失险）")
    cov_923 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（自燃险）")
    cov_924 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（涉水险）")
    cov_928 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（车上人员责任险（司机））")
    cov_929 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（车上人员责任险（乘客））")
    cov_930 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（车上人员责任险）")
    cov_931 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔（附加险）")
    biztotalpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险保费")
    totalpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="实际保费")
    standardpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="应交保费")
    forcepremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交强险总计")
    bizbegindate = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险起始日期")
    forcebegindate =  models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交强险起始日期")
    vehicletaxpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车船税")
    forcepremium_f = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交强险")
    session_id = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="Session")
    class Meta:
        verbose_name = '安盛报价信息表'
        verbose_name_plural = '安盛报价信息表'

class bxascallbackinfo(models.Model):
    hebao_id = models.ForeignKey(bxashebaoinfo,verbose_name="核保ID")
    sessionid = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="SessionID")
    requesttype = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="回调类型")# 215 核保回调，230 承保毁掉
    tborderid = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="本地订单号")
    premium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="保险总价")
    itemid = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="产品id")
    bizpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险总价")
    bizproposalno = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业投保单号")
    bizpolicyno = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业投单号")
    forcepremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险总价")
    forceproposalno = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业投保单号")
    forcepolicyno = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业投单号")
    status = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="核保状态")
    class Meta:
        verbose_name = '安盛回调信息表'
        verbose_name_plural = '安盛回调信息表'

class bxygpriceinfo(models.Model):
    car = models.ForeignKey(bxcarvin,verbose_name="车ID")
    forceflag = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="是否投保交强险")
    cov_200 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车损险")
    cov_600 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="第三者责任险")
    cov_701 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="司机责任险")
    cov_702 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="乘客责任险")
    cov_500 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="盗抢险")
    cov_291 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="涉水险")
    cov_231 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="玻璃险")
    cov_210 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="划痕险")
    cov_310 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="自燃损失险")
    cov_390 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="高速高价救援险")
    cov_640 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交通事故精神损害赔偿责任险")
    cov_911 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（车损险）")
    cov_912 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（三者险）")
    cov_921 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（机动车盗抢险）")
    cov_922 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（车身划痕损失险）")
    cov_928 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（车上人员责任险（司机））")
    cov_929 = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="不计免赔险（车上人员责任险（乘客））")
    biztotalpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险保费")
    totalpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="网购价")
    standardpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="市场价")
    forcepremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交强险")
    bizbegindate = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险起始日期")
    forcebegindate =  models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交强险起始日期")
    vehicletaxpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车船税")
    forceotalpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="交强险总保费")
    session_id = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="Session")
    class Meta:
        verbose_name = '阳光报价信息表'
        verbose_name_plural = '阳光报价信息表'

class bxyghebaoinfo(models.Model):
    car = models.ForeignKey(bxcarvin,verbose_name="车ID")
    session_id = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="Session")
    tborder_id = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="本地订单号")
    item_id = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="产品ID")
    insuredname = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人姓名")
    insuredidno = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人证件号")
    insuredmobile = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人电话")
    insuredemail = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人邮箱")
    ownername = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车主姓名")
    owneridno = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车主证件号")
    ownermobile = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车主电话")
    owneremail = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车主邮箱")
    addresseename = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="收件人姓名")
    addresseemobile = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="收件人电话")
    senddate =  models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="配送时间")
    insuredaddresseeDetails = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="被保险人身份证地址")
    addresseeprovince = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="省份代码")
    addresseecity = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="城市代码")
    addresseetown = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="区县代码")
    addresseedetails = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="详细地址")
    applicantname = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人姓名")
    applicantidno = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人证件号")
    applicantmobile = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人电话")
    applicantemail = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="投保人邮箱")
    bxgs_type = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="保险公司类型")
    status = models.CharField(default="0",max_length=255,null=True,blank=True,verbose_name="订单状态")
    proposalno_biz = models.CharField(default="0",max_length=255,null=True,blank=True,verbose_name="商业保单")
    proposalno_force = models.CharField(default="0",max_length=255,null=True,blank=True,verbose_name="交强保单")

    class Meta:
        verbose_name = '阳光核保信息表'
        verbose_name_plural = '阳光核保信息表'

class bxygcallbackinfo(models.Model):
    hebao_id = models.ForeignKey(bxyghebaoinfo,verbose_name="本地订单号")
    session_id = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="Sessionid")
    usercode = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="第三方用户登入账号")
    orderno_biz = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业订单号")
    orderno_force = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name='交强订单号')
    proposalno_biz = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name='商业投保单号')
    policyno_biz = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name='商业*保单号')
    proposalno_force = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name='交强投保单号')
    policyno_force = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name='交强*保单号')
    startdate = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name='起保日期')
    enddate = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name='终止日期')
    forcepremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name='交强险')
    vehicletaxpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name='车船税')
    paytime = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="支付时间")
    bizpremium = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险总价")

class bxzhisread(models.Model):
    price = models.ForeignKey(bxpayinfo,verbose_name='报价id')
    orderno = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险总价")
    flag = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险总价")
    businesscode_biz = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险总价")
    businesscode_force = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="商业险总价")
    class Meta:
        verbose_name = '中华是否阅读浮动告知单表'
        verbose_name_plural = '中华是否阅读浮动告知单表'
class citycode(models.Model):
    cararealiense  = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="车牌前缀")
    coding = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="coding")
    entrytime = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="entrytime")
    mid = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="城市代码")
    name = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="城市名称")
    pid = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="pid")
    citycode_yg = models.CharField(max_length=255,default="",null=True,blank=True,verbose_name="国际码")

    class Meta:
        verbose_name = '城市代码表'
        verbose_name_plural = '城市代码表'
    def __unicode__(self):
        return self.name,self.citycode_yg
class callbaklog(models.Model):
    log = models.TextField(default='',null=True,blank=True,verbose_name="xml")
    addtime = models.CharField(max_length=255,default='',null=True,blank=True,verbose_name="时间")
    bxgs_type = models.CharField(max_length=255,default='',null=True,blank=True,verbose_name="保险公司类型")
    interface_type = models.CharField(max_length=255,default='',null=True,blank=True,verbose_name="接口类型")
    class Meta:
        verbose_name = '回调日志'
        verbose_name_plural = '回调日志'

