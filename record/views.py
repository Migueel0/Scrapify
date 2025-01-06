from django.shortcuts import render, get_object_or_404
from user.models import User
from product.models import Product
from record.models import Record
from .models import Record


def get_or_create_record(user) -> Record:
    if Record.objects.filter(user=user).exists():
        record = Record.objects.get(user=user)
    else:
        Record.objects.create(user=user)
        record = Record.objects.get(user=user)
    return record
    

def user_record(request, user_id):
    user = get_object_or_404(User, id=user_id)
    record = get_or_create_record(user)
    products = record.products.all()

    return render(request, 'record.html', {'user': user, 'products': products})

def add_product_to_record(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    record = get_or_create_record(request.user)
    record.products.add(product)
    record.save()