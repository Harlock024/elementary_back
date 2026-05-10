from django.urls import path
from .views import GradeViewSet, GradingCriteriaViewSet

urlpatterns = [
    path('', GradeViewSet.as_view(), name='grade-list'),
    path('<int:pk>/', GradeViewSet.as_view(), name='grade-detail'),
    path('classroom/<uuid:class_room_id>/', GradeViewSet.as_view(), name='grade-by-classroom'),

    path('grading-criteria/', GradingCriteriaViewSet.as_view(), name='grading-criteria-list'),
    path('grading-criteria/<uuid:pk>/', GradingCriteriaViewSet.as_view(), name='grading-criteria-detail'),
    path('grading-criteria/classroom/<uuid:class_room_id>/', GradingCriteriaViewSet.as_view(), name='grading-criteria-by-classroom'),
]
