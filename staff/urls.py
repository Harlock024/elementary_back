from django.urls import path
from . import views
from .views import StaffLoginView



urlpatterns = [
        path("", views.index, name="index"),
        path("login/", StaffLoginView.as_view(), name="login"),
        path("professors/", views.list_professors, name="list_professors"),
        path("professors/create/", views.create_professor, name="create_professor"),
        ]
