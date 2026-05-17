
from django.urls import path
from .views import StudentViewSet



urlpatterns = [
    path('', StudentViewSet.as_view(), name='student-list'),
    path('group/<uuid:group_id>/', StudentViewSet.as_view(), name='students-by-group'),
    path('',StudentViewSet.as_view(), name='  student-create'),
    path('<uuid:pk>/', StudentViewSet.as_view(), name='student-detail'),
    ]