from django.urls import path,include
from rest_framework.routers import DefaultRouter
from workoutplan.views import GenarateWorkoutPlan
from mealplan.views import GenerateMealPlan
from .views import GetHomePageData,GenaratPageData,AllMealPlanGet,DailyMealwisedataget,AllWorkoutPlanGet,DailyWorkoutwisedataget,SingleMealSlotEntryGet,SingleWorkoutEntryGet,TodaysMealPlanGet,TodaysWorkoutPlanGet,UpdateTodayMealEntryStatus,UpdateWorkoutEntryStatus
from chatbot.views import FitnessChatAPIView



router = DefaultRouter()



urlpatterns = [
    path('', include(router.urls)),
    path('genarete/workout/plan',GenarateWorkoutPlan.as_view(),name="genarate-workout-plan"),
    path('genarete/meal/plan',GenerateMealPlan.as_view(),name="genarate-meal-plan"),
    path("stream-chat/", FitnessChatAPIView.as_view(), name="stream_chat"),
    path('homepage/', GetHomePageData.as_view(), name='get-homepage-data'),
    path('generate-page/', GenaratPageData.as_view(), name='generate-page'),
    path('mealplan/15days/', AllMealPlanGet.as_view(), name='mealplan-15days'),
    path('daily-meal-data/', DailyMealwisedataget.as_view(), name='daily-meal-data'),
    path('workoutplan/7days/', AllWorkoutPlanGet.as_view(), name='workout-plan-details'),
    path('daily-workout-data/', DailyWorkoutwisedataget.as_view(), name='daily-workout-detail'),
    path('meal-slot-entry/', SingleMealSlotEntryGet.as_view(), name='meal-slot-entry'),
    path('workout-entry/', SingleWorkoutEntryGet.as_view(), name='workout-entry'),
    path('meal-plan/', TodaysMealPlanGet.as_view(), name='todays-meal-plan'),
    path('todays-workout-plan/', TodaysWorkoutPlanGet.as_view(), name='todays-workout-plan'),
    path('meals/entry/update/', UpdateTodayMealEntryStatus.as_view(), name='update-meal-entry'),
    path('workouts/update-entry/<int:workout_entry_id>/',UpdateWorkoutEntryStatus.as_view(),name='update_workout_entry_status'),
]