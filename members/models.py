# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from LYZ.settings import SYS_APP
import datetime,os
from PIL import Image
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
from bxservice.models import bxcarvin

class ProfileBase(type):
    def __new__(cls,name,bases,attrs):
        module = attrs.pop('__module__')
        parents = [b for b in bases if isinstance(b, ProfileBase)]
        if parents:
            fields = []
            for obj_name, obj in attrs.items():
                if isinstance(obj, models.Field): fields.append(obj_name)
                User.add_to_class(obj_name, obj)
            UserAdmin.fieldsets = list(UserAdmin.fieldsets)
            UserAdmin.fieldsets.append((name, {'fields': fields}))
        return super(ProfileBase, cls).__new__(cls, name, bases, attrs)

class ProfileUser(object):
    __metaclass__ = ProfileBase

class MyProfile(ProfileUser):
    nick_name = models.CharField(max_length=255,verbose_name="昵称")
    real_name = models.CharField(max_length=255,verbose_name="真实姓名")
    level = models.IntegerField(default=0,verbose_name="用户等级")
    phone = models.CharField(max_length=64,default='',verbose_name='手机号码')
    # reg_time = models.DateTimeField(null=True,blank=True,auto_now_add=True,verbose_name='添加时间')
    # lastlogin = models.DateTimeField(null=True,blank=True,auto_now_add=True,auto_now=True,verbose_name='最后登录时间')
    addr= models.CharField(max_length=255,default='',verbose_name='住址',null=True,blank=True)
    hometown=models.CharField(max_length=255,default='',verbose_name='籍贯',null=True,blank=True)
    idcard= models.CharField(max_length=255,default='',verbose_name='身份证号码',null=True,blank=True)
    sex = models.IntegerField(max_length=1,default=0,verbose_name='性别',null=True,blank=True)
    img = models.ImageField(upload_to="user/",verbose_name="头像地址",null=True,blank=True)
    regos = models.CharField(default='',max_length=255,verbose_name='注册操作系统')
    sys = models.CharField(default=SYS_APP,max_length=255,verbose_name='平台')
    regip = models.IPAddressField(null=True,blank=True,verbose_name='注册ip')

#用户充值订单表
class order_pay(models.Model):
    user = models.ForeignKey(User,verbose_name='用户ID')
    order_number = models.CharField(default="",max_length=255,verbose_name='订单号')
    order_time = models.DateTimeField(auto_now_add=True,auto_now=False,verbose_name='订单生成时间')
    status = models.IntegerField(default=0,max_length=1,verbose_name='订单状态')
    order_sum = models.FloatField(default=0,max_length=11,verbose_name='金额')
    order_type = models.IntegerField(default=0,max_length=11,verbose_name='订单类型')
    class Meta:
        verbose_name = '用户充值订单表'
        verbose_name_plural = '用户充值订单表'

#用户金钱
class money(models.Model):
    user = models.ForeignKey(User,verbose_name='用户ID')
    order_pay = models.OneToOneField(order_pay,null=True,blank=True,verbose_name='订单号')
    money_sum = models.IntegerField(default=0,max_length=11,verbose_name='金额')
    action = models.CharField(default="",max_length=255,verbose_name='充值来源')
    add_time = models.DateTimeField(auto_now_add=True,auto_now=False,verbose_name='订单生成时间')
    status = models.IntegerField(default=1,max_length=1,verbose_name='状态')

    class Meta:
        verbose_name = '用户金钱表'
        verbose_name_plural = '用户金钱表'

'''
@用户积分表
'''
class uscores(models.Model):
    user = models.ForeignKey(User,verbose_name='用户ID')
    action = models.IntegerField(default=0,max_length=1,verbose_name='操作动作')
    number = models.IntegerField(default=0,max_length=11,verbose_name='分数')
    add_time = models.DateTimeField(auto_now_add=True,auto_now=False,verbose_name='获得积分时间')
    add_uid = models.IntegerField(default=0,max_length=2,verbose_name='操作用户')#0为系统
    class Meta:
        verbose_name = '用户积分表'
        verbose_name_plural = '用户积分表'
        db_table = "auth_user_scores"

