# -*- coding:utf-8 -*-
from django import forms
from django.contrib.auth.hashers import make_password, check_password
from webadmin.models import ebusiness_members
STATUS_OPTIONS = (("0", "激活"),("1", "未激活"))
class AddUserForms(forms.Form):

    username = forms.CharField(
        required=True,
        max_length=40,
        error_messages={'invalid': '用户名必须输入', 'required': '用户名必须输入'},
        label='渠道登录用户名：',
        widget=forms.TextInput(
            attrs={"class":"form-control rounded","id":"username","placeholder":"用户名"}
        )
    )

    passwd = forms.CharField(
        required=True,
        error_messages={'invalid': '密码格式不正确', 'required': '密码格式不正确'},
        label='密码：',
        widget=forms.PasswordInput(
            attrs={"class":"form-control rounded","id":"passwd","placeholder":"请输入密码"}
        )
    )

    repasswd = forms.CharField(
        required=True,
        error_messages={'invalid': '密码格式不正确', 'required': '密码格式不正确'},
        label='确认密码：',
        widget=forms.PasswordInput(
            attrs={"class":"form-control rounded","id":"repasswd","placeholder":"请再次输入密码"}
        )
    )

    status = forms.ChoiceField(
        choices=STATUS_OPTIONS,
        required=False,
        label='用户状态：',
        initial='激活',
        widget=forms.Select(
            attrs={"class":"form-control rounded","id":"status"}
        )
    )

    rebate = forms.CharField(
        required=True,
        error_messages={'invalid': '用户返利格式不正确', 'required': '用户返利格式不正确'},
        label='用户返利：',
        widget=forms.TextInput(
            attrs={"class":"form-control rounded","id":"rebate","placeholder":"用户返利"}
        )
    )

    def clean_repasswd(self):
        passwd = self.cleaned_data.get("passwd")
        repasswd = self.cleaned_data.get("repasswd")
        if passwd and repasswd and passwd != repasswd:
            raise forms.ValidationError('两次密码输入不一致')
        return repasswd


    def clean_username(self):
        username = self.cleaned_data.get("username")
        if ebusiness_members.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名存在,请更换用户名')
        return username


    def CheckAuthenticate(self):
        username = self.cleaned_data.get("username")
        passwd = self.cleaned_data.get("passwd")
        status = self.cleaned_data.get("status")
        rebate = self.cleaned_data.get("rebate")
        passwd = make_password(passwd)
        code = str((int(ebusiness_members.objects.count())*100)+888)
        CreateUser,isset = ebusiness_members.objects.get_or_create(username=username,passwd=passwd,status=status,rebate=rebate,code=code)
        return CreateUser,isset

