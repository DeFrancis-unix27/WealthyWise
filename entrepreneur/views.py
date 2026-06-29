from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Business, BusinessPlan, SideHustle, RevenueStream, EntrepreneurshipPath

@login_required
def business_list(request):
    businesses = Business.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "entrepreneur/business_list.html", {"businesses": businesses})

@login_required
def business_detail(request, business_id):
    business = get_object_or_404(Business, id=business_id, user=request.user)
    return render(request, "entrepreneur/business_detail.html", {"business": business})

@login_required
def business_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        business_type = request.POST.get("business_type", "sole_proprietorship")
        currency = request.POST.get("currency", "NGN")
        if name:
            Business.objects.create(user=request.user, name=name, business_type=business_type, currency=currency)
            messages.success(request, "Business created!")
            return redirect("business_list")
        else:
            messages.error(request, "Business name is required.")
    return render(request, "entrepreneur/business_form.html")

@login_required
def side_hustle_list(request):
    hustles = SideHustle.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "entrepreneur/side_hustle_list.html", {"hustles": hustles})

@login_required
def side_hustle_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        platform_type = request.POST.get("platform_type", "other")
        if name:
            SideHustle.objects.create(user=request.user, name=name, platform_type=platform_type)
            messages.success(request, "Side hustle added!")
            return redirect("side_hustle_list")
        else:
            messages.error(request, "Name is required.")
    return render(request, "entrepreneur/side_hustle_form.html")

def path_list(request):
    paths = EntrepreneurshipPath.objects.filter(is_published=True)
    return render(request, "entrepreneur/path_list.html", {"paths": paths})
