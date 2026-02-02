from django.urls import path
from .views import (
    upload_csv,
    get_summary,
    get_history,
    get_equipment_data,
    generate_pdf
)
from .auth_views import login, register

urlpatterns = [
    path("auth/login/", login, name="login"),
    path("auth/register/", register, name="register"),
    path("upload/", upload_csv, name="upload_csv"),
    path("summary/<int:dataset_id>/", get_summary, name="get_summary"),
    path("history/", get_history, name="get_history"),
    path("data/<int:dataset_id>/", get_equipment_data, name="get_equipment_data"),
    path("pdf/<int:dataset_id>/", generate_pdf, name="generate_pdf"),
]
