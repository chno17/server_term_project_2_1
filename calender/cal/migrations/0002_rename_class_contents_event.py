# Generated by Django 5.2.1 on 2025-06-14 12:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='class_contents',
            new_name='Event',
        ),
    ]
