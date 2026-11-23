from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0029_iptcamtrapdeployment_iptcamtrapmedia_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="iptcamtrapobservation",
            name="classificationMethod",
            field=models.CharField(
                blank=True,
                choices=[("human", "human")],
                default="human",
                help_text="固定填入 human",
                max_length=32,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="iptcamtrapobservation",
            name="sex",
            field=models.CharField(
                blank=True,
                choices=[
                    ("male", "male"),
                    ("female", "female"),
                    ("hermaphrodite", "hermaphrodite"),
                    ("ambiguous", "ambiguous"),
                ],
                help_text="對應 Cameratrap.sex",
                max_length=16,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="iptcamtrapmedia",
            name="mediaID",
            field=models.CharField(
                help_text="由 Cameratrap.observationID 與 fileName 以底線連接；fileName 空值視為空字串",
                max_length=512,
                unique=True,
            ),
        ),
    ]
