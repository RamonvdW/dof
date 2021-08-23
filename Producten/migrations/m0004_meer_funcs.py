# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    """ Migratie class voor dit deel van de applicatie """

    # volgorde afdwingen
    dependencies = [
        ('Producten', 'm0003_allow_null'),
    ]

    # migratie functies
    operations = [
        migrations.AddField(
            model_name='product',
            name='taal',
            field=models.CharField(
                choices=[('NL', 'Nederlands'), ('EN', 'Engels'), ('DU', 'Duits'), ('FR', 'Frans'), ('SE', 'Zweeds'),
                         ('TU', 'Turks')], default='NL', max_length=2),
        ),
        migrations.AddField(
            model_name='opdracht',
            name='to_naam',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.CreateModel(
            name='BerichtTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taal', models.CharField(
                    choices=[('NL', 'Nederlands'), ('EN', 'Engels'), ('DU', 'Duits'), ('FR', 'Frans'), ('SE', 'Zweeds'),
                             ('TU', 'Turks')], max_length=2)),
                ('intro', models.TextField()),
                ('outro', models.TextField()),
                ('eigenaar',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bericht template',
            },
        ),
    ]

# end of file
