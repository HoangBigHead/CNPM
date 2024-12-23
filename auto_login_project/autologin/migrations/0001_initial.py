# Generated by Django 4.2.7 on 2024-12-03 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteCredentials',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('username_field_id', models.CharField(max_length=255)),
                ('password_field_id', models.CharField(max_length=255)),
                ('login_button_id', models.CharField(max_length=255)),
            ],
        ),
    ]
