# Generated by Django 4.2.1 on 2023-06-15 16:21

from django.db import migrations


class Migration(migrations.Migration):
    def update_sectionparagraph(apps, schema_editor):

        SectionParagraph = apps.get_model("reports", "SectionParagraph")
        html_embed_open = '<div class="raw-html-embed">'
        html_embed_close = "</div>"

        # Update sections containing "div" or "class" or "table"
        sections_with_keywords = (
            SectionParagraph.objects.filter(content__contains="<div")
            | SectionParagraph.objects.filter(content__contains="class=")
            | SectionParagraph.objects.filter(content__contains="<table")
        )

        for section in sections_with_keywords:
            section.content = f"{html_embed_open}{section.content}{html_embed_close}"
            section.save(update_fields=["content"])

    dependencies = [
        (
            "reports",
            "0031_alter_sectionrecipient_first_recipient_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(update_sectionparagraph),
    ]