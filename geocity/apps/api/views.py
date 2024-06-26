import mimetypes
import os
from datetime import datetime, timedelta, timezone

import requests
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.db.models import F, Prefetch, Q
from django.http import FileResponse, JsonResponse
from django.utils.text import get_valid_filename
from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from geocity import geometry
from geocity.apps.accounts.models import AdministrativeEntity
from geocity.apps.api.pagination import AgendaResultsSetPagination
from geocity.apps.api.services import (
    can_image_be_displayed_for_agenda,
    get_image_path,
    get_mime_type,
)
from geocity.apps.django_wfs3.mixins import WFS3DescribeModelViewSetMixin
from geocity.apps.forms.models import Form
from geocity.apps.submissions import search
from geocity.apps.submissions.models import (
    FieldValue,
    Submission,
    SubmissionGeoTime,
    SubmissionInquiry,
)

from . import permissions, serializers

# ///////////////////////////////////
# DJANGO REST API
# ///////////////////////////////////


class SubmissionGeoTimeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Events request endpoint usage:
        1.- /rest/events/?show_only_future=true (past events get filtered out)
        2.- /rest/events/?starts_at=2022-01-01
        3.- /rest/events/?ends_at=2020-01-01
        4.- /rest/events/?adminentities=1,2,3

    """

    serializer_class = serializers.SubmissionGeoTimeSerializer
    throttle_scope = "events"
    permission_classes = [permissions.AllowAllRequesters]

    def get_queryset(self):
        """
        This view should return a list of events for which the logged user has
        view permissions or events set as public by pilot
        """

        show_only_future = self.request.query_params.get("show_only_future", None)
        starts_at = self.request.query_params.get("starts_at", None)
        ends_at = self.request.query_params.get("ends_at", None)
        administrative_entities = self.request.query_params.get("adminentities", None)

        base_filter = Q()
        if starts_at:
            start = datetime.strptime(starts_at, "%Y-%m-%d")
            base_filter &= Q(starts_at__gte=start)
        if ends_at:
            end = datetime.strptime(ends_at, "%Y-%m-%d")
            base_filter &= Q(ends_at__lte=end)
        if show_only_future == "true":
            base_filter &= Q(ends_at__gte=datetime.now())
        if administrative_entities:
            base_filter &= Q(
                submission__administrative_entity__in=administrative_entities.split(",")
            )
        base_filter &= ~Q(submission__status=Submission.STATUS_DRAFT)
        # Only allow forms that have at least one geometry type mandatory
        forms_prefetch = Prefetch(
            "submission__forms",
            queryset=Form.objects.filter(
                (
                    Q(has_geometry_point=True)
                    | Q(has_geometry_line=True)
                    | Q(has_geometry_polygon=True)
                )
                & Q(needs_date=True)
            ).select_related("category"),
        )

        today = datetime.today()
        current_inquiry_prefetch = Prefetch(
            "submission__inquiries",
            queryset=SubmissionInquiry.objects.filter(
                start_date__lte=today, end_date__gte=today
            ),
            to_attr="current_inquiries_filtered",
        )

        qs = (
            SubmissionGeoTime.objects.filter(base_filter)
            .filter(
                Q(
                    submission__in=Submission.objects.filter_for_user(
                        self.request.user,
                    )
                )
                | Q(submission__is_public=True)
                | Q(submission__status=Submission.STATUS_INQUIRY_IN_PROGRESS)
            )
            .prefetch_related(forms_prefetch)
            .prefetch_related(current_inquiry_prefetch)
            .select_related("submission__administrative_entity")
            .select_related("submission__price")
        )

        return qs.order_by("starts_at")


# //////////////////////////////////
# CURRENT USER ENDPOINT
# //////////////////////////////////


class CurrentUserAPIView(RetrieveAPIView):
    """
    Current user endpoint usage:
        /rest/current_user/     shows current user
    """

    serializer_class = serializers.CurrentUserSerializer
    permission_classes = [permissions.AllowAllRequesters]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=False)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)

    # Returns the logged user, if there's any
    def get_object(self):
        try:
            return User.objects.get(Q(username=self.request.user))
        except User.DoesNotExist:
            return AnonymousUser()


class SubmissionViewSet(WFS3DescribeModelViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Submission endpoint usage:
        1.- /rest/submissions/?submission_id=1
        2.- /rest/submissions/?form=1
        3.- /rest/submissions/?status=0

        Notes:
            1.- For forms that do not have geometry, the returned
                geometry is a 2x2 meters square around the centroid of the administrative entity geometry
            2.- This endpoint does not filter out items without geometry.
                For forms types that have only point geometry, the returned geometry
                is a polygon of 2x2 meters

            This endpoint is mainly designed for atlas print generation with QGIS Server
            For standard geometric endpoints, please use the following endpoints
            1.- Points: /rest/submissions_point/
            2.- Lines: /rest/submissions_line/
            3.- Polygons: /rest/submissions_poly/
    """

    throttle_scope = "submissions"
    serializer_class = serializers.SubmissionPrintSerializer
    permission_classes = [permissions.BlockRequesterUserWithoutGroup]

    wfs3_title = "Demandes"
    wfs3_description = "Toutes les demandes"
    wfs3_geom_lookup = "geo_time__geom"  # lookup for the geometry (on the queryset), used to determine bbox
    wfs3_srid = 2056

    def get_throttles(self):
        # Do not throttle API if request is used py print internal service
        throttle_classes = [ScopedRateThrottle]
        return [throttle() for throttle in throttle_classes]

    def get_queryset(self, geom_type=None):
        """
        This view should return a list of submissions for which the logged user has
        view permissions
        """
        user = self.request.user
        filters_serializer = serializers.SubmissionFiltersSerializer(
            data={
                # FIXME inform API consumers of query params changes
                # works_object_type -> form
                # permit_request_id -> submission_id
                "form": self.request.query_params.get("form"),
                "status": self.request.query_params.get("status"),
                "submission_id": self.request.query_params.get("submission_id"),
            }
        )
        filters_serializer.is_valid(raise_exception=True)
        filters = filters_serializer.validated_data

        base_filter = Q()

        if filters["form"]:
            base_filter &= Q(forms=filters["form"])

        if filters["status"]:
            base_filter &= Q(status=filters["status"])

        if filters["submission_id"]:
            base_filter &= Q(pk=filters["submission_id"])

        geom_qs = SubmissionGeoTime.objects.all()
        # filter item which have the geom_type in their geometry column
        if geom_type:
            geom_qs = geom_qs.annotate(
                geom_type=geometry.GeomStAsText(
                    F("geom"),
                )
            )
            if geom_type == "lines":
                geom_qs = geom_qs.filter(geom_type__contains="LINE")
            if geom_type == "points":
                geom_qs = geom_qs.filter(geom_type__contains="POINT")
            if geom_type == "polygons":
                geom_qs = geom_qs.filter(geom_type__contains="POLY")
            base_filter &= Q(
                id__in=set(geom_qs.values_list("submission_id", flat=True))
            )

        geotime_prefetch = Prefetch("geo_time", queryset=geom_qs)
        forms_prefetch = Prefetch(
            "forms",
            queryset=Form.objects.select_related("category"),
        )

        today = datetime.today()
        current_inquiry_prefetch = Prefetch(
            "inquiries",
            queryset=SubmissionInquiry.objects.filter(
                start_date__lte=today, end_date__gte=today
            ),
            to_attr="current_inquiries_filtered",
        )
        qs = (
            Submission.objects.filter(base_filter)
            .filter(
                Q(
                    id__in=Submission.objects.filter_for_user(
                        user,
                    )
                )
            )
            .prefetch_related(forms_prefetch)
            .prefetch_related(geotime_prefetch)
            .prefetch_related(current_inquiry_prefetch)
            .prefetch_related("selected_forms", "contacts")
            .prefetch_related("service_fee")
            .prefetch_related("service_fee__permit_department")
            .prefetch_related("service_fee__service_fee_type")
            .select_related(
                "administrative_entity",
                "author",
                "price",
            )
        )

        return qs


