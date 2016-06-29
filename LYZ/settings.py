# -*- coding:utf-8 -*-


import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
WEB_ROOT = BASE_DIR.replace('\\','/')
PUBLIC_DIR=os.path.join(WEB_ROOT,'public/').replace('\\','/')
FONTS_DIR=os.path.join(WEB_ROOT,'fonts/').replace('\\','/')
# 网页模版目录
TEMPLATE_DIRS = (
    os.path.join(WEB_ROOT,'templates/').replace('\\','/'),
)

SECRET_KEY = 'g^&l4+od9edl%%8%%_q3&jikt72+=&v%%k!ag3+b%6wa_1sauj'
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tokenapi',
    'members',
    'klbapp',
    'bxservice',
    'web',
    'wechat',
    'webadmin',
    'ClientAdmin',
    'ebusiness',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)
AUTHENTICATION_BACKENDS =(
    'django.contrib.auth.backends.ModelBackend',
    'tokenapi.backends.TokenBackend',
)
TOKEN_TIMEOUT_DAYS = 7
TOKEN_CHECK_ACTIVE_USER = True

ROOT_URLCONF = 'LYZ.urls'

WSGI_APPLICATION = 'LYZ.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bxweb',
        'HOST': '101.200.1.153',
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': 'klb139726845!@#$%^&*()',
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
)
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(WEB_ROOT,'static/').replace('\\', '/')
# STATIC_ROOT = os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'),'static')
STATICFILES_DIRS = (
    ("stylesheets", os.path.join(STATIC_ROOT,'stylesheets')),
    ("javascripts", os.path.join(STATIC_ROOT,'javascripts')),
    ("images", os.path.join(STATIC_ROOT,'images')),
    ("wechat", os.path.join(STATIC_ROOT,'wechat')),
    ("webadmin", os.path.join(STATIC_ROOT,'webadmin')),
    ("ClientAdmin", os.path.join(STATIC_ROOT,'ClientAdmin')),
    ("ebusiness", os.path.join(STATIC_ROOT,'ebusiness')),
)
# STATIC_ROOT = os.path.join(WEB_ROOT,'static/').replace('\\', '/')
MEDIA_ROOT = os.path.join(WEB_ROOT,'media/').replace('\\', '/')
MEDIA_URL = '/media/'

SYS_APP = "klb_bxweb"
SYS_MOBILE = "klb_bxapp"

#登录地址
LOGIN_URL = '/members/login/'
#短信
SMS_USER = "18629158186"
SMS_PWD = "9F9EF20F84F2B93330A71ACEF4DB"
SMS_URL = "http://web.1xinxi.cn/asmx/smsservice.aspx"

#微信
WECHAT_APPID = "wxe3aebe66d444b72b"
WECHAT_APPSECRET = "485bae4e950f7b4d85440084a3b56e72"
WECHAT_TOKEN = "weiphp"
WECHAT_URL = "http://web.kalaibao.com"

#微信open
OPEN_WECHAT_APPID = "wxc7eadf63b02d39bd"
OPEN_WECHAT_APPSECRET = "00d33900f6500980b553c55db1e24363"
OPEN_WECHAT_URL = "http://www.kalaibao.com"

#发送邮件
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_HOST_USER = 'kalaibao@kalaibao.com'
EMAIL_HOST_PASSWORD = 'tdf1618'