'''
@注册用户发送短信表
'''
class sendsms(models.Model):
    phone = models.CharField(default="",max_length=255,verbose_name='手机号')
    sendnum = models.IntegerField(default=1,max_length=2,verbose_name='发送次数')
    validated_code = models.CharField(default='',max_length=10,verbose_name='验证码')
    addtime = models.DateTimeField(verbose_name='生成时间',auto_now_add=True,auto_now=False)
    is_active = models.IntegerField(default=0,max_length=1,verbose_name='是否已经使用')
    sendip = models.IPAddressField(null=True,blank=True,verbose_name='Ip地址')
    sendos = models.CharField(default='',max_length=255,verbose_name='用户操作系统')
    sys = models.CharField(default=SYS_APP,max_length=255,verbose_name='平台')

    class Meta:
        verbose_name = '短信表'
        verbose_name_plural = '短信表'
    def __unicode__(self):
        return self.phone

'''
手机、邮件地址激活
'''
class active(models.Model):
    user = models.OneToOneField(User,verbose_name='用户ID')
    is_email = models.IntegerField(default=0,max_length=1,verbose_name="邮件是否激活")
    is_mobile = models.IntegerField(default=0,max_length=1,verbose_name="手机号码是否激活")
    class Meta:
        verbose_name = '手机、邮件地址激活表'
        verbose_name_plural = '手机、邮件地址激活表'

'''
@用户推荐码
'''
class recomcode(models.Model):
    user = models.OneToOneField(User,verbose_name='用户ID')
    code = models.CharField(default='',max_length=255,verbose_name='推荐码')
    h5code = models.CharField(default='',max_length=255,null=True,blank=True,verbose_name='h5推荐码')
    dwz = models.CharField(default='',max_length=255,verbose_name='短网址')
    addtime = models.DateTimeField(auto_now_add=True,auto_now=True,verbose_name='生成时间')
    coder_class = models.CharField(default=SYS_APP,max_length=255,verbose_name='使用平台')

    class Meta:
        verbose_name = '推荐码表'
        verbose_name_plural = '推荐码表'
    def __unicode__(self):
        return self.code

'''
@推荐码使用表
'''
class recomcoder_user(models.Model):

    user = models.OneToOneField(User,verbose_name='用户ID')
    coder = models.ForeignKey(recomcode,verbose_name='推荐码')
    addtime = models.DateTimeField(auto_now_add=True,auto_now=False,verbose_name='使用时间')

    class Meta:
        verbose_name = '推荐码使用表'
        verbose_name_plural = '推荐码使用表'

'''
@用户图片上传
'''
class photo(models.Model):

    user = models.ForeignKey(User,verbose_name='用户ID')
    title = models.CharField(max_length = 100,verbose_name='标题')
    image = models.ImageField(upload_to ="photos/originals/%Y/%m/%d/",verbose_name='原始图路径')
    image_height = models.IntegerField()
    image_width = models.IntegerField()
    thumbnail = models.ImageField(upload_to="photos/thumbs/%Y/%m/%d/",verbose_name='缩略图路径')
    thumbnail_height = models.IntegerField()
    thumbnail_width = models.IntegerField()
    caption = models.CharField(max_length = 250, blank =True)
    image_class = models.IntegerField(default=0,verbose_name='图片分类')

    def save(self, force_update=False, force_insert=False, thumb_size=(180,300)):

        image = Image.open(self.image)

        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')

        self.image_width, self.image_height = image.size

        image.thumbnail(thumb_size, Image.ANTIALIAS)

        temp_handle = StringIO()
        image.save(temp_handle, 'png')
        temp_handle.seek(0)
        suf = SimpleUploadedFile(os.path.split(self.image.name)[-1],temp_handle.read(),content_type='image/png')
        self.thumbnail.save(suf.name+'.png', suf, save=False)
        self.thumbnail_width, self.thumbnail_height = image.size
        super(photo, self).save(force_update, force_insert)
    class Meta:
        verbose_name = '用户上传照片表'
        verbose_name_plural = '用户上传照片表'

#用户微信绑定
class wechat(models.Model):

    user = models.OneToOneField(User,null=True,verbose_name='用户ID')
    openid = models.CharField(max_length = 255,verbose_name='普通用户的标识')
    nickname = models.CharField(max_length = 255,verbose_name='普通用户昵称')
    language = models.CharField(max_length = 255,verbose_name='语言')
    sex = models.IntegerField(default=1,max_length = 2,verbose_name='普通用户性别')
    province = models.CharField(max_length = 255,verbose_name='普通用户个人资料填写的省份')
    city = models.CharField(max_length = 255,verbose_name='普通用户个人资料填写的城市')
    country = models.CharField(max_length = 255,verbose_name='国家')
    headimgurl = models.TextField(default='',verbose_name='用户头像')
    unionid = models.CharField(max_length = 255,verbose_name='用户统一标识')
    addtime = models.DateTimeField(verbose_name='生成时间',auto_now_add=True,auto_now=False)
    class Meta:
        verbose_name = '用户微信绑定表'
        verbose_name_plural = '用户微信绑表'

