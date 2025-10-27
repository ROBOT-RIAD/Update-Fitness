from django.urls import path,include
from rest_framework.routers import DefaultRouter
from workout.views import AdminWorkoutBulkUploadAPIView, AdminWorkoutCreateAPIView,AdminWorkoutUpdateAPIView,AdminWorkoutListAPIView,AdminWorkoutRetrieveAPIView,AdminWorkoutDeleteAPIView
from meal.views import AdminMealRetrieveAPIView, AdminMealcreateApiview,AdminMealUpdateApiview,AdminMealDeleteAPIView,AdminMealListAPIView




router = DefaultRouter()




urlpatterns = [
    path('', include(router.urls)),

    path('all/workout/', AdminWorkoutListAPIView.as_view(), name='admin-workout-list'),
    path('workout/',AdminWorkoutCreateAPIView.as_view(),name="create-workout"),
    path('workout/<int:pk>',AdminWorkoutUpdateAPIView.as_view(),name="update-workout"),
    path('workout/<int:pk>/', AdminWorkoutRetrieveAPIView.as_view(), name='admin-workout-retrieve'),
    path('workout/delete/<int:pk>/', AdminWorkoutDeleteAPIView.as_view(), name='admin-workout-delete'),
    path('admin/workouts/bulk-upload/', AdminWorkoutBulkUploadAPIView.as_view(), name='admin-workout-bulk-upload'),


    path('meal/',AdminMealcreateApiview.as_view(),name ='create-meal'),
    path('all/meal/',AdminMealListAPIView.as_view(),name ='all-meal'),
    path('meal/<int:pk>/', AdminMealRetrieveAPIView.as_view(), name='admin-meal-retrieve'),
    path('meal/<int:pk>', AdminMealUpdateApiview.as_view(), name='admin-meal-update'),
    path('meal/delete/<int:pk>/', AdminMealDeleteAPIView.as_view(), name='admin-meal-delete'),

]