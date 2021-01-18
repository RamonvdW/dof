# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.shortcuts import reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, TemplateView, View
from django import forms
from django.urls import Resolver404
from django.http import HttpResponseRedirect
from .models import Product, TALEN, get_path_to_product_bestand
from types import SimpleNamespace
import logging
import os.path


TEMPLATE_PRODUCTEN = 'producten/producten.dtl'
TEMPLATE_WIJZIG_PRODUCT = 'producten/product-wijzig.dtl'

my_logger = logging.getLogger('DOF.Producten')


class ProductenView(UserPassesTestMixin, ListView):

    """ Django class-based view voor de activiteiten van de gebruikers """

    # class variables shared by all instances
    template_name = TEMPLATE_PRODUCTEN

    # TODO: pagination support
    # TODO: zoek/filter mogelijkheden

    def test_func(self):
        """ called by the UserPassesTestMixin to verify the user has permissions to use this view """
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        """ gebruiker heeft geen toegang --> redirect naar het plein """
        return HttpResponseRedirect(reverse('Plein:plein'))

    def _make_link_urls(self, context):
        # voorbereidingen voor een regel met volgende/vorige links
        # en rechtstreekse links naar een 10 pagina's
        links = list()

        num_pages = context['paginator'].num_pages
        page_nr = context['page_obj'].number

        # previous
        if page_nr > 1:
            tup = ('vorige', self.base_url + '?page=%s' % (page_nr - 1))
            links.append(tup)
        else:
            tup = ('vorige_disable', '')
            links.append(tup)

        # block van 10 pagina's; huidige pagina in het midden
        range_start = page_nr - 5
        range_end = range_start + 9
        if range_start < 1:
            range_end += (1 - range_start)  # 1-0=1, 1--1=2, 1--2=3, etc.
            range_start = 1
        if range_end > num_pages:
            range_end = num_pages
        for pgnr in range(range_start, range_end+1):
            tup = ('%s' % pgnr, self.base_url + '?page=%s' % pgnr)
            links.append(tup)
        # for

        # TODO: zet self.base_url

        # next
        if page_nr < num_pages:
            tup = ('volgende', self.base_url + '?page=%s' % (page_nr + 1))
            links.append(tup)
        else:
            tup = ('volgende_disable', '')
            links.append(tup)

        return links

    def get_queryset(self):
        if self.request.user.is_staff:
            qset = (Product
                    .objects
                    .order_by('-aangemaakt_op'))
        else:
            qset = (Product
                    .objects
                    .filter(eigenaar=self.request.user)
                    .order_by('-aangemaakt_op'))

        for prod in qset:
            prod.url_wijzig = reverse('Producten:wijzig-product',
                                      kwargs={'product_pk': prod.pk})

            prod.taal_lang = prod.taal
            for code, taal_lang in TALEN:
                if prod.taal == code:
                    prod.taal_lang = taal_lang
            # for
        # for

        return qset

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        if context['is_paginated']:
            context['page_links'] = self._make_link_urls(context)
            context['active'] = str(context['page_obj'].number)

        if self.request.user.is_staff:
            context['is_staff'] = True

        return context


class NieuwProductView(UserPassesTestMixin, View):

    """ Django class-based view voor het toevoegen van een product """

    def test_func(self):
        """ called by the UserPassesTestMixin to verify the user has permissions to use this view """
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        """ gebruiker heeft geen toegang --> redirect naar het plein """
        return HttpResponseRedirect(reverse('Plein:plein'))

    @staticmethod
    def post(request, *args, **kwargs):
        eigenaar = request.user

        product = Product(eigenaar=eigenaar)
        product.save()

        url = reverse('Producten:wijzig-product',
                      kwargs={'product_pk': product.pk})
        return HttpResponseRedirect(url)


