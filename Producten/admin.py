# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from .models import Product, Opdracht, Levering, BerichtTemplate


class ProductAdmin(admin.ModelAdmin):

    # velden om in te zoeken (in de lijst)
    search_fields = ('korte_beschrijving',)

    list_filter = ('eigenaar__username',)

    readonly_fields = ('aangemaakt_op',)

    list_select_related = ('eigenaar',)


class OpdrachtAdmin(admin.ModelAdmin):

    list_select_related = ('eigenaar',)


class LeveringAdmin(admin.ModelAdmin):

    list_select_related = ('eigenaar',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Opdracht, OpdrachtAdmin)
admin.site.register(Levering, LeveringAdmin)
admin.site.register(BerichtTemplate)

# end of file
