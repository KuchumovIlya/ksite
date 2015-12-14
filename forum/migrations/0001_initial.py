# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('message_text', models.CharField(max_length=200)),
                ('publication_date', models.DateTimeField(verbose_name='publication date')),
                ('topic_id', models.IntegerField()),
                ('message_id', models.IntegerField()),
                ('user_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('section_name', models.CharField(max_length=200)),
                ('section_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('topic_name', models.CharField(max_length=200)),
                ('topic_id', models.IntegerField()),
                ('section_id', models.IntegerField()),
                ('modification_date', models.DateTimeField(verbose_name='modification date')),
            ],
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=200)),
                ('confirming_token', models.CharField(max_length=200)),
                ('is_confirmed', models.BooleanField()),
            ],
        ),
    ]
