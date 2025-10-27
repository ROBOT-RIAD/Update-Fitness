from django.contrib import admin
from .models import UserMealFQA

# Register your models here.


@admin.register(UserMealFQA)
class UserMealFQAAdmin(admin.ModelAdmin):
    list_display = ('id','user','activeness_level','event','doctor_clearance','training_environment','preferences','created_at','updated_at')
    list_filter = ('activeness_level','doctor_clearance','training_environment','created_at',)
    search_fields = ('user__email','user__username','activeness_level','event','preferences','skipped',)
    ordering = ('-created_at',)