# Generated by Django 3.1.4 on 2020-12-10 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UI', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fencer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('weapon', models.CharField(choices=[('E', 'Epee'), ('S', 'Sabre'), ('F', 'Foil')], max_length=1)),
                ('rating', models.CharField(blank=True, max_length=1)),
            ],
        ),
    ]