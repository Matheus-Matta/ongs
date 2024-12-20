# Generated by Django 4.2.9 on 2024-11-30 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_post_likes_alter_post_event_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='typeuser',
            field=models.CharField(choices=[('volunteer', 'Voluntário'), ('organization', 'Organização')], default='volunteer', max_length=15),
        ),
    ]
