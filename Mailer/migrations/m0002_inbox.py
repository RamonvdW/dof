# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations, models


class Migration(migrations.Migration):

    """ Migratie class voor dit deel van de applicatie """

    # volgorde afdwingen
    dependencies = [
        ('Mailer', 'm0001_initial'),
    ]

    # migratie functies
    operations = [
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aangemaakt_op', models.DateTimeField(auto_now_add=True)),
                ('is_verwerkt', models.BooleanField(default=False)),
                ('mail_text', models.TextField()),
            ],
            options={
                'verbose_name': 'Mail inbox',
                'verbose_name_plural': 'Mail inbox',
            },
        ),
    ]

# end of file
