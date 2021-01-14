# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models
from Account.models import Account
from Mailer.models import Inbox


class Product(models.Model):

    """ definitie van een product """

    # van wie is het product
    eigenaar = models.ForeignKey(Account, on_delete=models.CASCADE)

    # voor in de lijst
    korte_beschrijving = models.CharField(max_length=100, default='', blank=True)

    # naam van het bestand (niet het pad, alleen de naam)
    naam_bestand = models.CharField(max_length=100, default='', blank=True)

    # wanneer aangemaakt
    aangemaakt_op = models.DateTimeField(auto_now_add=True)      # automatisch invullen

    # handmatig vrijgeven van levering?
    handmatig_vrijgeven = models.BooleanField(default=False)

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
        return "Product '%s' (van %s)" % (self.korte_beschrijving, self.eigenaar.username)

    def is_match(self, lines):
        for match in (self.match_1, self.match_2, self.match_3, self.match_4, self.match_5):
            if len(match) > 0:
                for line in lines:
                    if line.find(match) >= 0:
                        return True
                # for
        # for
        return False

    class Meta:
        """ meta data voor de admin interface """
        verbose_name = "Product"
        verbose_name_plural = "Producten"

    objects = models.Manager()      # for the editor only


class Opdracht(models.Model):

    """ definitie van 1 ontvangen opdracht tot levering """

    # voor wie is deze opdracht?
    eigenaar = models.ForeignKey(Account, on_delete=models.CASCADE)

    # wanneer aangemaakt?
    aangemaakt_op = models.DateTimeField(auto_now_add=True)      # automatisch invullen

    # aan wie te leveren
    to_email = models.CharField(max_length=250, default='')

    # de ontvangen mail body met de opdracht
    mail_body = models.TextField()

    # gekoppelde producten
    producten = models.ManyToManyField(Product, blank=True)

    # vrijgegeven voor levering?
    is_vrijgegeven_voor_levering = models.BooleanField(default=False)

    # afgehandeld?
    is_afgehandeld = models.BooleanField(default=False)

    # gemaakt uit welke binnenkomende mail?
    bron = models.ForeignKey(Inbox, on_delete=models.SET_NULL, null=True, blank=True)

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

    # hoort bij welke opdracht?
    opdracht = models.ForeignKey(Opdracht, on_delete=models.SET_NULL, null=True, blank=True)

    # welk product is geleverd?
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # van wie is het product
    eigenaar = models.ForeignKey(Account, on_delete=models.CASCADE)

    # aan wie geleverd
    to_email = models.CharField(max_length=250, default='')

    def __str__(self):
        """ Lever een tekstuele beschrijving van een database record, voor de admin interface """
        return "[%s] Levering van '%s' (van %s) aan %s" % (self.aangemaakt_op,
                                                           self.product.korte_beschrijving,
                                                           self.eigenaar.username,
                                                           self.to_email)

    class Meta:
        """ meta data voor de admin interface """
        verbose_name = "Levering"
        verbose_name_plural = "Leveringen"

    objects = models.Manager()      # for the editor only

# end of file
