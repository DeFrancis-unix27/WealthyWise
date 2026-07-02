from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("affiliates/", views.affiliate_partners, name="affiliate_partners"),
    path("orders/", views.order_list, name="order_list"),
    path("<slug:slug>/", views.product_detail, name="product_detail"),
]