class SubmissionDetailsViewSet(
    WFS3DescribeModelViewSetMixin, viewsets.ReadOnlyModelViewSet
):
    """
    Submissions details endpoint usage:
        1.- /rest/submissions_details/?submission_id=1
    Liste types :
    - address
    - checkbox
    - date
    - file
    - list_multiple
    - list_single
    - number
    - regex
    - text
    - title
    """

    throttle_scope = "submissions_details"
    serializer_class = serializers.SubmissionDetailsSerializer
    permission_classes = [permissions.AllowAllRequesters]

    def get_queryset(self, geom_type=None):
        """
        This view should return a list of submissions for which the logged user has
        view permissions.

        # TODO: In another story, implement the difference between anonymous and user. Group public/private with inquiry status in the same section of form or add buttons to make public permanent
        # TODO: Update test_api_submissions_details_user
        +---------+---------------------------++---------+---------++---------+---------++---------+---------++---------------------------------------------------------------------------------+
        |         |                           || Public  | Private || Public  | Private || Public  | Private ||                                                                                 |
        + Status  + Status name               ++---------+---------++---------+---------++---------+---------++ Comment                                                                         +
        |         |                           || Anonym. | Anonym. || User    | User    || Trusted | Trusted ||                                                                                 |
        +=========+===========================++=========+=========++=========+=========++=========+=========++=================================================================================+
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        |    0    | DRAFT                     ||    X    |    X    ||    X    |    X    ||    X    |    X    ||                                                                                 |
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        +---------+---------------------------++---------+---------++---------+---------++---------+---------++---------------------------------------------------------------------------------+
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        |    1    | SUBMITTED_FOR_VALIDATION  ||    X    |    X    ||    X    |    X    ||    X    |    X    ||                                                                                 |
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        +---------+---------------------------++---------+---------++---------+---------++---------+---------++---------------------------------------------------------------------------------+
        |         |                           ||         |         ||         |         ||         |         || Private user shows his own requests                                             |
        |    2    | APPROVED                  ||    /    |    X    ||    /    |    /    ||    /    |    /    || Private trusted shows based on administrative entity of group                   |
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        +---------+---------------------------++---------+---------++---------+---------++---------+---------++---------------------------------------------------------------------------------+
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        |    3    | PROCESSING                ||    X    |    X    ||    X    |    X    ||    X    |    X    ||                                                                                 |
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        +---------+---------------------------++---------+---------++---------+---------++---------+---------++---------------------------------------------------------------------------------+
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        |    4    | AWAITING_SUPPLEMENT       ||    X    |    X    ||    X    |    X    ||    X    |    X    ||                                                                                 |
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        +---------+---------------------------++---------+---------++---------+---------++---------+---------++---------------------------------------------------------------------------------+
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        |    5    | AWAITING_VALIDATION       ||    X    |    X    ||    X    |    X    ||    X    |    X    ||                                                                                 |
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        +---------+---------------------------++---------+---------++---------+---------++---------+---------++---------------------------------------------------------------------------------+
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        |    6    | REJECTED                  ||    X    |    X    ||    X    |    X    ||    X    |    X    ||                                                                                 |
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        +---------+---------------------------++---------+---------++---------+---------++---------+---------++---------------------------------------------------------------------------------+
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        |    7    | RECEIVED                  ||    X    |    X    ||    X    |    X    ||    X    |    X    ||                                                                                 |
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        +---------+---------------------------++---------+---------++---------+---------++---------+---------++---------------------------------------------------------------------------------+
        |         |                           ||                   ||                   ||                   ||                                                                                 |
        |    8    | INQUIRY_IN_PROGRESS       ||    ///////////    ||    ///////////    ||    ///////////    ||                                                                                 |
        |         |                           ||                   ||                   ||                   ||                                                                                 |
        +---------+---------------------------++---------+---------++---------+---------++---------+---------++---------------------------------------------------------------------------------+
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        |    9    | ARCHIVED                  ||    X    |    X    ||    X    |    X    ||    X    |    X    ||                                                                                 |
        |         |                           ||         |         ||         |         ||         |         ||                                                                                 |
        +---------+---------------------------++---------+---------++---------+---------++---------+---------++---------------------------------------------------------------------------------+
        / = Should show
        X = Should not show
        Anonym. = Any non logged user. Anonym. = Anonymous
        User = Logged user, based on his submissions
        Trusted = Logged user, based on group in the same administrative entity as the submission
        """
        # Only take user with session authentication
        user = (
            self.request.user
            if self.request.user.is_authenticated
            and self.request.session._SessionBase__session_key
            else None
        )

        filters_serializer = serializers.SubmissionFiltersSerializer(
            data={
                "submission_id": self.request.query_params.get("submission_id"),
            }
        )
        filters_serializer.is_valid(raise_exception=True)
        filters = filters_serializer.validated_data

        base_filter = Q()

        if filters["submission_id"]:
            base_filter &= Q(pk=filters["submission_id"])

        if user:
            qs = Submission.objects.filter(base_filter).filter(
                Q(
                    id__in=Submission.objects.filter_for_user(
                        user,
                    )
                )
                & Q(status__in=Submission.VISIBLE_IN_CALENDAR_STATUSES)
                | Q(is_public=True)
                & Q(status__in=Submission.VISIBLE_IN_CALENDAR_STATUSES)
            )
        else:
            qs = Submission.objects.filter(base_filter).filter(
                Q(is_public=True)
                & Q(status__in=Submission.VISIBLE_IN_CALENDAR_STATUSES)
            )

        return qs


