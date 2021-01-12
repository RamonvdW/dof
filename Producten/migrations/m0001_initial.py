# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.conf import settings
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
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('korte_beschrijving', models.CharField(default='', max_length=100)),
                ('naam_bestand', models.CharField(default='', max_length=100)),
                ('aangemaakt_op', models.DateTimeField(auto_now_add=True)),
                ('handmatig_vrijgeven', models.BooleanField(default=False)),
                ('match_1', models.CharField(default='', max_length=100)),
                ('match_2', models.CharField(default='', max_length=100)),
                ('match_3', models.CharField(default='', max_length=100)),
                ('match_4', models.CharField(default='', max_length=100)),
                ('match_5', models.CharField(default='', max_length=100)),
                ('match_6', models.CharField(default='', max_length=100)),
                ('match_7', models.CharField(default='', max_length=100)),
                ('match_8', models.CharField(default='', max_length=100)),
                ('match_9', models.CharField(default='', max_length=100)),
                ('eigenaar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Producten',
            },
        ),
        migrations.CreateModel(
            name='Opdracht',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aangemaakt_op', models.DateTimeField(auto_now_add=True)),
                ('to_email', models.CharField(default='', max_length=250)),
                ('mail_body', models.TextField()),
                ('is_vrijgegeven_voor_levering', models.BooleanField(default=False)),
                ('is_afgehandeld', models.BooleanField(default=False)),
                ('eigenaar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('producten', models.ManyToManyField(to='Producten.Product')),
            ],
            options={
                'verbose_name': 'Opdracht',
                'verbose_name_plural': 'Opdrachten',
            },
        ),
        migrations.CreateModel(
            name='Levering',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aangemaakt_op', models.DateTimeField(auto_now_add=True)),
                ('to_email', models.CharField(default='', max_length=250)),
                ('eigenaar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('opdracht', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Producten.Opdracht')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Producten.Product')),
            ],
            options={
                'verbose_name': 'Levering',
                'verbose_name_plural': 'Leveringen',
            },
        ),
    ]

# end of file
