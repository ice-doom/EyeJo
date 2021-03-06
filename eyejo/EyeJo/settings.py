"""
Django settings for EyeJo project.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import yaml

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

with open(str(Path('/').joinpath(BASE_DIR, "config.yaml"))) as f:
    yaml_configuration = yaml.safe_load(f)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!z)!7awn59ip0zt$gq8bw%dnng^hs!$%7b#)umkmk+_t@*9ysd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# 访问页面不存在时,禁止在路径后补充左斜杠
APPEND_SLASH = False

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'projectApp',
    'scanTaskApp',

    # 'django_dramatiq',
    # 'silk',
    'rest_framework'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',  # 支持中文显示
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'silk.middleware.SilkyMiddleware'
]

ROOT_URLCONF = 'EyeJo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'EyeJo.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'dj_db_conn_pool.backends.mysql',   # 数据库引擎
        'POOL_OPTIONS': {
            'POOL_SIZE': 200,
            'MAX_OVERFLOW': 200,
        },
        "OPTIONS": {
                    "isolation_level": "repeatable read"  # 将事务隔离级别设置为repeatable read
                },
        'NAME': yaml_configuration["MYSQL"]["NAME"],  # 数据库名，先前创建的
        'USER': yaml_configuration["MYSQL"]["USER"],  # 用户名，可以自己创建用户
        'PASSWORD': yaml_configuration["MYSQL"]["PASSWORD"],  # 密码
        'HOST': yaml_configuration["MYSQL"]["HOST"],  # mysql服务所在的主机ip
        'PORT': yaml_configuration["MYSQL"]["PORT"],  # mysql服务端口
    }
}



# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'


USE_I18N = True

USE_L10N = True

USE_TZ = True
# USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

LOGIN_REQUIRED_IGNORE_VIEW_NAMES = [
    'login',
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboardIndex'
LOGOUT_REDIRECT_URL = 'login'


'''
CELERY settings
'''
CELERY_BROKER_URL = f'redis://:{yaml_configuration["REDIS"]["PASSWORD"]}@{yaml_configuration["REDIS"]["HOST"]}:{yaml_configuration["REDIS"]["PORT"]}'  # Broker配置，使用Redis作为消息中间件
CELERYD_MAX_TASKS_PER_CHILD = 20  # 每个worker最大执行任务数
# CELERYD_CONCURRENCY = 2  # celery worker并发数,默认是服务器的内核数目
CELERY_ACKS_LATE = False  # 任务发送完成是否需要确认
CELERYD_PREFETCH_MULTIPLIER = 1  # 预取任务数量

# session 设置
SESSION_COOKIE_AGE = 3600 * 24 * 10  # Session的cookie失效日期(10天)
ESSION_SAVE_EVERY_REQUEST = True  # 关闭浏览器使得Session过期
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 每次请求都保存Session