class recommend_log(models.Model):
    openid = models.ForeignKey(wechat,null=True,blank=True)
    fromopenid = models.ForeignKey(wechat,null=True,blank=True,related_name="fromwechat")
    from_open_id = models.CharField(max_length=255,default='',null=True,blank=True,verbose_name="被谁点击")
    to_open_id = models.CharField(max_length=255,default='',null=True,blank=True,verbose_name="点击谁")
    addtime = models.DateTimeField(verbose_name='生成时间',auto_now_add=True,auto_now=False)
    status = models.IntegerField(default=0,max_length=2,verbose_name='购买状态')

#用户车辆绑定

class car(models.Model):
    user = models.ForeignKey(User,verbose_name='用户ID')
    chepai = models.CharField(max_length = 255,verbose_name='车牌号')
    carusername = models.CharField(max_length = 255,verbose_name='车主姓名')
    vin = models.CharField(max_length=255,verbose_name="车架号")
    fadongji = models.CharField(max_length=255,verbose_name="发动机号")
    class Meta:
        verbose_name = '用户车辆表'
        verbose_name_plural = '用户车辆表'

#车辆基本信息

class carinfo(models.Model):

    car = models.OneToOneField(car,verbose_name='车辆ID')
    name = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="产品名称")
    # /*产品名称*/
    brand = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="品牌")
    # /*品牌*/
    productionDate = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="制造年份")
    # /*制造年份*/
    model = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="产品型号")
    # /*产品型号*/
    engineType = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="发动机型号")
    # /*发动机型号*/
    displacement = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="排量")
    # /*排量（CC）*/
    power = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="功率")
    # /*功率（KW）*/
    type = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="产品类型")
    # /*产品类型*/
    reatedQuality = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="额定质量")
    # /*额定质量*/
    totalQuality = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="总质量")
    # /*总质量*/
    equipmentQuality = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="装备质量")
    # /*装备质量*/
    combustionType = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="燃料种类")
    # /*燃料种类*/
    emissionStandards = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="排放依据标准")
    # /*排放依据标准*/
    shaftNum = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="轴数")
    # /*轴数*/
    shaftdistance = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="轴距")
    # /*轴距*/
    shaftLoad = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="轴荷")
    # /*轴荷*/
    springNum = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="弹簧片数")
    # /*弹簧片数*/
    tireNum = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="轮胎数")
    # /*轮胎数*/
    tireSpecifications = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="轮胎规格")
    # /*轮胎规格*/
    departureAngle = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="接近离去角")
    # /*接近离去角*/
    beforeAfterHanging = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="前悬后悬")
    # /*前悬后悬*/
    beforeWheelTrack = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="前轮距")
    # /*前轮距*/
    afterWheelTrack = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="后轮距")
    # /*后轮距*/
    carLong = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="整车长")
    # /*整车长*/
    carWidth = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="整车宽")
    # /*整车宽*/
    carHigh = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="整车高")
    # /*整车高*/
    crateLong = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="货箱长")
    # /*货箱长*/
    crateWidth = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="货箱宽")
    # /*货箱宽*/
    crateHight = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="货箱高")
    # /*货箱高*/
    maxSpeed = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="最高车速")
    # /*最高车速*/
    carrying = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="额定载客量")
    # /*额定载客量*/
    cabCarring = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="驾驶室准乘人数")
    # /*驾驶室准乘人数*/
    turnToType = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="转向形式")
    # /*转向形式*/
    trailerTotalQuality = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="准拖挂车总质量")
    # /*准拖挂车总质量*/
    loadQualityFactor = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="载质量利用系数")
    # /*载质量利用系数*/
    semiSaddleBearingQuelity = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="半挂车鞍座最大承载质量")
    # /*半挂车鞍座最大承载质量*/
    engineProducers = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="发动机生产商")
    # /*发动机生产商*/

    class Meta:
        verbose_name = '用户车辆表详细信息表'
        verbose_name_plural = '用户车辆细信息表'

