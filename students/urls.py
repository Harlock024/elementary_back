
from django.urls import path
from .views import StudentViewSet



urlpatterns = [
    path('', StudentViewSet.as_view(), name='student-list'),
    path('',StudentViewSet.as_view(), name='  student-create'),
    path('<int:pk>/', StudentViewSet.as_view(), name='student-detail'),
    ]
