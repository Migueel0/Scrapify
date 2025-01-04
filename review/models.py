from django.db import models

from product.models import Product

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    author_name = models.CharField(max_length=50,blank=True)
    rating = models.FloatField(null=False)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    image = models.URLField(null=True)
    date = models.CharField(blank=True, max_length=50)
    
    def __str__(self):
        return self.product.name + ' - ' + self.author_name