from django.urls import path
from .views  import  ExportAttendace, ExportGrades


urlpatterns = [
        path('attendance/<uuid:class_id>/',ExportAttendace, name='export-attendance'),
        path('grades/<uuid:class_id>/',ExportGrades, name='export-grades'),
]
