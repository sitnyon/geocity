# Generated by Django 3.2.13 on 2022-05-17 12:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import permits.fields


class Migration(migrations.Migration):

    replaces = [('permits', '0065_permitrequestcomplementarydocument'), ('permits', '0066_auto_20220329_1641'), ('permits', '0067_permitrequestcomplementarydocument_document_type'), ('permits', '0068_alter_permitrequestcomplementarydocument_authorised_departments'), ('permits', '0069_historicalpermitrequestinquiry_permitrequestinquiry'), ('permits', '0070_auto_20220406_1421'), ('permits', '0071_delete_historicalpermitrequestinquiry'), ('permits', '0072_alter_permitrequestcomplementarydocument_document'), ('permits', '0073_archivedpermitrequest'), ('permits', '0074_auto_20220427_1644'), ('permits', '0075_alter_archivedpermitrequest_archived_date')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('permits', '0064_add_field_can_always_update_in_WorksObjectType'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermitRequestComplementaryDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='', verbose_name='Document')),
                ('description', models.TextField(blank=True, verbose_name='Description du document')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Provisoire'), (1, 'Final'), (2, 'Autre'), (3, 'Annulé')], verbose_name='Statut du document')),
                ('is_public', models.BooleanField(default=False, verbose_name='Public')),
                ('authorised_departments', models.ManyToManyField(to='permits.PermitDepartment', verbose_name='Département autorisé à visualiser le document')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Propriétaire du document')),
                ('permit_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='permits.permitrequest', verbose_name='Demande de permis')),
            ],
        ),
        migrations.CreateModel(
            name='ComplementaryDocumentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nom')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='permits.complementarydocumenttype', verbose_name='Type parent')),
                ('work_object_types', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='permits.worksobjecttype', verbose_name='Objets')),
            ],
        ),
        migrations.AddConstraint(
            model_name='complementarydocumenttype',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('parent__isnull', False), ('work_object_types__isnull', True)), models.Q(('parent__isnull', True), ('work_object_types__isnull', False)), _connector='OR'), name='Only parent types can be linked to a work object type'),
        ),
        migrations.AddField(
            model_name='permitrequestcomplementarydocument',
            name='document_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='permits.complementarydocumenttype', verbose_name='Type du document'),
        ),
        migrations.AlterField(
            model_name='permitrequestcomplementarydocument',
            name='authorised_departments',
            field=models.ManyToManyField(db_table='permits_authorised_departments', to='permits.PermitDepartment', verbose_name='Département autorisé à visualiser le document'),
        ),
        migrations.CreateModel(
            name='PermitRequestInquiry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('documents', models.ManyToManyField(blank=True, to='permits.PermitRequestComplementaryDocument', verbose_name='Documents complémentaire')),
                ('permit_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='permits.permitrequest', verbose_name='Demande de permis')),
                ('submitter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name="Demandeur de l'enquête")),
            ],
        ),
        migrations.AlterField(
            model_name='historicalpermitrequest',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Brouillon'), (1, 'Envoyée, en attente de traitement'), (4, 'Demande de compléments'), (3, 'En traitement'), (5, 'En validation'), (2, 'Approuvée'), (6, 'Refusée'), (7, 'Réceptionnée'), (8, "Mise à l'enquête en cours")], default=0, verbose_name='état'),
        ),
        migrations.AlterField(
            model_name='permitrequest',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Brouillon'), (1, 'Envoyée, en attente de traitement'), (4, 'Demande de compléments'), (3, 'En traitement'), (5, 'En validation'), (2, 'Approuvée'), (6, 'Refusée'), (7, 'Réceptionnée'), (8, "Mise à l'enquête en cours")], default=0, verbose_name='état'),
        ),
        migrations.AlterField(
            model_name='permitworkflowstatus',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Brouillon'), (1, 'Envoyée, en attente de traitement'), (4, 'Demande de compléments'), (3, 'En traitement'), (5, 'En validation'), (2, 'Approuvée'), (6, 'Refusée'), (7, 'Réceptionnée'), (8, "Mise à l'enquête en cours")], verbose_name='statut'),
        ),
        migrations.AlterField(
            model_name='permitrequestcomplementarydocument',
            name='document',
            field=permits.fields.ComplementaryDocumentFileField(storage=permits.fields.PrivateFileSystemStorage(), upload_to='', verbose_name='Document'),
        ),
        migrations.AlterField(
            model_name='historicalpermitrequest',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Brouillon'), (1, 'Envoyée, en attente de traitement'), (4, 'Demande de compléments'), (3, 'En traitement'), (5, 'En validation'), (2, 'Approuvée'), (6, 'Refusée'), (7, 'Réceptionnée'), (8, "Mise à l'enquête en cours"), (9, 'Archivée')], default=0, verbose_name='état'),
        ),
        migrations.AlterField(
            model_name='permitrequest',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Brouillon'), (1, 'Envoyée, en attente de traitement'), (4, 'Demande de compléments'), (3, 'En traitement'), (5, 'En validation'), (2, 'Approuvée'), (6, 'Refusée'), (7, 'Réceptionnée'), (8, "Mise à l'enquête en cours"), (9, 'Archivée')], default=0, verbose_name='état'),
        ),
        migrations.AlterField(
            model_name='permitworkflowstatus',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Brouillon'), (1, 'Envoyée, en attente de traitement'), (4, 'Demande de compléments'), (3, 'En traitement'), (5, 'En validation'), (2, 'Approuvée'), (6, 'Refusée'), (7, 'Réceptionnée'), (8, "Mise à l'enquête en cours"), (9, 'Archivée')], verbose_name='statut'),
        ),
        migrations.CreateModel(
            name='ArchivedPermitRequest',
            fields=[
                ('archived_date', models.DateTimeField(auto_now_add=True)),
                ('permit_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='permits.permitrequest')),
                ('archivist', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Personne ayant archivé la demande')),
            ],
        ),
    ]
