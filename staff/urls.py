from django.urls import path
from . import views
from .views import  StaffLoginView,edit_professor,StaffView


urlpatterns = [
 
        path("", StaffView.as_view(), name="staff_list_create"),
        path("<uuid:pk>/", views.StaffView.as_view(), name="staff_detail"),

        path("login/", StaffLoginView.as_view(), name="login"),
        path("profile/", views.StaffProfileView.as_view(), name="staff_profile"),
        # Admin paths (solo directora y admin) contraseña no hasheada visible
        path("professors/", views.list_professors, name="list_professors"),
        path("professors/create/", views.create_professor, name="create_professor"),
        path("professors/<uuid:pk>/delete/", views.delete_professor, name="delete_professor"),
        path("professors/<uuid:pk>/",edit_professor , name="edit_professor"),
        path("admin/",views.create_admin, name="create_admin"),
        ]



