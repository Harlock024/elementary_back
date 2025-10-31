from django.urls import path 
from .views import AttendaceView


urlpatterns = [
        path('', AttendaceView.as_view(), name='attendance-list-all'),
        path('classroom/<uuid:class_id>/', AttendaceView.as_view(), name='attendance-list'),
        ]
