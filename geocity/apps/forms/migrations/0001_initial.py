# Generated by Django 3.2.15 on 2022-10-13 13:24

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import geocity.apps.forms.fields
import geocity.fields
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("taggit", "0004_alter_taggeditem_content_type_alter_taggeditem_tag"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Field",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="nom")),
                (
                    "placeholder",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="exemple de donnée à saisir",
                    ),
                ),
                (
                    "help_text",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="information complémentaire",
                    ),
                ),
                (
                    "input_type",
                    models.CharField(
                        choices=[
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
                            ("title", "Titre"),
                        ],
                        max_length=30,
                        verbose_name="type de caractéristique",
                    ),
                ),
                (
                    "line_number_for_textarea",
                    models.PositiveIntegerField(
                        blank=True,
                        default=1,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(50),
                        ],
                        verbose_name="Nombre de lignes de la zone de texte",
                    ),
                ),
                (
                    "is_mandatory",
                    models.BooleanField(default=False, verbose_name="obligatoire"),
                ),
                (
                    "choices",
                    models.TextField(
                        blank=True,
                        help_text="Entrez un choix par ligne",
                        verbose_name="valeurs à choix",
                    ),
                ),
                (
                    "regex_pattern",
                    models.CharField(
                        blank=True,
                        help_text="Exemple: ^[0-9]{4}$",
                        max_length=255,
                        verbose_name="regex pattern",
                    ),
                ),
                (
                    "services_to_notify",
                    models.TextField(
                        blank=True,
                        help_text='Veuillez séparer les emails par une virgule ","',
                        verbose_name="Emails des services à notifier",
                    ),
                ),
                (
                    "file_download",
                    geocity.apps.forms.fields.FormFileField(
                        blank=True,
                        storage=geocity.fields.PrivateFileSystemStorage(),
                        upload_to="wot_files",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["pdf"]
                            )
                        ],
                        verbose_name="Fichier",
                    ),
                ),
                (
                    "additional_searchtext_for_address_field",
                    models.CharField(
                        blank=True,
                        help_text='Ex: "Yverdon-les-Bains" afin de limiter les recherches à Yverdon, <a href="https://api3.geo.admin.ch/services/sdiservices.html#search" target="_blank">Plus d\'informations</a>',
                        max_length=255,
                        verbose_name="Filtre additionnel pour la recherche d'adresse",
                    ),
                ),
                (
                    "store_geometry_for_address_field",
                    models.BooleanField(
                        default=False,
                        help_text="L'API Geoadmin est utilisée afin de trouver un point correspondant à l'adresse. En cas d'échec, le centroïde de l'entité administrative est utilisée <a href=\"https://api3.geo.admin.ch/services/sdiservices.html#search\" target=\"_blank\">Plus d'informations</a>",
                        verbose_name="Stocker la géométrie de l'adresse dans la table géométrique",
                    ),
                ),
                (
                    "is_public_when_permitrequest_is_public",
                    models.BooleanField(
                        default=False,
                        help_text="Ce champs sera visible sur l'application géocalendrier si la demande est publique",
                        verbose_name="Afficher ce champs au grand public si la demande est publique",
                    ),
                ),
            ],
            options={
                "verbose_name": "1.5 Configuration du champ",
                "verbose_name_plural": "1.5 Configuration des champs",
            },
        ),
        migrations.CreateModel(
            name="Form",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "can_always_update",
                    models.BooleanField(
                        default=False,
                        verbose_name="Demande modifiable en tout temps par le secrétariat",
                    ),
                ),
                (
                    "can_have_multiple_ranges",
                    models.BooleanField(
                        default=False, verbose_name="Peut avoir plusieurs plages"
                    ),
                ),
                (
                    "has_geometry_point",
                    models.BooleanField(default=True, verbose_name="Point"),
                ),
                (
                    "has_geometry_line",
                    models.BooleanField(default=True, verbose_name="Ligne"),
                ),
                (
                    "has_geometry_polygon",
                    models.BooleanField(default=True, verbose_name="Surface"),
                ),
                (
                    "directive",
                    geocity.apps.forms.fields.AdministrativeEntityFileField(
                        blank=True,
                        storage=geocity.fields.PrivateFileSystemStorage(),
                        upload_to="",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["pdf"]
                            )
                        ],
                        verbose_name="directive",
                    ),
                ),
                (
                    "directive_description",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        verbose_name="description de la directive",
                    ),
                ),
                (
                    "additional_information",
                    models.TextField(blank=True, verbose_name="autre information"),
                ),
                (
                    "needs_date",
                    models.BooleanField(
                        default=True, verbose_name="avec période de temps"
                    ),
                ),
                (
                    "start_delay",
                    models.IntegerField(
                        blank=True,
                        help_text="Délai minimum en jours avant la date de début (nombre entier positif ou négatif).",
                        null=True,
                        verbose_name="délai de commencement",
                    ),
                ),
                (
                    "requires_payment",
                    models.BooleanField(
                        default=True, verbose_name="Demande soumise à des frais"
                    ),
                ),
                (
                    "requires_validation_document",
                    models.BooleanField(
                        default=True, verbose_name="Document de validation obligatoire"
                    ),
                ),
                (
                    "is_public",
                    models.BooleanField(default=False, verbose_name="Visibilité "),
                ),
                (
                    "is_anonymous",
                    models.BooleanField(
                        default=False, verbose_name="Demandes anonymes uniquement"
                    ),
                ),
                (
                    "notify_services",
                    models.BooleanField(
                        default=False, verbose_name="Notifier les services"
                    ),
                ),
                (
                    "services_to_notify",
                    models.TextField(
                        blank=True,
                        help_text='Veuillez séparer les emails par une virgule ","',
                        verbose_name="Emails des services à notifier",
                    ),
                ),
                (
                    "permit_duration",
                    models.IntegerField(
                        blank=True,
                        help_text="Le permis pour l'objet sera prolongeable uniquement si cette valeur est fournie.",
                        null=True,
                        verbose_name="Durée de validité de la demande (jours)",
                    ),
                ),
                (
                    "expiration_reminder",
                    models.BooleanField(
                        default=False, verbose_name="Activer la fonction de rappel"
                    ),
                ),
                (
                    "days_before_reminder",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Délai de rappel (jours)"
                    ),
                ),
                (
                    "document_enabled",
                    models.BooleanField(
                        default=False, verbose_name="Activer la gestion des documents"
                    ),
                ),
                (
                    "publication_enabled",
                    models.BooleanField(
                        default=False,
                        verbose_name="Activer la gestion de la publication",
                    ),
                ),
                (
                    "permanent_publication_enabled",
                    models.BooleanField(
                        default=False,
                        verbose_name="Autoriser la mise en consultation sur une durée indéfinie",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="nom")),
                (
                    "order",
                    models.PositiveIntegerField(
                        db_index=True, default=0, verbose_name="ordre"
                    ),
                ),
                (
                    "wms_layers",
                    models.URLField(
                        blank=True, max_length=1024, verbose_name="Couche(s) WMS"
                    ),
                ),
                (
                    "wms_layers_order",
                    models.PositiveIntegerField(
                        default=1, verbose_name="Ordre de(s) couche(s)"
                    ),
                ),
                (
                    "administrative_entities",
                    models.ManyToManyField(
                        related_name="forms",
                        to="accounts.AdministrativeEntity",
                        verbose_name="entités administratives",
                    ),
                ),
            ],
            options={
                "verbose_name": "1.4 Configuration du formulaire",
                "verbose_name_plural": "1.4 Configuration des formulaires",
            },
        ),
        migrations.CreateModel(
            name="FormField",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("order", models.PositiveSmallIntegerField(db_index=True, default=0)),
                (
                    "field",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="forms.field",
                    ),
                ),
                (
                    "form",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="forms.form",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FormCategory",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="nom")),
                (
                    "meta_type",
                    models.IntegerField(
                        choices=[
                            (0, "Autres"),
                            (1, "Chantier"),
                            (2, "Construction"),
                            (3, "Événement sportif"),
                            (4, "Événement culturel"),
                            (5, "Événement commercial"),
                            (6, "Dispositif de police"),
                        ],
                        default=0,
                        verbose_name="Type générique",
                    ),
                ),
                (
                    "integrator",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="auth.group",
                        verbose_name="Groupe des administrateurs",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text="Mots clefs sans espaces, séparés par des virgules permettant de filtrer les types par l'url: https://geocity.ch/?typefilter=stationnement",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Mots-clés",
                    ),
                ),
            ],
            options={
                "verbose_name": "1.2 Configuration du type",
                "verbose_name_plural": "1.2 Configuration des types",
            },
        ),
        migrations.AddField(
            model_name="form",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="forms",
                to="forms.formcategory",
                verbose_name="categorie",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="integrator",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="auth.group",
                verbose_name="Groupe des administrateurs",
            ),
        ),
        migrations.AddField(
            model_name="field",
            name="forms",
            field=models.ManyToManyField(
                related_name="fields",
                through="forms.FormField",
                to="forms.Form",
                verbose_name="objets",
            ),
        ),
        migrations.AddField(
            model_name="field",
            name="integrator",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="auth.group",
                verbose_name="Groupe des administrateurs",
            ),
        ),
        migrations.AddIndex(
            model_name="field",
            index=models.Index(
                fields=["input_type"], name="forms_field_input_t_3001c2_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="field",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("input_type__in", ["list_single", "list_multiple"]),
                    ("choices", ""),
                    _negated=True,
                ),
                name="field_choices_not_empty_for_lists",
            ),
        ),
        migrations.AddConstraint(
            model_name="field",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("input_type", "regex"), ("regex_pattern", ""), _negated=True
                ),
                name="field_pattern_not_empty_for_regex",
            ),
        ),
    ]
