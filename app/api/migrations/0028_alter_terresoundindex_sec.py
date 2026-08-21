from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0027_add_import_data_hash_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="terresoundindex",
            name="sec",
            field=models.FloatField(blank=True, help_text="錄音長度：秒數", null=True),
        ),
    ]
