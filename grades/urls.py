from django.urls import path
from .views import GradeViewSet, GradeCatalogViewSet

urlpatterns = [

        path('', GradeViewSet.as_view(), name='grade-list'),
        path('<int:pk>/', GradeViewSet.as_view(), name='grade-detail'),
        path('classroom/<uuid:class_room_id>/', GradeViewSet.as_view(), name='grade-by-classroom'),
        # Catalog endpoints
        path('catalog/', GradeCatalogViewSet.as_view(), name='grade-catalog-list'),
        path('catalog/<uuid:pk>/', GradeCatalogViewSet.as_view(), name='grade-catalog-detail-or-update/delete'),
]