#用户汽车召回查询日志
class recall_log(models.Model):
    user = models.ForeignKey(User,verbose_name="用户ID",null=True,blank=True)
    addtime = models.DateTimeField(auto_now_add=True,auto_now=False,verbose_name='添加时间')
    vin = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="VIN")
    class Meta:
        verbose_name = '汽车召回查询日志表'
        verbose_name_plural = '汽车召回查询日志表'

#用户查询汽车召回
class recall(models.Model):
    user = models.ForeignKey(User,verbose_name="用户ID",null=True,blank=True)
    car = models.OneToOneField(car,verbose_name="车辆",null=True,blank=True)
    log = models.ForeignKey(recall_log,verbose_name="日志ID",null=True,blank=True)
    addtime = models.DateTimeField(auto_now_add=True,auto_now=False,verbose_name='添加时间')
    vin = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="VIN")
    recall_time = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="召回时间")
    factory = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="厂家")
    cartype = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="型号")
    class Meta:
        verbose_name = '用户查询汽车召回表'
        verbose_name_plural = '用户查询汽车召回表'



# 订单表

class insure_pay_policy(models.Model):
    user = models.ForeignKey(User,verbose_name="用户ID",null=True,blank=True)
    TBOrderId = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="厂家")

#用户比价车辆历史
class car_history(models.Model):
    user = models.ForeignKey(User,verbose_name="用户ID",null=True,blank=True)
    car = models.ForeignKey(bxcarvin,verbose_name='用户ID',null=True,blank=True)
    addtime = models.DateTimeField(auto_now_add=True,auto_now=False,verbose_name='添加时间')

#比价历史
class pricing_history(models.Model):
    user = models.ForeignKey(User,verbose_name="用户ID",null=True,blank=True)
    history = models.ForeignKey(car_history,verbose_name="车牌历史id",null=True,blank=True)
    car = models.ForeignKey(bxcarvin,verbose_name='用户ID',null=True,blank=True)
    bxgs = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="保险公司")
    addtime = models.DateTimeField(auto_now_add=True,auto_now=False,verbose_name='添加时间')
    chesun = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="车损险")
    sanzhe = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="三者险")
    daoqiang = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="盗抢险")
    siji = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="责任司机")
    chengke = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="责任乘客")
    boli = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="玻璃破碎险")
    huahen = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="划痕险")
    ziran = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="自然险")
    fadongji = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="涉水险")
    chesun_bj = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="不计车损")
    sanzhe_bj = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="不计三者")
    daoqiang_bj = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="不计盗抢")
    siji_bj = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="不计司机")
    chengke_bj = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="不计乘客")
    jiaoqiang = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="交强险")
    chechuan = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="车船税")
    zongji = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="保费总计")
# 保额历史 1投保,0未投保
class coverage_history(models.Model):
    user = models.ForeignKey(User,verbose_name="用户ID",null=True,blank=True)
    history = models.ForeignKey(car_history,verbose_name="车牌历史id",null=True,blank=True)
    car = models.ForeignKey(bxcarvin,verbose_name='用户ID',null=True,blank=True)
    bxgs = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="保险公司")
    addtime = models.DateTimeField(auto_now_add=True,auto_now=False,verbose_name='添加时间')
    chesun = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="车损险")
    sanzhe = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="三者险")
    daoqiang = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="盗抢险")
    siji = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="责任司机")
    chengke = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="责任乘客")
    boli = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="玻璃破碎险")
    huahen = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="划痕险")
    ziran = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="自然险")
    fadongji = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="涉水险")
    chesun_bj = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="不计车损")
    sanzhe_bj = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="不计三者")
    daoqiang_bj = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="不计盗抢")
    siji_bj = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="不计司机")
    chengke_bj = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="不计乘客")
    jiaoqiang = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="交强险")
    chechuan = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="车船税")
    zongji = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="保费总计")
# 微信用户订单表
class user_order(models.Model):
    userid = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="用户ID")
    orderno = models.CharField(default="",null=True,blank=True,max_length=255, verbose_name="订单号")
    bxgs = models.CharField(default="",null=True,blank=True,max_length=255,verbose_name="保险公司")
    addtime = models.DateTimeField(auto_now_add=True,auto_now=False,verbose_name='添加时间')
