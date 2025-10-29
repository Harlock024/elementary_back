from django.urls import path


from .views import SchoolGradeViewSet, GroupViewSet, SubjectViewSet, EnrollmentViewSet,ClassRoomViewSet


urlpatterns = [
        # SchoolGrade endpoints
            path('school-grades/', SchoolGradeViewSet.as_view(), name='school-grade-list'),
            path('school-grades/<uuid:pk>/', SchoolGradeViewSet.as_view(),name='school-grade-detail'),
            
        # Group endpoints
            path('groups/', GroupViewSet.as_view(), name='group-list'),
            path('groups/<uuid:pk>/', GroupViewSet.as_view(), name='group-detail'),
        
        # Subject endpoints
            path('subjects/', SubjectViewSet.as_view(), name='subject-list'),
            path('subjects/<uuid:pk>/', SubjectViewSet.as_view(), name='subject-detail'),

        # Enrollment endpoints
            path('enrollments/', EnrollmentViewSet.as_view(), name='enrollment-list'),
            path('enrollments/<uuid:pk>/', EnrollmentViewSet.as_view(), name='enrollment-detail'),

        # ClassRoom endpoints
            path('classrooms/', ClassRoomViewSet.as_view(), name='classroom-list'),
            path('classrooms/<uuid:pk>/', ClassRoomViewSet.as_view(), name='classroom-detail')
    ]

