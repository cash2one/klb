# -*- coding:utf-8 -*-
from django.db import models


class ebusiness_members(models.Model):
    father = models.ForeignKey('self', default='', null=True, blank=True, verbose_name='父级渠道')
    username = models.CharField(max_length=255, default='', verbose_name='渠道方的用户名')
    passwd = models.CharField(max_length=255, default='', verbose_name='渠道方密码')
    reg_time = models.DateTimeField(verbose_name='生成时间', auto_now_add=True, auto_now=False)
    code = models.CharField(max_length=255, default='', verbose_name='渠道代码')
    status = models.IntegerField(default=0, max_length=2, null=True, blank=True, verbose_name='是否被屏蔽')
    last_login = models.CharField(max_length=255, default='', null=True, blank=True, verbose_name='最后登录时间')
    last_ip = models.IPAddressField(verbose_name='最后登录IP', null=True, blank=True)
    sys = models.CharField(max_length=255, default='', null=True, blank=True, verbose_name='登录操作系统')
    login_num = models.IntegerField(default=0, max_length=2, null=True, blank=True, verbose_name='是否被屏蔽')
    rebate = models.CharField(max_length=255, default='50', null=True, blank=True, verbose_name='返现金额')
    ischildren = models.IntegerField(default=0,max_length=2,verbose_name='是否有下线功能')

    class Meta:
        verbose_name = '渠道方用户表'
        verbose_name_plural = '渠道方用户表'

    def delete(self, *args, **kwargs):
        self.clear_nullable_related()
        super(ebusiness_members, self).delete(*args, **kwargs)

    def clear_nullable_related(self):
        for related in self._meta.get_all_related_objects():
            accessor = related.get_accessor_name()
            related_set = getattr(self, accessor)

            if related.field.null:
                related_set.clear()
            else:
                for related_object in related_set.all():
                    related_object.clear_nullable_related()

    def __unicode__(self):
        return self.username




class flow_analytics(models.Model):
    ebusiness = models.ForeignKey("ebusiness_members", default='', null=True, blank=True, verbose_name='渠道代码')
    ip = models.CharField(max_length=255, default='', null=True, blank=True, verbose_name='IP')
    browser = models.CharField(max_length=255, default='', null=True, blank=True, verbose_name='浏览器')
    os = models.CharField(max_length=255, default='', null=True, blank=True, verbose_name='操作系统')
    intime = models.DateTimeField(verbose_name='开始访问时间', auto_now_add=True, auto_now=False)
    endtime = models.DateTimeField(verbose_name='最后访问时间', auto_now_add=True, auto_now=True)
    inurl = models.CharField(max_length=255, default='', null=True, blank=True, verbose_name='第一次打开的网址')
    endurl = models.CharField(max_length=255, default='', null=True, blank=True, verbose_name='最后一次访问的网址')
    num = models.IntegerField(max_length=11, default=1, verbose_name='日访问次数')

    class Meta:
        verbose_name = '访问统计表'
        verbose_name_plural = '访问统计表'
