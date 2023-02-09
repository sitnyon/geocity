# Generated by Django 4.1.4 on 2022-12-19 16:27

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0017_sectionparagraphright"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sectionparagraph",
            name="content",
            field=ckeditor.fields.RichTextField(
                help_text='Il est possible d\'inclure des variables et de la logique avec la <a href="https://jinja.palletsprojects.com/en/3.1.x/templates/">syntaxe Jinja</a>. Les variables de la demande sont accessible dans `{{request_data}}`, celles du formulaire dans `{{form_data}}`, celles des transactions dans `{{transaction_data}}`.',
                verbose_name="Contenu",
            ),
        ),
        migrations.AlterField(
            model_name="sectionparagraphright",
            name="content",
            field=ckeditor.fields.RichTextField(
                help_text='Il est possible d\'inclure des variables et de la logique avec la <a href="https://jinja.palletsprojects.com/en/3.1.x/templates/">syntaxe Jinja</a>. Les variables de la demande sont accessible dans `{{request_data}}`, celles du formulaire dans `{{form_data}}`, celles des transactions dans `{{transaction_data}}`.',
                verbose_name="Contenu",
            ),
        ),
    ]