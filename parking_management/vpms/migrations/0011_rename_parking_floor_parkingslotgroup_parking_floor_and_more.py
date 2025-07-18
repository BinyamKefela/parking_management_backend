# Generated by Django 5.1.7 on 2025-05-27 08:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vpms', '0010_owner_company_address_owner_company_email_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='parkingslotgroup',
            old_name='Parking_floor',
            new_name='parking_floor',
        ),
        migrations.AlterField(
            model_name='parkingslot_vehicletype',
            name='parking_slot',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='vpms.parkingslot'),
        ),
        migrations.CreateModel(
            name='FavoriteZones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parking_zone', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='vpms.parkingzone')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ZoneUtitlities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wifi', models.BooleanField(default=False)),
                ('cctv', models.BooleanField(default=False)),
                ('charger', models.BooleanField(default=False)),
                ('parking_zone', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='vpms.parkingzone')),
            ],
        ),
    ]
