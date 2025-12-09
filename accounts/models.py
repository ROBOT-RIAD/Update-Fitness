from django.contrib.auth.models import AbstractUser
from django.db import models
from .constants import ROLE_CHOICES,GENDER





class User(AbstractUser):
    # extra field add
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10,choices=ROLE_CHOICES,default="user")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='media/user_images/', null=True, blank=True)
    fullname = models.CharField(max_length=200, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True ,help_text="Weight in kilograms")
    height = models.FloatField(null=True, blank=True,help_text="Height in centimeters")
    abdominal = models.FloatField(null=True, blank=True)
    sacroiliac = models.FloatField(null=True, blank=True)
    subscapularis = models.FloatField(null=True, blank=True)
    triceps = models.FloatField(null=True, blank=True)
    train_duration = models.TextField(null=True, blank=True)


    #english data 
    gender = models.CharField(max_length=20, choices=GENDER, null=True, blank=True)
    trainer = models.TextField(null=True, blank=True)
    fitness_goals = models.TextField(null=True, blank=True)
    injuries_discomfort = models.TextField(null=True, blank=True)
    dietary_preferences = models.TextField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    medical_conditions = models.TextField(null=True, blank=True)


    #spanish data 
    gender_spanish =models.TextField(null=True, blank=True)
    trainer_spanish =models.TextField(null=True, blank=True)
    fitness_goals_spanish =models.TextField(null=True, blank=True)
    injuries_discomfort_spanish=models.TextField(null=True, blank=True)
    dietary_preferences_spanish =models.TextField(null=True, blank=True)
    allergies_spanish =models.TextField(null=True, blank=True)
    medical_conditions_spanish= models.TextField(null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
   



class AISuggestData(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='ai_suggest_data',null=True,blank=True)
    calorie_need_daily = models.PositiveIntegerField(help_text="Daily calorie need in Kcal")
    water_liter = models.FloatField(help_text="Daily water intake recommendation in liters")
    sleep_duration = models.DurationField(help_text="Total recommended sleep duration")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Suggestion for {self.user} on {self.created_at.date()}"



    