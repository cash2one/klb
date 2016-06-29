# -*- coding:utf-8 -*-
from webadmin.models import ebusiness_members
from django import forms
from django.contrib.auth.hashers import check_password, make_password


class UserForms(forms.Form):
    username = forms.CharField(
        required=True,
        max_length=40,
        error_messages={'invalid': '用户名必须输入', 'required': '用户名必须输入'},
        label='渠道登录用户名：',
        widget=forms.TextInput(
            attrs={"class": "form-control rounded", "id": "username", "placeholder": "用户名"}
        )
    )

    passwd = forms.CharField(
        required=True,
        max_length=20,
        min_length=6,
        error_messages={'invalid': '密码格式不正确', 'required': '密码格式不正确'},
        label='密码：',
        widget=forms.PasswordInput(
            attrs={"class": "form-control rounded", "id": "passwd", "placeholder": "请输入密码"}
        )
    )

    def clean(self):

        cleaned_data = super(UserForms, self).clean()
        username = cleaned_data.get("username")
        passwd = cleaned_data.get("passwd")
        UserMember = ebusiness_members.objects.filter(username=username)
        if UserMember.count() > 0:
            pwd = UserMember.values()[0]['passwd']
            if not check_password(passwd, pwd):
                msg_username = u"用户密码不正确"
                self._errors["username"] = self.error_class([msg_username])

        else:
            msg_username = u"用户不存在"
            self._errors["username"] = self.error_class([msg_username])

        return cleaned_data


'''
自定义渠道代码
'''


class DefineCodeForms(forms.Form):
    code = forms.RegexField(
        required=True,
        regex="^[0-9a-zA-Z]{2,20}$",
        error_messages={'invalid': '渠道代码格式不正确', 'required': '渠道代码格式不正确'},
        label='渠道代码：',
        widget=forms.TextInput(
            attrs={"class": "form-control", "id": "code"}
        )
    )
    uid = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )

    def clean(self):
        cleaned_data = super(DefineCodeForms, self).clean()
        code = cleaned_data.get("code")
        uid = cleaned_data.get("uid")
        print(code)
        print(uid)
        GetCode = ebusiness_members.objects.filter(code=code).exists()
        if GetCode:
            code_msg = '渠道代码已经存在，请更换'
            self._errors["code"] = self.error_class([code_msg])
        else:
            try:
                GetUser = ebusiness_members.objects.get(id=uid)
                GetUser.code = code
                GetUser.save()
            except:
                code_msg = '渠道代码更新失败'
                self._errors["code"] = self.error_class([code_msg])
        return cleaned_data


class UserAuth(object):
    def __init__(self, req):
        self.username = req.session.get("ebusiness_username", "")

    def isLogin(self):
        if self.username == "" or self.username == None:
            return False
        else:
            return True


class AutoCreateUser(forms.Form):
    username = forms.CharField(
        required=True,
        max_length=20,
        error_messages={'invalid': '用户名必须输入', 'required': '用户名必须输入'},
        label='登录用户名：',
        widget=forms.TextInput(
            attrs={"class": "form-control rounded", "id": "username", "placeholder": "用户名"}
        )
    )

    passwd = forms.CharField(
        required=True,
        max_length=20,
        min_length=6,
        error_messages={'invalid': '密码格式不正确', 'required': '密码格式不正确'},
        label='密码：',
        widget=forms.PasswordInput(
            attrs={"class": "form-control rounded", "id": "passwd", "placeholder": "请输入密码"}
        )
    )

    repasswd = forms.CharField(
        required=True,
        error_messages={'invalid': '密码格式不正确', 'required': '密码格式不正确'},
        label='确认密码：',
        widget=forms.PasswordInput(
            attrs={"class": "form-control rounded", "id": "repasswd", "placeholder": "请再次输入密码"}
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

    def CheckAuthenticate(self,fcode=None):
        username = self.cleaned_data.get("username")
        passwd = self.cleaned_data.get("passwd")
        passwd = make_password(passwd)
        try:
            code = str((int(ebusiness_members.objects.count()) * 100) + 888)
            get_fuid = ebusiness_members.objects.get(code=fcode)
            CreateUser, isset = get_fuid.ebusiness_members_set.get_or_create(username=username, passwd=passwd, status=1,
                                                                        rebate=0, code=code)
            return CreateUser, isset
        except:
            return False, False
