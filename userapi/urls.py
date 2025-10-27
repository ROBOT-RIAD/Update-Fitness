from django.urls import path,include
from rest_framework.routers import DefaultRouter
from workoutplan.views import GenarateWorkoutPlan
from mealplan.views import GenerateMealPlan



router = DefaultRouter()



urlpatterns = [
    path('', include(router.urls)),
    path('genarete/workout/plan',GenarateWorkoutPlan.as_view(),name="genarate-workout-plan"),
    path('genarete/meal/plan',GenerateMealPlan.as_view(),name="genarate-meal-plan")

]