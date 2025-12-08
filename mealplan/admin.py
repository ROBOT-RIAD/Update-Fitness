from django.contrib import admin
from .models import UserMealFQA, MealPlan, DailyMeal, MealSlot, MealSlotEntry



# ------------------------------
# UserMealFQA Admin
# ------------------------------
@admin.register(UserMealFQA)
class UserMealFQAAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'activeness_level', 'event', 'doctor_clearance',
        'training_environment', 'created_at', 'updated_at'
    )
    search_fields = (
        'user__email', 'activeness_level', 'event', 'training_environment'
    )
    list_filter = ('activeness_level', 'created_at')




# ------------------------------
# MealPlan Admin
# ------------------------------
@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'meal_plan_name', 'start_date', 'end_date',
        'is_completed', 'is_cancelled', 'created_at'
    )
    search_fields = ('user__email', 'meal_plan_name')
    list_filter = ('is_completed', 'is_cancelled', 'start_date', 'end_date')




# ------------------------------
# DailyMeal Admin
# ------------------------------
@admin.register(DailyMeal)
class DailyMealAdmin(admin.ModelAdmin):
    list_display = ('meal_plan', 'date', 'completed', 'updated_at')
    search_fields = ('meal_plan__user__email', 'date')
    list_filter = ('completed', 'date')




# ------------------------------
# MealSlot Admin
# ------------------------------
@admin.register(MealSlot)
class MealSlotAdmin(admin.ModelAdmin):
    list_display = ('daily_meal', 'slot_type', 'completed', 'updated_at')
    search_fields = ('daily_meal__meal_plan__user__email', 'slot_type')
    list_filter = ('slot_type', 'completed')




# ------------------------------
# MealSlotEntry Admin
# ------------------------------
@admin.register(MealSlotEntry)
class MealSlotEntryAdmin(admin.ModelAdmin):
    list_display = (
        'meal_slot', 'meal', 'completed', 'grams', 'calories',
        'protein_g', 'fat_g', 'carbs_g', 'created_at'
    )
    search_fields = (
        'meal_slot__daily_meal__meal_plan__user__email',
        'meal__food_name'
    )
    list_filter = ('completed',)





