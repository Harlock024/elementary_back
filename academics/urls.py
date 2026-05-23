from django.urls import path

from .views import (
    ClassRoomViewSet,
    EnrollmentViewSet,
    GroupViewSet,
    PromotionView,
    SchoolGradeViewSet,
    SubjectViewSet,
)

urlpatterns = [
    # SchoolGrade endpoints
    path("school-grades/", SchoolGradeViewSet.as_view(), name="school-grade-list"),
    path( "school-grades/<uuid:pk>/",SchoolGradeViewSet.as_view(),name="school-grade-detail"),
    # Group endpoints
    path("groups/", GroupViewSet.as_view(), name="group-list"),
    path("groups/<uuid:pk>/", GroupViewSet.as_view(), name="group-detail,group-delete"),
    # Subject endpoints
    path("subjects/", SubjectViewSet.as_view(), name="subject-list"),
    path("subjects/<uuid:pk>/", SubjectViewSet.as_view(), name="subject-detail,subject-delete"),
    path("subjects/classroom/<uuid:class_id>/",SubjectViewSet.as_view(),name="subjects-by-classroom"),
    # Enrollment endpoints
    path("enrollments/", EnrollmentViewSet.as_view(), name="enrollment-list"),
    path("enrollments/<uuid:pk>/", EnrollmentViewSet.as_view(), name="enrollment-detail,enrollment-delete"),
    path("enrollments/student/<uuid:student_id>/", EnrollmentViewSet.as_view(), name="enrollments-by-student"),
    # ClassRoom endpoints
    path("classrooms/", ClassRoomViewSet.as_view(), name="classroom-list"),
    path("classrooms/<uuid:pk>/", ClassRoomViewSet.as_view(), name="classroom-detail,classroom-delete"),
    # Promotion endpoint
    path("promotions/execute/", PromotionView.as_view(), name="promotion-execute"),
]