class WijzigProductView(UserPassesTestMixin, TemplateView):

    """ Django class-based view voor het wijzigen van 1 product """

    # class variables shared by all instances
    template_name = TEMPLATE_WIJZIG_PRODUCT

    def test_func(self):
        """ called by the UserPassesTestMixin to verify the user has permissions to use this view """
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        """ gebruiker heeft geen toegang --> redirect naar het plein """
        return HttpResponseRedirect(reverse('Plein:plein'))

    @staticmethod
    def _get_talen(keuze):
        talen = list()
        for code, taal in TALEN:
            optie = SimpleNamespace()
            optie.code = code
            optie.taal = taal
            optie.actief = (keuze == optie.code)
            talen.append(optie)
        # for
        return talen

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            product_pk = int(kwargs['product_pk'][:6])                  # afkappen voor veiligheid
            if self.request.user.is_staff:
                product = Product.objects.get(pk=product_pk)
            else:
                product = Product.objects.get(pk=product_pk,
                                              eigenaar=self.request.user)   # alleen eigen producten
        except (ValueError, Product.DoesNotExist):
            raise Resolver404()

        context['product'] = product

        if product.handmatig_vrijgeven:
            context['check_2'] = True
        else:
            context['check_1'] = True

        context['url_terug'] = reverse('Producten:producten')

        context['url_opslaan'] = reverse('Producten:wijzig-product',
                                         kwargs={'product_pk': product.pk})

        context['talen'] = self._get_talen(product.taal)

        fpath, naam = get_path_to_product_bestand(product)
        context['bestandsnaam'] = naam
        if not os.path.exists(fpath):
            context['niet_gevonden'] = True

        context['url_upload'] = reverse('Producten:upload-bestand',
                                        kwargs={'product_pk': product.pk})

        if self.request.user.is_staff:
            context['is_staff'] = True

        return context

    def post(self, request, *args, **kwargs):
        try:
            product_pk = int(kwargs['product_pk'][:6])                  # afkappen voor veiligheid
            product = Product.objects.get(pk=product_pk,
                                          eigenaar=self.request.user)   # alleen eigen producten
        except (ValueError, Product.DoesNotExist):
            raise Resolver404()

        delete = request.POST.get('delete', None)
        if delete and delete == "ja":
            product.delete()
        else:
            try:
                product.korte_beschrijving = request.POST.get('kort', product.korte_beschrijving)[:100]

                taal = request.POST.get('taal', '')
                for code, _ in TALEN:
                    if taal == code:
                        product.taal = code
                        taal = None
                # for
                if taal is not None:
                    # illegal taal
                    raise Resolver404()

                product.match_1 = request.POST.get('match1', product.match_1)[:100]
                product.match_2 = request.POST.get('match2', product.match_2)[:100]
                product.match_3 = request.POST.get('match3', product.match_3)[:100]
                product.match_4 = request.POST.get('match4', product.match_4)[:100]
                product.match_5 = request.POST.get('match5', product.match_5)[:100]

                bevinding = request.POST.get('bevinding')
                product.handmatig_vrijgeven = (bevinding == '2')
            except KeyError:
                raise Resolver404()

            product.save()

        return HttpResponseRedirect(reverse('Producten:producten'))


class UploadView(UserPassesTestMixin, View):

    """ deze view ontvangt een file upload """

    def test_func(self):
        """ called by the UserPassesTestMixin to verify the user has permissions to use this view """
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        """ gebruiker heeft geen toegang --> redirect naar het plein """
        return HttpResponseRedirect(reverse('Producten:producten'))

    @staticmethod
    def post(request, *args, **kwargs):

        try:
            product_pk = int(kwargs['product_pk'][:6])            # afkappen voor veiligheid
            product = Product.objects.get(eigenaar=request.user,  # alleen eigen producten
                                          pk=product_pk)
        except Product.DoesNotExist:
            raise Resolver404()

        try:
            uploaded_file = request.FILES['bestand']
        except KeyError:
            raise Resolver404()

        old_fpath, _ = get_path_to_product_bestand(product)

        product.naam_bestand = uploaded_file.name
        fpath, _ = get_path_to_product_bestand(product)

        # maak het pad aan, indien nog niet aanwezig
        prod_dir = os.path.dirname(fpath)
        try:
            os.makedirs(prod_dir, exist_ok=True)
        except OSError as exc:
            my_logger.error('Aanmaken van directory %s voor product %s mislukt: %s' % (repr(prod_dir), product.pk, str(exc)))

        # sla het bestand op
        try:
            with open(fpath, 'wb') as target:
                for chunk in uploaded_file.chunks():
                    target.write(chunk)
                # for
        except OSError as exc:
            my_logger.error('Upload van %s voor product %s mislukt: %s' % (repr(fpath), product.pk, str(exc)))
        else:
            # upload gelukt
            product.save()
            my_logger.info('Upload van %s voor product %s gelukt' % (repr(fpath), product.pk))

            # verwijder het oude bestand, indien aanwezig
            if os.path.exists(old_fpath):
                try:
                    os.remove(old_fpath)
                except OSError as exc:
                    my_logger.error('Verwijderen van oude bestand %s voor product %s mislukt: %s' % (repr(old_fpath), product.pk, str(exc)))
                else:
                    my_logger.info('Verwijderen van oude bestand %s voor product %s gelukt' % (repr(old_fpath), product.pk))

        # terug naar de wijzig-product pagina
        url = reverse('Producten:wijzig-product', kwargs={'product_pk': product.pk})
        return HttpResponseRedirect(url)

# end of file
