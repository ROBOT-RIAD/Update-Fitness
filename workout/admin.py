from django.contrib import admin
from .models import Workout

# Register your models here.

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'code',
        'exercise_type',
        'workout_name',
        'exercise_type_spanish',
        'workout_name_spanish',
        'created_at',
        'updated_at',
    )
    search_fields = ('code', 'workout_name', 'workout_name_spanish')
    list_filter = ('exercise_type', 'exercise_type_spanish')
