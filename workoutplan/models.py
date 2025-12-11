from django.db import models
from accounts.models import User
from workout.models import Workout
from datetime import date

# Create your models here.



class UserWorkoutFQA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_workout_fqas')
    session_duration = models.CharField(max_length=100, blank=True, null=True, help_text="Preferred session length, e.g., 30 min, 1 hour")
    days_per_week = models.IntegerField(blank=True, null=True, help_text="Preferred number of training days per week")


    #English
    training_environment = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., Gym, Home, Outdoor")
    equipments_access = models.TextField(blank=True, null=True, help_text="List of available equipment, e.g., Dumbbells, Treadmill")
    training_style = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., Strength, Cardio, HIIT, Yoga")
    activeness_level = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., Beginner, Intermediate, Advanced")
    motivation_factor = models.TextField(blank=True, null=True, help_text="Reason or motivation for training, e.g., Weight loss, Muscle gain")
    event = models.CharField(max_length=255, blank=True, null=True, help_text="Upcoming event or goal, e.g., Marathon, Wedding")
    recent_injuries = models.TextField(blank=True, null=True, help_text="Describe any recent injuries or physical limitations")
    fitness_level = models.CharField(max_length=255, blank=True, null=True, help_text="Overall fitness level, e.g., Low, Moderate, High")
    doctor_clearance = models.CharField(max_length=255, blank=True, null=True, help_text="Doctor's clearance or recommendation, e.g., Cleared, Needs check-up")
    

    # Spanish fields
    training_environment_spanish = models.CharField(max_length=255, blank=True, null=True)
    equipments_access_spanish = models.TextField(blank=True, null=True)
    training_style_spanish = models.CharField(max_length=255, blank=True, null=True)
    activeness_level_spanish = models.CharField(max_length=255, blank=True, null=True)
    motivation_factor_spanish = models.TextField(blank=True, null=True)
    event_spanish = models.CharField(max_length=255, blank=True, null=True)
    recent_injuries_spanish = models.TextField(blank=True, null=True)
    fitness_level_spanish = models.CharField(max_length=255, blank=True, null=True)
    doctor_clearance_spanish = models.CharField(max_length=255, blank=True, null=True)


    profile_json = models.JSONField(default=dict, blank=True, null=True, help_text="Extra profile info in JSON format")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class WorkoutPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_plans')
    fqa = models.OneToOneField(UserWorkoutFQA, on_delete=models.CASCADE, related_name='workout_plan', blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)

    #english
    workout_plan_name = models.CharField(max_length=255)

    #spanish
    workout_plan_name_spanish = models.CharField(max_length=255)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s workout plan ({self.start_date} to {self.end_date})"
    
    def mark_complete_if_expired(self):
        if date.today() > self.end_date and not self.is_completed:
            self.is_completed = True
            self.save()




class DailyWorkout(models.Model):
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='daily_workouts')
    date = models.DateField()
    completed = models.BooleanField(default=False, help_text="Mark if the workout is completed")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    



class WorkoutEntry(models.Model):
    daily_workout = models.ForeignKey(DailyWorkout, on_delete=models.CASCADE, related_name='workouts')
    workout = models.ForeignKey(Workout, on_delete=models.SET_NULL, null=True, blank=True)
    completed = models.BooleanField(default=False)
    series = models.PositiveIntegerField(default=1, help_text="Number of sets performed")
    reps = models.PositiveIntegerField(default=10, help_text="Repetitions per set") 
    rest = models.PositiveIntegerField(help_text="Repetitions per set")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        all_completed = self.daily_workout.workouts.filter(completed=False).count() == 0
        if all_completed and not self.daily_workout.completed:
            self.daily_workout.completed = True
            self.daily_workout.save()
        elif not all_completed and self.daily_workout.completed:
            self.daily_workout.completed = False
            self.daily_workout.save()






