# Generated by Django 2.2.13 on 2020-11-02 14:10

from django.db import migrations

STATUS_DRAFT = 0
STATUS_SUBMITTED_FOR_VALIDATION = 1
STATUS_APPROVED = 2
STATUS_PROCESSING = 3
STATUS_AWAITING_SUPPLEMENT = 4
STATUS_AWAITING_VALIDATION = 5
STATUS_REJECTED = 6
STATUS_RECEIVED = 7


STATUS_CHOICES = (
    (STATUS_DRAFT, "Brouillon"),
    (STATUS_SUBMITTED_FOR_VALIDATION, "Envoyée, en attente de traitement"),
    (STATUS_AWAITING_SUPPLEMENT, "Demande de compléments"),
    (STATUS_PROCESSING, "En traitement"),
    (STATUS_AWAITING_VALIDATION, "En validation"),
    (STATUS_APPROVED, "Approuvée"),
    (STATUS_REJECTED, "Refusée"),
    (STATUS_RECEIVED, "Annonce réceptionnée"),
)


def insert_workflow_status(apps, schema_editor):
    """
    Insert values in PermitWorkflowStatus model from models.PermitRequest.STATUS_CHOICES values
    """
    for status_value in STATUS_CHOICES:

        AdministrativeEntity = apps.get_model("permits", "PermitAdministrativeEntity")
        PermitWorkflowStatus = apps.get_model("permits", "PermitWorkflowStatus")

        for entity in AdministrativeEntity.objects.all():
            PermitWorkflowStatus.objects.get_or_create(
                status=status_value[0], administrative_entity=entity
            )


class Migration(migrations.Migration):

    dependencies = [
        ("permits", "0003_permitworkflowstatus"),
    ]

    operations = [
        migrations.RunPython(insert_workflow_status),
    ]