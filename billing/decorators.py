from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def premium_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        profile = getattr(request.user, "profile", None)
        if profile and profile.account_type in ("premium", "business"):
            return view_func(request, *args, **kwargs)

        messages.warning(
            request,
            "This feature requires a Premium or Business subscription. "
            '<a href="/pricing/">Upgrade now</a> to unlock it.',
        )
        return redirect("landing")

    return _wrapped_view


def business_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        profile = getattr(request.user, "profile", None)
        if profile and profile.account_type == "business":
            return view_func(request, *args, **kwargs)

        messages.warning(
            request,
            "This feature requires a Business subscription. "
            '<a href="/pricing/">Upgrade now</a> to unlock it.',
        )
        return redirect("landing")

    return _wrapped_view
