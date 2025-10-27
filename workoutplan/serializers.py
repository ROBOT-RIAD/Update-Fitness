from rest_framework import serializers
from workoutplan.models import UserWorkoutFQA,WorkoutPlan


class UserWorkoutFQASerializer(serializers.ModelSerializer):
    # Profile fields
    weight = serializers.FloatField(required=False, allow_null=True)
    height = serializers.FloatField(required=False, allow_null=True)
    injuries_discomfort = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    allergies = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    medical_conditions = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    session_duration = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    days_per_week = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # English FQA fields
    training_environment = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    equipments_access = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    training_style = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    activeness_level = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    motivation_factor = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    event = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    recent_injuries = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Spanish fields
    training_environment_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    equipments_access_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    training_style_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    activeness_level_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    motivation_factor_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    event_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    recent_injuries_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Extra profile JSON
    profile_json = serializers.JSONField(required=False)

    class Meta:
        model = UserWorkoutFQA
        fields = [
            'weight', 'height', 'injuries_discomfort', 'allergies', 'medical_conditions',
            'training_environment', 'equipments_access', 'training_style', 'activeness_level',
            'motivation_factor', 'event', 'session_duration', 'days_per_week', 'recent_injuries',
            'training_environment_spanish', 'equipments_access_spanish', 'training_style_spanish',
            'activeness_level_spanish', 'motivation_factor_spanish', 'event_spanish', 'recent_injuries_spanish',
            'profile_json','fitness_level','fitness_level_spanish','doctor_clearance','doctor_clearance_spanish'
        ]




class WorkoutPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutPlan
        fields = '__all__'