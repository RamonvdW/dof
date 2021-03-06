# -*- coding: utf-8 -*-

#  Copyright (c) 2020 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    """ Migratie class voor dit deel van de applicatie """

    # dit is de eerste
    initial = True

    # volgorde afdwingen
    dependencies = [
        ('Account', 'm0001_squashed'),
    ]

    # migratie functies
    operations = [
        migrations.CreateModel(
            name='SiteFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('toegevoegd_op', models.DateTimeField()),
                ('site_versie', models.CharField(max_length=20)),
                ('gebruiker', models.CharField(max_length=50)),
                ('op_pagina', models.CharField(max_length=50)),
                ('bevinding', models.CharField(choices=[('8', 'Tevreden'), ('6', 'Bruikbaar'), ('4', 'Moet beter')], max_length=1)),
                ('is_afgehandeld', models.BooleanField(default=False)),
                ('feedback', models.TextField()),
            ],
            options={
                'verbose_name': 'Site feedback',
                'verbose_name_plural': 'Site feedback',
            },
        ),
        migrations.CreateModel(
            name='SiteTijdelijkeUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_code', models.CharField(max_length=32)),
                ('aangemaakt_op', models.DateTimeField()),
                ('geldig_tot', models.DateTimeField()),
                ('hoortbij_accountemail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Account.AccountEmail')),
                ('dispatch_to', models.CharField(default='', max_length=20)),
            ],
        ),
    ]

# end of file
