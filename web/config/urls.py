from django.contrib import admin
from django.urls import path

from parking.views import sample_data_view, student_list

urlpatterns = [
    path("", sample_data_view, name="sample_data"),
    path("students/", student_list, name="student_list"),
    path("admin/", admin.site.urls),
]
