# Generated by Django 4.1 on 2022-09-14 22:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_post_liker'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='liker',
            new_name='likers',
        ),
    ]