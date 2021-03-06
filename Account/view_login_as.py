# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2020 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.shortcuts import render
from django.urls import reverse, Resolver404
from django.contrib.auth import login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.db.models import Q, Value
from django.db.models.functions import Concat
from .forms import ZoekAccountForm, KiesAccountForm
from .models import Account, AccountEmail
from .rechten import account_rechten_otp_controle_gelukt, account_rechten_login_gelukt
from .view_login import account_plugins_login
from Overig.tijdelijke_url import (set_tijdelijke_url_receiver,
                                   RECEIVER_ACCOUNT_WISSEL,
                                   maak_tijdelijke_url_accountwissel)
from Logboek.models import schrijf_in_logboek
from Overig.helpers import get_safe_from_ip
import logging


TEMPLATE_LOGIN_AS_ZOEK = 'account/login-as-zoek.dtl'
TEMPLATE_LOGIN_AS_GO = 'account/login-as-go.dtl'

my_logger = logging.getLogger('DOF.Account')


def receiver_account_wissel(request, obj):
    """ Met deze functie kan een geautoriseerd persoon tijdelijk inloggen op de site
        als een andere gebruiker.
            obj is een AccountEmail object.
        We moeten een url teruggeven waar een http-redirect naar gedaan kan worden.
    """
    account = obj.account

    old_last_login = account.last_login

    # integratie met de authenticatie laag van Django
    login(request, account)

    from_ip = get_safe_from_ip(request)
    my_logger.info('%s LOGIN automatische inlog met account %s' % (from_ip, repr(account.username)))

    for _, func in account_plugins_login:
        httpresp = func(request, from_ip, account)
        if httpresp:
            # plugin has decided that the user may not login
            # and has generated/rendered an HttpResponse that we cannot handle here
            return httpresp

    if account.otp_is_actief:
        # fake de OTP passage
        account_rechten_otp_controle_gelukt(request)
    else:
        account_rechten_login_gelukt(request)

    # herstel de last_login van de echte gebruiker
    account.last_login = old_last_login
    account.save(update_fields=['last_login'])

    # gebruiker mag NIET aangemeld blijven
    # zorg dat de session-cookie snel verloopt
    request.session.set_expiry(0)

    # schrijf in het logboek
    schrijf_in_logboek(account=None,
                       gebruikte_functie="Inloggen",
                       activiteit="Automatische inlog als gebruiker %s vanaf IP %s" % (repr(account.username), from_ip))

    return reverse('Plein:plein')


set_tijdelijke_url_receiver(RECEIVER_ACCOUNT_WISSEL, receiver_account_wissel)


class LoginAsZoekView(UserPassesTestMixin, ListView):

    """ Deze view laat Wissel van Rol toe naar een gekozen gebruiker
        zodat de website 'door de ogen van' deze gebruiker bekeken kan worden
    """

    template_name = TEMPLATE_LOGIN_AS_ZOEK

    def test_func(self):
        """ called by the UserPassesTestMixin to verify the user has permissions to use this view """
        # deze functie wordt gebruikt voordat de GET of de POST afgehandeld wordt (getest bewezen)
        account = self.request.user
        if account.is_authenticated:
            return account.is_staff
        return False

    def handle_no_permission(self):
        """ gebruiker heeft geen toegang --> doe alsof dit niet bestaat """
        raise Resolver404()

    def get_queryset(self):
        """ called by the template system to get the queryset or list of objects for the template """

        self.form = ZoekAccountForm(self.request.GET)
        self.form.full_clean()  # vult cleaned_data

        zoekterm = self.form.cleaned_data['zoekterm']
        if len(zoekterm) >= 2:  # minimaal twee tekens van de naam/nummer
            self.zoekterm = zoekterm
            qset = (Account
                    .objects
                    .exclude(is_staff=True)
                    .annotate(hele_naam=Concat('first_name', Value(' '), 'last_name'))
                    .filter(Q(username__icontains=zoekterm) |  # dekt nhb_nr
                            Q(first_name__icontains=zoekterm) |
                            Q(last_name__icontains=zoekterm) |
                            Q(hele_naam__icontains=zoekterm))
                    .order_by('username'))
            return qset[:50]

        self.zoekterm = ""
        return None

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)
        context['url'] = reverse('Account:account-wissel')
        context['zoekterm'] = self.zoekterm
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        """ deze functie wordt aangeroepen als een POST request ontvangen is.
            dit is gekoppeld aan het drukken op de Selecteer knop.
        """
        form = KiesAccountForm(request.POST)
        form.full_clean()  # vult cleaned_data
        account_pk = form.cleaned_data.get('selecteer')

        try:
            accountemail = AccountEmail.objects.get(account__pk=account_pk)
        except AccountEmail.DoesNotExist:
            raise Resolver404()

        # prevent upgrade
        if accountemail.account.is_staff:
            raise Resolver404()

        context = dict()
        context['account'] = accountemail.account

        # schrijf de intentie in het logboek
        schrijf_in_logboek(account=self.request.user,
                           gebruikte_functie="Inloggen",
                           activiteit="Wissel naar account %s" % repr(accountemail.account.username))

        # maak een tijdelijke URL aan waarmee de inlog gedaan kan worden
        url = maak_tijdelijke_url_accountwissel(accountemail, naar_account=accountemail.account.username)
        context['login_as_url'] = url
        return render(self.request, TEMPLATE_LOGIN_AS_GO, context)


# end of file
