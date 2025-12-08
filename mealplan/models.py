from django.db import models
from accounts.models import User
from datetime import date
from meal.models import Meal
from .constants import SLOT_CHOICES


# Create your models here.


class UserMealFQA(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name='user_meal_fqa')
     

    #english fields
    activeness_level = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., Beginner, Intermediate, Advanced")
    event = models.CharField(max_length=255, blank=True, null=True, help_text="Upcoming event or goal, e.g., Marathon, Wedding")
    doctor_clearance = models.CharField(max_length=255, blank=True, null=True, help_text="Doctor's clearance or recommendation, e.g., Cleared, Needs check-up")
    training_environment = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., Gym, Home, Outdoor")
    preferences = models.CharField(max_length=100 , blank=True,null = True)
    skipped = models.TextField(blank=True, null=True, help_text="Foods or ingredients to avoid")


    # Spanish fields
    activeness_level_spanish = models.CharField(max_length=255, blank=True, null=True)
    event_spanish = models.CharField(max_length=255, blank=True, null=True)
    doctor_clearance_spanish = models.CharField(max_length=255, blank=True, null=True)
    training_environment_spanish = models.CharField(max_length=255, blank=True, null=True)
    preferences_spanish = models.CharField(max_length=100 , blank=True,null = True)
    skipped_spanish = models.TextField(blank=True, null=True)


    profile_json = models.JSONField(default=dict, blank=True, null=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)





class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    fqa = models.OneToOneField(UserMealFQA, on_delete=models.CASCADE, related_name='meal_plan', blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)

    # English fields
    meal_plan_name = models.CharField(max_length=255)

    # Spanish fields
    meal_plan_name_spanish = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s meal plan ({self.start_date} to {self.end_date})"

    def mark_complete_if_expired(self):
        """Automatically mark plan as completed when past the end date."""
        if date.today() > self.end_date and not self.is_completed:
            self.is_completed = True
            self.save()





class DailyMeal(models.Model):
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='daily_meals')
    date = models.DateField()
    completed = models.BooleanField(default=False, help_text="Mark if the meals for the day are completed")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Daily meals for {self.meal_plan.user.email} on {self.date}"
    



class MealSlot(models.Model):
    daily_meal = models.ForeignKey(DailyMeal, on_delete=models.CASCADE, related_name='meal_slots')
    slot_type = models.CharField(max_length=20, choices=SLOT_CHOICES)
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)





class MealSlotEntry(models.Model):
    """Each MealSlot can have multiple food items (Meal)."""
    meal_slot = models.ForeignKey(MealSlot, on_delete=models.CASCADE, related_name='entries')
    meal = models.ForeignKey(Meal, on_delete=models.SET_NULL, null=True, blank=True)
    completed = models.BooleanField(default=False)

    grams = models.FloatField(default=0.0, help_text="Total weight of the meal in grams")
    calories = models.FloatField(default=0.0, help_text="Total calories in kcal")
    protein_g = models.FloatField(default=0.0, help_text="Protein content in grams")
    fat_g = models.FloatField(default=0.0, help_text="Fat content in grams")
    carbs_g = models.FloatField(default=0.0, help_text="Carbohydrate content in grams")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Update completion status automatically."""
        super().save(*args, **kwargs)

        # Update slot completion
        slot = self.meal_slot
        all_completed = slot.entries.filter(completed=False).count() == 0
        if all_completed and not slot.completed:
            slot.completed = True
            slot.save()
        elif not all_completed and slot.completed:
            slot.completed = False
            slot.save()

        # Update daily completion
        daily = slot.daily_meal
        all_slots_completed = daily.meal_slots.filter(completed=False).count() == 0
        if all_slots_completed and not daily.completed:
            daily.completed = True
            daily.save()
        elif not all_slots_completed and daily.completed:
            daily.completed = False
            daily.save()

    def __str__(self):
        return f"{self.meal} - {self.meal_slot.get_slot_type_display()} ({self.meal_slot.daily_meal.date})"
    


    