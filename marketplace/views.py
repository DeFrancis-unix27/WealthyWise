from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, ProductCategory, CuratedCollection, Order, AffiliatePartner

def product_list(request):
    products = Product.objects.filter(is_active=True)
    category_slug = request.GET.get("category")
    if category_slug:
        products = products.filter(category__slug=category_slug)
    categories = ProductCategory.objects.filter(is_active=True)
    collections = CuratedCollection.objects.filter(is_active=True)
    return render(request, "marketplace/product_list.html", {
        "products": products, "categories": categories, "collections": collections,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "marketplace/product_detail.html", {"product": product})

def affiliate_partners(request):
    partners = AffiliatePartner.objects.filter(status="active")
    return render(request, "marketplace/affiliates.html", {"partners": partners})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "marketplace/order_list.html", {"orders": orders})
