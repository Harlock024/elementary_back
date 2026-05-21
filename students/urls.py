from django.urls import path
from .views import StudentProfileView, StudentViewSet

urlpatterns = [
    path('', StudentViewSet.as_view(), name='student-list'),
    path('group/<uuid:group_id>/', StudentViewSet.as_view(), name='students-by-group'),
    path('<uuid:pk>/', StudentViewSet.as_view(), name='student-detail'),
    path('<uuid:pk>/profile/', StudentProfileView.as_view(), name='student-profile'),
]
