# Generated by Django 4.2.1 on 2023-06-20 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0020_map_widget_configuration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="field",
            name="input_type",
            field=models.CharField(
                choices=[
                    ("title_output", "Titre à afficher"),
                    ("text_output", "Texte à afficher"),
                    ("address", "Adresse"),
                    ("checkbox", "Case à cocher"),
                    ("list_multiple", "Choix multiple"),
                    ("list_single", "Choix simple"),
                    ("date", "Date"),
                    ("file", "Fichier"),
                    ("file_download", "Fichier (à télécharger)"),
                    ("number", "Nombre"),
                    ("text", "Texte"),
                    ("regex", "Texte (regex)"),
                ],
                max_length=30,
                verbose_name="type de caractéristique",
            ),
        ),
    ]
