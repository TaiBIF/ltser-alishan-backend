from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0026_birdnetsound_data_hash_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="biosound",
            name="data_hash",
            field=models.CharField(db_index=True, default="", max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="cameratrap",
            name="data_hash",
            field=models.CharField(db_index=True, default="", max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="plantphenology",
            name="data_hash",
            field=models.CharField(db_index=True, default="", max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="terresoundindex",
            name="data_hash",
            field=models.CharField(db_index=True, default="", max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="weather",
            name="data_hash",
            field=models.CharField(db_index=True, default="", max_length=64),
            preserve_default=False,
        ),
    ]
