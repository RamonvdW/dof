# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.conf import settings
from django.db import models
from Account.models import Account
from Mailer.models import Inbox
from uuid import uuid5, NAMESPACE_URL
import os


TALEN = (
    ('NL', 'Nederlands'),
    ('EN', 'Engels'),
    ('DU', 'Duits'),
    ('FR', 'Frans'),
    ('SE', 'Zweeds'),
    ('TR', 'Turks'),
)

uuid_namespace = uuid5(NAMESPACE_URL, 'DOF.Producten.models')


class Product(models.Model):

    """ definitie van een product """

    # van wie is het product
    eigenaar = models.ForeignKey(Account, on_delete=models.CASCADE)

    # voor in de lijst
    korte_beschrijving = models.CharField(max_length=100, default='', blank=True)

    # in welke taal is dit bericht
    taal = models.CharField(max_length=2, choices=TALEN, default=TALEN[0][0])

    # naam van het bestand (niet het pad, alleen de naam)
    naam_bestand = models.CharField(max_length=100, default='', blank=True)

    # wanneer aangemaakt
    aangemaakt_op = models.DateTimeField(auto_now_add=True)      # automatisch invullen

    # handmatig vrijgeven van levering?
    handmatig_vrijgeven = models.BooleanField(default=True)

    # strings waarop dit product kunnen matchen in de order fulfillment e-mail
    match_1 = models.CharField(max_length=100, default='', blank=True)
    match_2 = models.CharField(max_length=100, default='', blank=True)
    match_3 = models.CharField(max_length=100, default='', blank=True)
    match_4 = models.CharField(max_length=100, default='', blank=True)
    match_5 = models.CharField(max_length=100, default='', blank=True)
    match_6 = models.CharField(max_length=100, default='', blank=True)
    match_7 = models.CharField(max_length=100, default='', blank=True)
    match_8 = models.CharField(max_length=100, default='', blank=True)
    match_9 = models.CharField(max_length=100, default='', blank=True)

    # TODO: log toevoegen?

    def __str__(self):
        """ Lever een tekstuele beschrijving van een database record, voor de admin interface """
        return "Product '%s' [%s] (van %s)" % (self.korte_beschrijving,
                                               self.taal,
                                               self.eigenaar.username)

    def is_match(self, regel):
        for match in (self.match_1, self.match_2, self.match_3, self.match_4, self.match_5):
            if len(match) > 0:
                if regel.find(match) >= 0:
                    return True
                # for
        # for
        return False

    class Meta:
        """ meta data voor de admin interface """
        verbose_name = "Product"
        verbose_name_plural = "Producten"

    objects = models.Manager()      # for the editor only


def get_path_to_product_bestand(prod):
    """ retourneer het volledige pad naar het bestand """
    naam = prod.naam_bestand.split('/')[-1]  # verwijder pad voor veiligheid
    fpath = os.path.join(settings.DOF_FILE_STORE,
                         prod.eigenaar.username,
                         'prod-%s' % prod.pk,
                         naam)
    return fpath, naam


class Opdracht(models.Model):

    """ definitie van 1 ontvangen opdracht tot levering """

    # voor wie is deze opdracht?
    eigenaar = models.ForeignKey(Account, on_delete=models.CASCADE)

    # wanneer aangemaakt?
    aangemaakt_op = models.DateTimeField(auto_now_add=True)      # automatisch invullen

    # aan wie te leveren
    to_email = models.CharField(max_length=250, default='')
    to_naam = models.CharField(max_length=100, default='')

    # onderwerp voor de email
    subject = models.CharField(max_length=100, default='')

    # de ontvangen mail body met de opdracht
    mail_body = models.TextField()

    # gekoppelde producten
    producten = models.ManyToManyField(Product, blank=True)

    # vrijgegeven voor levering?
    is_vrijgegeven_voor_levering = models.BooleanField(default=False)

    # is het product gedownload?
    is_afgehandeld = models.BooleanField(default=False)

    # gemaakt uit welke binnenkomende mail?
    bron = models.ForeignKey(Inbox, on_delete=models.SET_NULL, null=True, blank=True)

    # regels met bestelling-details die in de mail gevonden zijn
    regels = models.TextField(default='', blank=True)

    def __str__(self):
        """ Lever een tekstuele beschrijving van een database record, voor de admin interface """
        msg = "[%s] Opdracht voor %s aan %s" % (self.aangemaakt_op,
                                                self.eigenaar.username,
                                                self.to_email)
        if self.is_afgehandeld:
            msg += ' (afgehandeld)'
        else:
            if self.is_vrijgegeven_voor_levering:
                msg += ' (vrijgegeven, nog niet afgehandeld)'
            else:
                msg += ' (nog niet vrijgegeven)'

        return msg

    class Meta:
        """ meta data voor de admin interface """
        verbose_name = "Opdracht"
        verbose_name_plural = "Opdrachten"

    objects = models.Manager()      # for the editor only


class Levering(models.Model):

    """ definitie van 1 levering van een product """

    # wanneer aangemaakt
    aangemaakt_op = models.DateTimeField(auto_now_add=True)      # automatisch invullen

    # download code
    url_code = models.CharField(max_length=32, default='')

    # hoort bij welke opdracht?
    # SET_NULL laat de opdrachten opruimen en de download bestaan
    opdracht = models.ForeignKey(Opdracht, on_delete=models.SET_NULL, null=True, blank=True)

    # welk product is geleverd?
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # van wie is het product
    eigenaar = models.ForeignKey(Account, on_delete=models.CASCADE)

    # aan wie geleverd
    to_email = models.CharField(max_length=250, default='')

    # aantal keer gedownload
    download_count = models.PositiveIntegerField(default=0)

    # geblokkeerd?
    is_geblokkeerd = models.BooleanField(default=False)

    def __str__(self):
        """ Lever een tekstuele beschrijving van een database record, voor de admin interface """
        return "[%s] Levering van '%s' (van %s) aan %s" % (self.aangemaakt_op,
                                                           self.product.korte_beschrijving,
                                                           self.eigenaar.username,
                                                           self.to_email)

    def maak_url_code(self):
        # voeg argumenten toe om het uniek te maken
        args = {'datum': str(self.aangemaakt_op),
                'eigenaar': self.eigenaar.username,
                'opdracht': self.opdracht.pk,
                'product': self.product.korte_beschrijving,
                'email': self.to_email}
        self.url_code = uuid5(uuid_namespace, repr(args)).hex

    class Meta:
        """ meta data voor de admin interface """
        verbose_name = "Levering"
        verbose_name_plural = "Leveringen"

    objects = models.Manager()      # for the editor only


class BerichtTemplate(models.Model):

    # van wie is de template
    eigenaar = models.ForeignKey(Account, on_delete=models.CASCADE)

    # in welke taal is dit bericht
    taal = models.CharField(max_length=2, choices=TALEN)

    # onderwerp voor de email
    subject = models.CharField(max_length=100, default='')

    # intro
    singular = models.TextField()

    # outro
    plural = models.TextField()

    def __str__(self):
        return "[%s] %s" % (self.eigenaar.get_first_name(), self.taal)

    class Meta:
        """ meta data voor de admin interface """
        verbose_name = "Bericht template"


# end of file
