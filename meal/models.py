from django.db import models

class Meal(models.Model):

    # English fields
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100)
    food_name = models.CharField(max_length=255)

    # Spanish fields
    category_spanish = models.CharField(max_length=100, blank=True, null=True)
    subcategory_spanish = models.CharField(max_length=100, blank=True, null=True)
    food_name_spanish = models.CharField(max_length=255, blank=True, null=True)

    # Image field
    image = models.ImageField(upload_to='media/meals/image', blank=True, null=True)

    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.food_name} ({self.category} - {self.subcategory})"

