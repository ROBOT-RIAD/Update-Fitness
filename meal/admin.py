from django.contrib import admin
from .models import Meal

# Register your models here.

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('id','food_name','category','subcategory','food_name_spanish','category_spanish','subcategory_spanish','created_at','updated_at',)
    list_filter = ('category', 'subcategory', 'created_at')
    search_fields = ('food_name','food_name_spanish','category','subcategory',)
    ordering = ('-created_at',)


