from rest_framework import serializers
from .models import UserMealFQA , MealPlan



class UserMealFQASerializer(serializers.ModelSerializer):
    # profile fields
    weight = serializers.FloatField(required=False, allow_null=True)
    height = serializers.FloatField(required=False, allow_null=True)
    injuries_discomfort = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    allergies = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    medical_conditions = serializers.CharField(required=False, allow_blank=True, allow_null=True)


    # English fields
    activeness_level = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    event = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    doctor_clearance = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    training_environment = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    preferences = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    skipped = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Spanish fields
    activeness_level_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    event_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    doctor_clearance_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    training_environment_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    preferences_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    skipped_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)


    # Extra profile JSON
    profile_json = serializers.JSONField(required=False)

    class Meta:
        model = UserMealFQA
        fields = [
            'weight', 'height', 'injuries_discomfort', 'allergies', 'medical_conditions',
            'activeness_level', 'event', 'doctor_clearance', 'training_environment',
            'preferences', 'skipped',
            'activeness_level_spanish', 'event_spanish', 'doctor_clearance_spanish',
            'training_environment_spanish', 'preferences_spanish', 'skipped_spanish',
            'profile_json'
        ]




class MealPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlan
        fields = [
            'id', 'user', 'fqa', 'start_date', 'end_date', 'is_completed',
            'is_cancelled', 'meal_plan_name', 'meal_plan_name_spanish',
            'created_at', 'updated_at'
        ]



