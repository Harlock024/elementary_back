from django.urls import path 
from .views import AttendaceView,AttendanceCatalogView



urlpatterns = [
        path('', AttendaceView.as_view(), name='attendance-list-all'),
        path('classroom/<uuid:class_id>/', AttendaceView.as_view(), name='attendance-list'),

        path('catalog/', AttendanceCatalogView.as_view(), name='attendance-catalog-list'),
        path('catalog/<uuid:class_id>/', AttendanceCatalogView.as_view(), name='attendance-catalog-list-by-class')

        ]
