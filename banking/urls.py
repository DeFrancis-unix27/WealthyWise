from django.urls import path
from . import views

urlpatterns = [
    path("", views.bank_list_view, name="bank_list"),
    path("link/<str:provider>/", views.link_bank_view, name="link_bank"),
    path("callback/", views.bank_callback_view, name="bank_callback"),
    path("unlink/<int:bank_id>/", views.unlink_bank_view, name="unlink_bank"),
    path("sync/<int:bank_id>/", views.sync_bank_view, name="sync_bank"),
    path("webhook/<str:provider>/", views.webhook_view, name="bank_webhook"),
]
