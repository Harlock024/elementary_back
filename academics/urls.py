from django.urls import path


from .views import SchoolGradeViewSet, GroupViewSet, SubjectViewSet, EnrollmentViewSet


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
            path('enrollments/<uuid:pk>/', EnrollmentViewSet.as_view(), name='enrollment-detail')

    ]
