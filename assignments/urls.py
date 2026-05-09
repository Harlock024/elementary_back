from django.urls import path 
from .views import AssignmentView

urlpatterns = [
        path('', AssignmentView.as_view(), name='assignment-list-all'),
        path('student/<uuid:student_id>/date/<str:date>/', AssignmentView.as_view(), name='assignment-list-by-student-date'),
        path('classroom/<uuid:class_id>/', AssignmentView.as_view(), name='assignment-list-by-class'),
        path('<uuid:id>/', AssignmentView.as_view(), name='assignment-patch'),
]
