# -*- coding:utf-8 -*-
from django import template
from LYZ.klb_class import *
register = template.Library()

'''
读取网站基本信息
'''

@register.tag(name="ENcode")
def ENcode(s, t=0):
    K= KLBCode()
    try:
        if t==0:
            return K.encode(s)
        else:
            return K.decode(s)
    except:
        return ""

register.filter(ENcode)

