import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0002_rename_spanish_to_english'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ['order']},
        ),
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together={('course', 'order')},
        ),
        migrations.AddField(
            model_name='lesson',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