def submission_view_set_subset_factory(geom_type_name):
    """Returns a subclass of SubmissionViewSet with a specific multi-geometry instead
    of the bounding box"""

    if geom_type_name == "lines":
        geom_serializer = serializers.SubmissionGeoTimeGeoJSONSerializer.EXTRACT_LINES
    elif geom_type_name == "points":
        geom_serializer = serializers.SubmissionGeoTimeGeoJSONSerializer.EXTRACT_POINTS
    elif geom_type_name == "polygons":
        geom_serializer = serializers.SubmissionGeoTimeGeoJSONSerializer.EXTRACT_POLYS
    else:
        raise Exception(f"Unsupported geom type name {geom_type_name}")

    class Serializer(serializers.SubmissionPrintSerializer):
        geo_envelop = serializers.SubmissionGeoTimeGeoJSONSerializer(
            source="geo_time",
            read_only=True,
            extract_geom=geom_serializer,
        )

    # DRF want's the serializer to have a specific class name
    Serializer.__name__ = f"SubmissionViewSetSerializer{geom_type_name}"

    class ViewSet(SubmissionViewSet):
        """
        Submissions endpoint usage:
            1.- /rest/submissions/?submission_id=1
            2.- /rest/submissions/?form=1
            3.- /rest/submissions/?status=0
        """

        throttle_scope = "submissions"
        serializer_class = Serializer
        permission_classes = [permissions.BlockRequesterUserWithoutGroup]

        wfs3_title = f"{SubmissionViewSet.wfs3_title} ({geom_type_name})"
        wfs3_description = f"{SubmissionViewSet.wfs3_description} (géométries de type {geom_type_name})"

        def get_throttles(self):
            throttle_classes = [ScopedRateThrottle]
            return [throttle() for throttle in throttle_classes]

        def get_queryset(self):
            # Inject the geometry filter
            return super().get_queryset(geom_type=geom_type_name)

    return ViewSet


class SearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Search endpoint usage:
        1.- /rest/search/?search=my_search
        2.- /rest/search/?search=my_search&limit=10
        3.- Some examples, not all cases are represented :
            - Date : /rest/search/?search=25.08
            - Author : /rest/search/?search=Marcel Dupond
            - Email : /rest/search/?search=Marcel.Dupond@hotmail.com
            - Phone : /rest/search/?search=0241112233
        Replace "my_search" by the text/words you want to find
        By default only 5 elements are shown
        Replace the number after limit to changes the number of elements to show
    """

    throttle_scope = "search"
    serializer_class = serializers.SearchSerializer
    permission_classes = [permissions.BlockRequesterUserPermission]

    def get_queryset(self):
        terms = self.request.query_params.get("search")
        limit_params = self.request.query_params.get("limit")
        # If a digit is given in query params, take this value casted to int, if not take 5 as default limit
        limit = int(limit_params) if limit_params and limit_params.isdigit() else 5
        if terms:
            permit_requests = Submission.objects.filter_for_user(self.request.user)
            results = search.search_submissions(
                search_str=terms, submissions_qs=permit_requests, limit=limit
            )
            return results
        else:
            return None


SubmissionPointViewSet = submission_view_set_subset_factory("points")
SubmissionLineViewSet = submission_view_set_subset_factory("lines")
SubmissionPolyViewSet = submission_view_set_subset_factory("polygons")


class CustomFileResponse(FileResponse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add header Expires
        expiration_date = datetime.now() + timedelta(days=7)
        expiration_date_http_format = expiration_date.strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )
        self["Expires"] = expiration_date_http_format


def image_display(request, submission_id, image_name):
    safe_submission_id = get_valid_filename(submission_id)
    safe_image_name = get_valid_filename(image_name)

    image_path = get_image_path(safe_submission_id, safe_image_name)

    if os.path.exists(image_path) and can_image_be_displayed_for_agenda(
        safe_submission_id, safe_image_name, Submission, FieldValue
    ):
        image_file = open(image_path, "rb")
        mime_type, encoding = mimetypes.guess_type(image_path)
        response = CustomFileResponse(image_file, content_type=mime_type)
        return response
    else:
        return JsonResponse({"message": "unauthorized."}, status=404)


def image_thumbor_display(request, submission_id, image_name):
    safe_submission_id = get_valid_filename(submission_id)
    safe_image_name = get_valid_filename(image_name)

    if not can_image_be_displayed_for_agenda(
        safe_submission_id, safe_image_name, Submission, FieldValue
    ):
        return JsonResponse({"message": "unauthorized."}, status=404)

    width = request.GET.get("width", 397)
    height = request.GET.get("height", 562)
    format = request.GET.get("format", "webp")
    fit = request.GET.get("fit", None)

    INTERNAL_WEB_ROOT_URL = "http://web:9000"
    image_url = (
        f"{INTERNAL_WEB_ROOT_URL}/rest/image/{safe_submission_id}/{safe_image_name}"
    )

    # TODO: V2 -> understand (adaptive-)(full-)fit-in between unsafe and size

    thumbor_params = "unsafe/"

    if fit:
        thumbor_params += f"{fit}/"

    thumbor_params += f"{width}x{height}/smart/filters:format({format})"

    if settings.USE_THUMBOR:
        try:
            response = requests.get(
                f"{settings.THUMBOR_SERVICE_URL}/{thumbor_params}/{image_url}"
            )
        except requests.exceptions.RequestException as e:
            response = requests.get(image_url)
    else:
        response = requests.get(image_url)

    mime_type = get_mime_type(response.content)
    thumbor_response = CustomFileResponse(response, content_type=mime_type)

    return thumbor_response


def get_agenda_submissions(entities, submissions):
    # To validate a request and show it in agenda, an user need to be pilot of his own entity and validator for other entities.
    # Retrieve pilots of entity
    pilot_of_entity = User.objects.filter(
        groups__permit_department__administrative_entity__in=entities,
        groups__permit_department__is_backoffice=True,
    ).values("id")

    # Check agenda submissions is validated by any user on the pilot group of it's own entity
    submissions = submissions.filter(
        Q(administrative_entity__in=entities)
        | Q(validations__validated_by__in=pilot_of_entity)
    )

    return submissions


class AgendaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This api provides :
    - Minimal informations, to show all available submissions /rest/agenda/
    - Detailed informations of a specific submission, filtered by id, example : /rest/agenda/:id
    Submissions are filtered by date
    Images are provided through thumbor https://thumbor.readthedocs.io/en/latest/imaging.html
    Arguments that can be supplied in the url :
    - ?domain can be given through the component in html, can be a comma separated list, it corresponds to the entity tags (mots-clés)
    - ?starts_at
    - ?ends_at
    - ?width
    - ?height
    - ?format (jpg, jpeg, png, webp, etc...)
    - ?query to filter on values containing the query
    - ?fit to chose the way the image will fit the size. Can be used for all the following arguments https://thumbor.readthedocs.io/en/latest/usage.html
    - --- adaptive-in
    - --- full-in
    - --- fit-in
    """

    throttle_scope = "agenda"
    serializer_class = serializers.AgendaSerializer
    pagination_class = AgendaResultsSetPagination
    permission_classes = [permissions.AllowAllRequesters]

    def get_queryset(self):
        """
        This view has a detailed result and a simple result
        The detailed result is built with AgendaResultsSetPagination,
        this is required to be able to make pagination and return features and filters
        The simple result just return informations for une submission and lists available domains
        The order is important, agenda-embed has no logic, everything is set here
        """
        submissions = (
            Submission.objects.filter(
                Q(selected_forms__field_values__value__val__isnull=False)
                & Q(selected_forms__form__agenda_visible=True)
                & Q(is_public_agenda=True)
                & Q(status__in=Submission.VISIBLE_IN_AGENDA_STATUSES)
            )
            .distinct()
            .order_by("-featured_agenda", "geo_time__starts_at")
            .prefetch_related("selected_forms__field_values")
        )
        # List params given by the request as query_params
        query_params = self.request.query_params
        # Filter domain (administrative_entity) to permit sites to filter on their own domain (e.g.: sports, culture)
        domains = None

        # Dont filter with other conditions, when trying to access to event details
        # Still possible to put after a domain_filter later, if we return it in agenda-embed
        if "pk" in self.kwargs:
            return submissions

        if "domain_filter" in query_params:
            domain_filter = query_params.getlist("domain_filter")
            entities = AdministrativeEntity.objects.filter(id__in=domain_filter)
            submissions = get_agenda_submissions(entities, submissions)
        elif "domain" in query_params:
            domains = query_params["domain"]
            domains = domains.split(",") if domains else None
            entities = AdministrativeEntity.objects.filter(agenda_domain__in=domains)
            submissions = get_agenda_submissions(entities, submissions)

        if "starts_at" in query_params:
            starts_at = datetime.strptime(query_params["starts_at"], "%Y-%m-%d")
            starts_at = starts_at.replace(tzinfo=timezone.utc)
            submissions = submissions.filter(geo_time__ends_at__gte=starts_at)

        if "ends_at" in query_params:
            ends_at = datetime.strptime(query_params["ends_at"], "%Y-%m-%d")
            ends_at = ends_at.replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc
            )
            submissions = submissions.filter(geo_time__starts_at__lte=ends_at)

        if "starts_at" not in query_params and "ends_at" not in query_params:
            today = datetime.now(timezone.utc) + timedelta(
                hours=settings.LOCAL_TIME_ZONE_UTC
            )
            submissions = submissions.filter(geo_time__ends_at__gte=today)

        if "query" in query_params:
            query = query_params["query"]
            submissions = submissions.filter(
                Q(selected_forms__field_values__value__val__contains=query)
                | Q(selected_forms__field_values__value__val__icontains=query)
            )

        # List every available filter
        available_filters = serializers.get_available_filters_for_agenda_as_qs(domains)

        if not available_filters:
            return submissions

        # Secure the number of query_params to dont be higher than the number of available_filters + 5
        # + 5 for optional filters, like startsAt and endsAt, domain
        if len(query_params) > len(available_filters) + 5:
            return submissions

        # Do the required actions fo every query_param
        for field_name in query_params:
            # Check if the given query_param is used to filter (is it a category ?)
            field_name_is_api_filter = any(
                field_name in api_filter
                for api_filter in available_filters.values_list("api_name")
            )
            if field_name_is_api_filter:
                # Prepare queryset to filter by categories
                conditions = Q()

                # Get the Field object related to the query_param.
                # Filter + first, in case there's twice the same api_name in field for same entity
                field = available_filters.filter(Q(api_name=field_name)).first()

                # Get every value for each id given in query_param
                for value in query_params.getlist(field_name):
                    value = int(value)

                    # Get the choice corresponding to the id given in query_param
                    # The id = line of choice
                    category_choice = field.choices.strip().splitlines()[value]

                    # Filter submission according to the category choices
                    conditions |= Q(
                        selected_forms__field_values__value__val=category_choice
                    )
                    conditions |= Q(
                        selected_forms__field_values__value__val__contains=[
                            category_choice
                        ]
                    )

                # Filter with every category
                submissions = submissions.filter(conditions)

        return submissions
