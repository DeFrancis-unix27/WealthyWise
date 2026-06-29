from django.urls import path
from . import views

urlpatterns = [
    path("pricing/", views.pricing_view, name="pricing"),
    path("subscribe/<int:plan_id>/", views.subscribe_view, name="subscribe"),
    path("status/", views.subscription_status_view, name="subscription_status"),
    path("cancel/<int:sub_id>/", views.cancel_subscription_view, name="cancel_subscription"),
    path("checkout/<int:plan_id>/", views.create_checkout_session_view, name="create_checkout"),
    path("webhook/stripe/", views.stripe_webhook_view, name="stripe_webhook"),
    path("webhook/paystack/", views.paystack_webhook_view, name="paystack_webhook"),
]
