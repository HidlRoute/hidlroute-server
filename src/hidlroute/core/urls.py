from django.urls import path

from hidlroute.core import views

app_name = "hidl_core"
urlpatterns = [
    path("devices/", views.device_list, name="devices_list"),
    path("add_device/", views.device_add, name="device_add"),
    path("edit_device/<int:device_id>/", views.device_edit, name="device_edit"),
]
