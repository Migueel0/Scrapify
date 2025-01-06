from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=128, null=False)
    price = models.CharField(max_length=10,null=False)
    rating = models.FloatField(null=True)
    image = models.URLField(null=True)
    link = models.URLField(null=True)
    store = models.CharField(max_length=128, null=False)
    

    def __str__(self):
        return self.name
