# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

"""
    Django local settings for the NhbApps project.

    This file is included from settings.py and contains specific
    settings that can be changed as part of a deployment, without
    having to edit the settings.py file.
"""

# the secret below ensures an adversary cannot fake aspects like a session-id
# just make sure it is unique per installation and keep it private
# details: https://docs.djangoproject.com/en/2.2/ref/settings/#secret-key
SECRET_KEY = '80dy=y4+nc_6gqa&@2j_6@^6ijvrs@nkv383omxo&%!i!ok69m'

# SITE_URL wordt gebruikt door Overige:tijdelijke urls
SITE_URL = "http://localhost:8000"

ALLOWED_HOSTS = [
    'localhost', 'forcie', '192.168.2.150',             # intern
]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dof',
        'USER': 'django',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

# the issuer name that is sent to the OTP application in the QR code
OTP_ISSUER_NAME = "test.st-visir.nl"

# end of file
