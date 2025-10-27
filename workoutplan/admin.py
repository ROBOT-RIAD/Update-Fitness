from django.contrib import admin
from .models import UserWorkoutFQA, WorkoutPlan, DailyWorkout, WorkoutEntry

# Register your models here.


@admin.register(UserWorkoutFQA)
class UserWorkoutFQAAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'training_environment',
        'training_style',
        'activeness_level',
        'days_per_week',
        'recent_injuries',
    )
    search_fields = ('user__email', 'training_environment', 'training_style', 'activeness_level')
    list_filter = ('training_environment', 'training_style', 'activeness_level')
    ordering = ('id',)




@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'fqa',
        'workout_plan_name',
        'workout_plan_name_spanish',
        'start_date',
        'end_date',
        'is_completed',
        'is_cancelled',
    )
    search_fields = ('user__email', 'workout_plan_name', 'workout_plan_name_spanish')
    list_filter = ('is_completed', 'is_cancelled', 'start_date', 'end_date')
    ordering = ('-start_date',)




@admin.register(DailyWorkout)
class DailyWorkoutAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'workout_plan',
        'date',
        'completed',
    )
    search_fields = ('workout_plan__workout_plan_name',)
    list_filter = ('completed', 'date')
    ordering = ('-date',)




@admin.register(WorkoutEntry)
class WorkoutEntryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'daily_workout',
        'workout',
        'completed',
        'series',
        'reps',
        'rest',
    )
    search_fields = ('daily_workout__workout_plan__workout_plan_name', 'workout__name')
    list_filter = ('completed',)
    ordering = ('id',)