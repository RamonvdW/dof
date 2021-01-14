# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.shortcuts import redirect, render, reverse
from django.http import HttpResponseRedirect
from django.views.generic import View
from Account.rechten import account_rechten_is_otp_verified


TEMPLATE_PLEIN_BEZOEKER = 'plein/plein-bezoeker.dtl'    # niet ingelogd
TEMPLATE_PLEIN_2FA = 'plein/plein-2fa.dtl'              # 2FA controle na inlog
TEMPLATE_PLEIN_BEHEERDER = 'plein/plein-beheerder.dtl'  # beheerder
TEMPLATE_NIET_ONDERSTEUND = 'plein/niet-ondersteund.dtl'


def is_browser_supported(request):
    """ analyseer de User Agent header
        geef True terug als de browser ondersteund wordt
    """

    # minimal requirement is ECMAScript 2015 (ES6)
    # since most browsers have supported this since 2016/2017, we don't need to check the version
    # only filter out Internet Explorer

    is_supported = True

    try:
        useragent = request.META['HTTP_USER_AGENT']
    except KeyError:
        # niet aanwezig, dus kan geen analyse doen
        pass
    else:
        if " MSIE " in useragent:
            # Internal Explorer versie tm IE10: worden niet ondersteund
            is_supported = False
        elif "Trident/7.0; rv:11" in useragent:
            # Internet Explorer versie 11
            is_supported = False

    # wel ondersteund
    return is_supported


def site_root_view(request):
    """ simpele Django view functie om vanaf de top-level site naar het Plein te gaan """

    if not is_browser_supported(request):
        return redirect('Plein:niet-ondersteund')

    return redirect('Plein:plein')


class PleinView(View):
    """ Django class-based view voor het Plein """

    # class variables shared by all instances

    def get(self, request, *args, **kwargs):
        """ called by the template system to get the context data for the template """

        if not is_browser_supported(request):
            return redirect('Plein:niet-ondersteund')

        # zet alles goed voor bezoekers / geen rol
        template = TEMPLATE_PLEIN_BEZOEKER
        context = dict()

        if request.user.is_authenticated:
            account = request.user
            context['first_name'] = account.get_first_name()

            if account.otp_is_actief:
                if not account_rechten_is_otp_verified(request):
                    # eerste 2FA controle afdwingen
                    return HttpResponseRedirect(reverse('Functie:otp-controle'))
            else:
                context['toon_koppel_2fa'] = True

            # beheerder
            template = TEMPLATE_PLEIN_BEHEERDER

            if request.user.is_staff:
                context['rol_is_it'] = True

        return render(request, template, context)


class NietOndersteundView(View):

    """ Django class-based om te rapporteren dat de browser niet ondersteund wordt """

    # class variables shared by all instances
    template_name = TEMPLATE_NIET_ONDERSTEUND

    def get(self, request, *args, **kwargs):
        context = dict()
        return render(request, self.template_name, context)


# end of file
