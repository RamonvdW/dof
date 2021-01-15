# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

"""
Django settings for the NhbApps project.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# import install-specific settings from a separate file
# that is easy to replace as part of the deployment process
from dof.settings_local import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJ_DIR)

# version of the site
# this is used to keep site feedback separated by version
SITE_VERSIE = '2021-01-15'

# modules van de site
INSTALLED_APPS = [
    'Beheer.apps.BeheerConfig',        # replaces admin
    'Account.apps.AccountConfig',
    'Functie.apps.FunctieConfig',
    'Logboek.apps.LogboekConfig',
    'Mailer.apps.MailerConfig',
    'Overig.apps.OverigConfig',
    'Plein.apps.PleinConfig',
    'Producten.apps.ProductenConfig',
    'django.contrib.staticfiles',      # gather static files from modules helper
    'django.contrib.sessions',         # support for database-backed sessions; needed for logged-in user
    'django.contrib.admin',            # see-all/fix-all admin pages
    'django.contrib.auth',             # authenticatie framework
    'django.contrib.contenttypes',     # permission association to models
    'django.contrib.messages',
    # 'django_extensions'              # very useful for show_urls
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',                # security (https improvements)
    'django.contrib.sessions.middleware.SessionMiddleware',         # manage sessions across requests
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',                    # security (cross-site request forgery)
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',       # security
]


# gebruik ingebouwde authenticatie / login laag
# inclusief permissions en groepen
# levert ook de integratie met sessies
# en het niet accepteren van oude sessies na wachtwoord wijziging
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend'
]


# vervanger van (aanpassing/uitbreiding op) de ingebouwde User
AUTH_USER_MODEL = 'Account.Account'

# maximum aantal keer dat een verkeerd wachtwoord opgegeven mag worden
# voor een account (login of wijzig-wachtwoord) voor het geblokkeerd wordt
AUTH_BAD_PASSWORD_LIMIT = 5
AUTH_BAD_PASSWORD_LOCKOUT_MINS = 15


# templates (django template language) processors
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [ str(APPS_DIR.path('templates')), ],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',      # permission checking
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', ['dof.minify_dtl.Loader']),
            ],
        },
    },
]


# point out location of WSGI application for django runserver command
WSGI_APPLICATION = 'dof.wsgi.application'

# let browsers remember to connect with https
# security analysis recommends at least 180 days
SECURE_HSTS_SECONDS = 17280000      # 17280000 = 200 days


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/2.2/topics/i18n/
# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'nl-NL'     # provides wanted date/time output format
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True

# format localization
USE_L10N = True

# sla alle datums in de database op als UTC
# dit doet PostgreSQL sowieso, onafhankelijk van deze instelling
# alleen vertalen bij presentatie naar de gebruiker toe
USE_TZ = True


# top-level URL verdeling naar apps
ROOT_URLCONF = 'dof.urls'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'     # url
STATIC_ROOT = 'dof/.static'     # relative to project top-dir
STATICFILES_DIRS = [
    os.path.join(PROJ_DIR, "compiled_static"),
]
STATICFILES_FINDER = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
]


# wordt gebruikt door LoginView als er geen 'next' veld bij de POST zit
# LOGIN_REDIRECT_URL = '/plein/'

# wordt gebruikt door de permission_required decorator en UserPassesTextMixin
# om de gebruiker door te sturen als een view geen toegang verleend
LOGIN_URL = '/account/login/'


# for debug_toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]


# logging to syslog
# zie https://docs.djangoproject.com/en/3.0/topics/logging/
# en  https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[django] %(asctime)s %(name)s [%(levelname)s] %(message)s",
            'datefmt': "%Y-%b-%d %H:%M:%S"
        }
    },
    'handlers': {
        'syslog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'verbose',
            'facility': 'user',
            'address': '/dev/log'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['syslog'],
            'level': 'ERROR'
        },
        'saml2': {
            'handlers': ['syslog'],
            'level': 'WARNING'
        },
        'djangosaml2idp': {
            'handlers': ['syslog'],
            'level': 'WARNING'
        },
        '': {
            'handlers': ['syslog'],
            'level': 'DEBUG'
        }
    }
}


BACKGROUND_SYNC_POORT = 3000
BACKGROUND_SYNC__VERWERK_OPDRACHTEN = BACKGROUND_SYNC_POORT + 1


# defaults for 'dev' and 'test' options

# SECURITY WARNING: don't run with debug turned on in production!
# let op: zonder DEBUG=True geen static files in dev omgeving!
DEBUG = False

# HTML validation using v.Nu (see Overig/e2ehelpers.py)
TEST_VALIDATE_HTML = False

# end of file
