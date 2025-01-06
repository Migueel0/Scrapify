from django.db import models

from user.models import User
from product.models import Product

class Record(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(Product, related_name='products')

    def __str__(self):
        return f"Record for {self.user.username} on {self.date}"
