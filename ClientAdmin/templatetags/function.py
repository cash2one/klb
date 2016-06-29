# -*- coding:utf-8 -*-
import re
'''
$函数名:CheckStrFormat
$介绍:检查字符串格式
$参数:str(string)
$返回:int  1邮件2手机3中文
'''


def CheckStrFormat(str):
    # 判断用户登录方式：手机号，邮件地址，用户名
    PhoneRegex = "^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$"  # 手机号正则
    EmailRegex = "^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$"  # 邮件正则
    StrRegex = "^[\u4e00-\u9fa5]+"  # 中文名普通正则