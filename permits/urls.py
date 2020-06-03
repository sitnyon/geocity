from django.urls import include, path

from . import views

app_name = 'permits'

permit_request_urlpatterns = [
    path('administrative-entity/', views.permit_request_select_administrative_entity, name='permit_request_select_administrative_entity'),
]

existing_permit_request_urlpatterns = [
    path('', views.PermitRequestDetailView.as_view(), name='permit_request_detail'),
    path('types/', views.permit_request_select_types, name='permit_request_select_types'),
    path('objects/', views.permit_request_select_objects, name='permit_request_select_objects'),
    path('properties/', views.permit_request_properties, name='permit_request_properties'),
    path('appendices/', views.permit_request_appendices, name='permit_request_appendices'),
    path('actors/', views.permit_request_actors, name='permit_request_actors'),
    path('submit/', views.permit_request_submit, name='permit_request_submit'),
    path('geotime/', views.permit_request_geo_time, name='permit_request_geo_time'),
    path('delete/', views.permit_request_delete, name='permit_request_delete'),
    path('approve/', views.permit_request_approve, name='permit_request_approve'),
    path('reject/', views.permit_request_reject, name='permit_request_reject'),
]

urlpatterns = [
    path('<int:permit_request_id>/', include(permit_request_urlpatterns + existing_permit_request_urlpatterns)),
    path('permits-files/<path:path>', views.permit_request_file_download, name='permit_request_file_download'),
    path('', views.PermitRequestListExternsView.as_view(), name='permit_requests_list'),
    path('', include(permit_request_urlpatterns)),
    path('media/<int:property_value_id>/', views.permit_request_media_download, name='permit_request_media_download'),
]
