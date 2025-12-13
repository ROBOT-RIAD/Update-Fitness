from django.db import models
from accounts.models import User

# Create your models here.


class ChatBotMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot_messages")
    user_input = models.TextField()
    ai_response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.user_input[:50]}"
    



from pydantic import BaseModel, Field
from datetime import date as dt

class Meal(BaseModel):
    id: str = Field(..., description="Unique identifier for the meal")
    date: dt = Field(..., description="Date of the meal")
    meal_name: str = Field(..., description="Name of the meal")
    grams: int = Field(..., description="Weight of the meal in grams")
    calories: int = Field(..., description="Caloric content of the meal")
    protein_g: int = Field(..., description="Protein content in grams")
    fat_g : int = Field(..., description="Fat content in grams")
    carbs_g: int = Field(..., description="Carbohydrate content in grams")

class MealList(BaseModel):
    entries: list[Meal] = Field(..., description="List of all meals")

class Workout(BaseModel):
    id: str = Field(..., description="Unique identifier for the workout")
    date: dt = Field(..., description="Date of the workout")
    workout_name: str = Field(..., description="Name of the workout exercise")
    series: int = Field(..., description="Number of series for the workout")
    reps: int = Field(..., description="Number of repetitions per series")
    rest: int = Field(..., description="Rest time between series in seconds")

class WorkoutList(BaseModel):
    workouts: list[Workout] = Field(..., description="List of all workouts")