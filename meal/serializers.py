from rest_framework import serializers
from .models import Meal


class MealCreateAndUpdateSerializer(serializers.ModelSerializer):
    # English fields
    category = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    food_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Spanish fields
    category_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    food_name_spanish = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Image field
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Meal
        fields = ['category', 'food_name','category_spanish', 'food_name_spanish', 'image',]




class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id','category','food_name','category_spanish','food_name_spanish','image','created_at','updated_at']



