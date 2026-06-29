from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import BillingPlan, Subscription, Invoice


def pricing_view(request):
    plans = BillingPlan.objects.filter(is_active=True).order_by("sort_order")
    user_sub = None
    if request.user.is_authenticated:
        user_sub = Subscription.objects.filter(user=request.user, status="active").first()
    return render(request, "billing/pricing.html", {
        "plans": plans,
        "user_subscription": user_sub,
    })


@login_required
def subscribe_view(request, plan_id: int):
    try:
        plan = BillingPlan.objects.get(id=plan_id, is_active=True)
    except BillingPlan.DoesNotExist:
        messages.error(request, "Invalid plan.")
        return redirect("pricing")

    if plan.tier == "free":
        messages.info(request, "You're already on the Free plan.")
        return redirect("pricing")

    existing = Subscription.objects.filter(user=request.user, status="active").first()
    if existing:
        messages.info(request, f"You already have an active {existing.plan.name} subscription.")
        return redirect("pricing")

    return render(request, "billing/checkout.html", {
        "plan": plan,
    })


@login_required
def subscription_status_view(request):
    subs = Subscription.objects.filter(user=request.user).select_related("plan")
    invoices = Invoice.objects.filter(user=request.user).order_by("-created_at")[:10]
    return render(request, "billing/status.html", {
        "subscriptions": subs,
        "invoices": invoices,
    })


@login_required
def cancel_subscription_view(request, sub_id: int):
    try:
        sub = Subscription.objects.get(id=sub_id, user=request.user)
    except Subscription.DoesNotExist:
        messages.error(request, "Subscription not found.")
        return redirect("subscription_status")

    if sub.status == "active":
        sub.status = "canceled"
        sub.canceled_at = timezone.now()
        sub.auto_renew = False
        sub.save(update_fields=["status", "canceled_at", "auto_renew"])

        profile = getattr(request.user, "profile", None)
        if profile:
            profile.account_type = "standard"
            profile.save(update_fields=["account_type"])

        messages.success(request, "Subscription canceled.")

    return redirect("subscription_status")


@login_required
@require_POST
def create_checkout_session_view(request, plan_id: int):
    try:
        plan = BillingPlan.objects.get(id=plan_id, is_active=True)
    except BillingPlan.DoesNotExist:
        return JsonResponse({"error": "Invalid plan"}, status=400)

    if plan.tier == "free":
        return JsonResponse({"error": "Free plan cannot be purchased"}, status=400)

    return JsonResponse({"error": "Payment gateway not configured. Add Stripe or Paystack keys."}, status=501)


@csrf_exempt
def stripe_webhook_view(request):
    return JsonResponse({"status": "received"})


@csrf_exempt
def paystack_webhook_view(request):
    return JsonResponse({"status": "received"})
