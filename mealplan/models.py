from django.db import models
from accounts.models import User
from datetime import date
from meal.models import Meal

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
    




class MealEntry(models.Model):
    daily_meal = models.ForeignKey(DailyMeal, on_delete=models.CASCADE, related_name='meals')
    meal = models.ForeignKey(Meal, on_delete=models.SET_NULL, null=True, blank=True)
    completed = models.BooleanField(default=False, help_text="Mark if the meal was eaten")
    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Auto-update daily completion status when all meals are done."""
        super().save(*args, **kwargs)

        all_completed = self.daily_meal.meals.filter(completed=False).count() == 0
        if all_completed and not self.daily_meal.completed:
            self.daily_meal.completed = True
            self.daily_meal.save()
        elif not all_completed and self.daily_meal.completed:
            self.daily_meal.completed = False
            self.daily_meal.save()

    def __str__(self):
        return f"{self.meal} - {self.daily_meal.date}"
    


    