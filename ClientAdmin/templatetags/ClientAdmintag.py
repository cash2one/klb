# -*- coding:utf-8 -*-
from django import template
register = template.Library()

'''

'''
@register.tag(name="ShowTitle")
def ShowTitle(str):
    return "卡来宝系统管理-%s"%str
register.filter(ShowTitle)

@register.tag(name="NoAsterisk")
def NoAsterisk(str):
    str = str.replace("*","")
    return str
register.filter(NoAsterisk)


