# Generated by Django 4.1.7 on 2023-04-18 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0023_sectionhorizontalrule_padding_top"),
    ]

    operations = [
        migrations.AddField(
            model_name="sectionamendproperty",
            name="show_form_name",
            field=models.BooleanField(
                default=True,
                help_text="Cocher cette option affiche le nom du formulaire (objet et type de demande)",
                verbose_name="Afficher le nom du formulaire",
            ),
        ),
        migrations.AddField(
            model_name="sectionamendproperty",
            name="undesired_properties",
            field=models.CharField(
                blank=True,
                help_text="Liste de champs à masquer, séparés par des points virgules ';' correspondant aux titre des champs (ex: hauteur;largeur)",
                max_length=2000,
                null=True,
                verbose_name="Nom de champs a masquer",
            ),
        ),
    ]