from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_record_validity_user_user_validity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='user_validity',
        ),
    ]
