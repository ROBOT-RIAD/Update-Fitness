from rest_framework import serializers
from .models import Workout



class WorkoutCreateAndUpdateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    exercise_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    workout_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    image = serializers.ImageField(required=False, allow_null=True)
    video = serializers.FileField(required=False, allow_null=True)

    workout_name_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    exercise_type_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Workout
        fields = ['code', 'exercise_type', 'workout_name', 'image', 'video','workout_name_spanish','exercise_type_spanish']




class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = ['id','code','exercise_type','workout_name','image','video','exercise_type_spanish','workout_name_spanish','updated_at','created_at']




