# Generated by Django 5.2.4 on 2025-07-14 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='status',
            field=models.CharField(choices=[('Active', 'Активний'), ('Inactive', 'Неактивний'), ('On_moderation', 'На модерації'), ('Closed', 'Закритий'), ('Archived', 'Архівний')], default='On_moderation', max_length=50),
        ),
    ]
