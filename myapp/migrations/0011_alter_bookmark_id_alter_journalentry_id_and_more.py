# Generated by Django 4.2.7 on 2025-01-06 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_prayer_user_alter_prayer_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmark',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='like',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='prayer',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='prayertime',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]