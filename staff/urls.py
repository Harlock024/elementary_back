from django.urls import path
from . import views
from .views import (
    StaffChangePasswordView,
    StaffLoginView,
    StaffLogoutView,
    StaffView,
    edit_professor,
)


urlpatterns = [
 
        path("", StaffView.as_view(), name="staff_list_create"),
        path("<uuid:pk>/", views.StaffView.as_view(), name="staff_detail"),

        path("login/", StaffLoginView.as_view(), name="login"),
        path("logout/", StaffLogoutView.as_view(), name="logout"),
        path("profile/", views.StaffProfileView.as_view(), name="staff_profile"),
        path("profile/change-password/", StaffChangePasswordView.as_view(), name="staff_change_password"),
        path("professors/", views.list_professors, name="list_professors"),
        path("professors/create/", views.create_professor, name="create_professor"),
        path("professors/<uuid:pk>/delete/", views.delete_professor, name="delete_professor"),
        path("professors/<uuid:pk>/",edit_professor , name="edit_professor"),
        path("admin/",views.create_admin, name="create_admin"),
        ]
