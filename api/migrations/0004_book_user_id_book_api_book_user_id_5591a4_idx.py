# Generated by Django 5.1.3 on 2024-11-25 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_page_book'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='user_id',
            field=models.CharField(default='default_user', max_length=100),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['user_id', '-last_edited'], name='api_book_user_id_5591a4_idx'),
        ),
    ]
