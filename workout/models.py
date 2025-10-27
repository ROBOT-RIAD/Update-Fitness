from django.db import models
# from .constants import EXERCISE_TYPE_CHOICES,EXERCISE_TYPE_CHOICES_SPANISH

# Create your models here.


class Workout(models.Model):
    code = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='media/workouts/images/', blank=True, null=True)
    video = models.FileField(upload_to='media/workouts/videos/', blank=True, null=True)

    #english
    exercise_type = models.CharField(max_length=50,blank=True, null=True)
    workout_name = models.CharField(max_length=100,blank=True, null=True)


    #spanish
    exercise_type_spanish = models.CharField(max_length=50,blank=True, null=True)
    workout_name_spanish = models.CharField(max_length=150, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.workout_name} ({self.exercise_type})"






