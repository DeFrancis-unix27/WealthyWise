from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FinancialGoal, GoalMilestone, GoalProgress, LiteracyAssessment, LiteracyLevel

@login_required
def goal_list(request):
    goals = FinancialGoal.objects.filter(user=request.user).order_by("sort_order")
    return render(request, "goals/goal_list.html", {"goals": goals})

@login_required
def goal_detail(request, goal_id):
    goal = get_object_or_404(FinancialGoal, id=goal_id, user=request.user)
    return render(request, "goals/goal_detail.html", {"goal": goal})

@login_required
def goal_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        category = request.POST.get("category")
        target_amount = request.POST.get("target_amount")
        currency = request.POST.get("currency", "NGN")
        if title and category and target_amount:
            FinancialGoal.objects.create(
                user=request.user,
                title=title,
                category=category,
                target_amount=target_amount,
                currency=currency,
            )
            messages.success(request, "Goal created!")
            return redirect("goal_list")
        else:
            messages.error(request, "Please fill in all required fields.")
    return render(request, "goals/goal_form.html")

@login_required
def literacy_view(request):
    assessments = LiteracyAssessment.objects.filter(user=request.user).order_by("-taken_at")
    level, _ = LiteracyLevel.objects.get_or_create(user=request.user)
    return render(request, "goals/literacy.html", {"assessments": assessments, "level": level})
