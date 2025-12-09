from django.urls import path,include
from rest_framework.routers import DefaultRouter
from workoutplan.views import GenarateWorkoutPlan
from mealplan.views import GenerateMealPlan
from .views import GetHomePageData,GenaratPageData
from chatbot.views import FitnessChatAPIView



router = DefaultRouter()



urlpatterns = [
    path('', include(router.urls)),
    path('genarete/workout/plan',GenarateWorkoutPlan.as_view(),name="genarate-workout-plan"),
    path('genarete/meal/plan',GenerateMealPlan.as_view(),name="genarate-meal-plan"),
    path("stream-chat/", FitnessChatAPIView.as_view(), name="stream_chat"),
    path('homepage/', GetHomePageData.as_view(), name='get-homepage-data'),
    path('generate-page/', GenaratPageData.as_view(), name='generate-page'),
]