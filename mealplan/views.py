from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import MealPlan, UserMealFQA , DailyMeal, MealSlot, MealSlotEntry
from meal.models import Meal
from accounts.models import Profile
from accounts.translations import translate_text
from datetime import date,timedelta
from .serializers import MealPlanSerializer,UserMealFQASerializer
from meal.serializers import MealSerializer
from workoutplan.serializers import WorkoutPlanSerializer
from workoutplan.models import WorkoutPlan
from .service import init_mealplan



# swagger 
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser


# Create your views here.


class GenerateMealPlan(APIView):
    permission_classes = [ permissions.IsAuthenticated]
    parser_classes = (MultiPartParser , FormParser)

    @swagger_auto_schema(
        operation_description="Generate meal plan based on user FQA",
        manual_parameters=[
            openapi.Parameter('weight', openapi.IN_FORM, description="Weight in kg", type=openapi.TYPE_NUMBER, required=False),
            openapi.Parameter('height', openapi.IN_FORM, description="Height in cm", type=openapi.TYPE_NUMBER, required=False),
            openapi.Parameter('injuries_discomfort', openapi.IN_FORM, description="Injuries or discomfort", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('allergies', openapi.IN_FORM, description="Allergies", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('medical_conditions', openapi.IN_FORM, description="Medical conditions", type=openapi.TYPE_STRING, required=False),

            openapi.Parameter('activeness_level', openapi.IN_FORM, description="Activeness level", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('event', openapi.IN_FORM, description="Event or goal", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('doctor_clearance', openapi.IN_FORM, description="Doctor's clearance", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('training_environment', openapi.IN_FORM, description="Training environment", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('preferences', openapi.IN_FORM, description="Food preferences", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('skipped', openapi.IN_FORM, description="Foods to avoid", type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            200: openapi.Response("Meal Plan Created Successfully"),
            400: "Bad Request",
            401: "Unauthorized",
        },
        tags=['Meal Plan'],
    )

    def post(self, request ,*args, **kwargs):
        user = request.user 
        lean = request.query_params.get('lean', 'EN').upper()

        profile , created = Profile.objects.get_or_create(user = user)
        data = request.data.copy()

        if lean!= 'EN':
            profile.weight = data.get("weight")
            profile.height =data.get("height")
            
            profile.injuries_discomfort = translate_text(data.get('injuries_discomfort'), 'EN'),
            profile.allergies = translate_text(data.get('allergies'), 'EN'),
            profile.medical_conditions= translate_text(data.get('profile.medical_conditions'), 'EN'),

            profile.injuries_discomfort_spanish= data.get('injuries_discomfort'),
            profile.allergies_spanish= data.get('injuries_discomfort'),
            profile.medical_conditions_spanish= data.get('injuries_discomfort'),
        else:
            profile.weight = data.get("weight")
            profile.height =data.get("height")

            profile.injuries_discomfort = data.get("injuries_discomfort")
            profile.allergies = data.get("allergies")
            profile.medical_conditions= data.get("medical_conditions")

            profile.injuries_discomfort_spanish = translate_text(data.get('injuries_discomfort'), 'ES'),
            profile.allergies_spanish = translate_text(data.get('allergies'), 'ES'),
            profile.medical_conditions_spanish = translate_text(data.get('medical_conditions'), 'ES'),
        

        profile.save()

        profile_json = {
            "gender": profile.gender,
            "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
            "weight": profile.weight,
            "height": profile.height,
            "injuries_discomfort": profile.injuries_discomfort,
            "allergies": profile.allergies,
            "medical_conditions": profile.medical_conditions,
        }

        fqadata ={}

        if lean != 'EN':
            fqadata = {
                "user" : user,
                
                "profile_json" : profile_json,

                #english,
                "training_environment": translate_text(data.get("training_environment"),'EN'),
                "activeness_level": translate_text(data.get("activeness_level"),'EN'),
                "event": translate_text(data.get("event"),'EN'),
                "doctor_clearance": translate_text(data.get("doctor_clearance"),'EN'),
                "preferences": translate_text(data.get("preferences"),'EN'),
                "skipped": translate_text(data.get("skipped"),'EN'),


                #spanish
                "training_environment_spanish": data.get("training_environment"),
                "activeness_level_spanish": data.get("activeness_level"),
                "event_spanish": data.get("event"),
                "doctor_clearance_spanish": data.get("doctor_clearance"),
                "preferences_spanish": data.get("preferences"),
                "skipped_spanish": data.get("skipped"),

            }
        else:
            fqadata = {

                "user" : user,
                "profile_json" : profile_json,

                #english
                "training_environment": data.get("training_environment"),
                "activeness_level": data.get("activeness_level"),
                "event": data.get("event"),
                "doctor_clearance": data.get("doctor_clearance"),
                "preferences": data.get("preferences"),
                "skipped": data.get("skipped"),
                


                #spanish
                "training_environment_spanish": translate_text(data.get("training_environment"),'ES'),
                "activeness_level_spanish": translate_text(data.get("activeness_level"),'ES'),
                "event_spanish": translate_text(data.get("event"),'ES'),
                "doctor_clearance_spanish": translate_text(data.get("doctor_clearance"),'ES'),
                "preferences_spanish": translate_text(data.get("preferences"),'ES'),
                "skipped_spanish": translate_text(data.get("skipped"),'ES'),
            }
        
        fqa = UserMealFQA.objects.create(**fqadata)


        start_date = date.today()
        end_date = start_date + timedelta(days=15)

        mealplan = MealPlan.objects.create(
            user=user,
            fqa=fqa,
            start_date=start_date,
            end_date=end_date,
            meal_plan_name="15 Days meal Plan",
            meal_plan_name_spanish="15 días de entrenamiento"
        )

        mealplan_data = MealPlanSerializer(mealplan).data
        fwq_data = UserMealFQASerializer(fqa).data

        all_meals = Meal.objects.all()
        meal_data = MealSerializer(all_meals, many = True).data

        active_workout_plan = (
            WorkoutPlan.objects
            .filter(user=user, is_completed=False, is_cancelled=False)
            .prefetch_related('daily_workouts__workouts__workout')
            .first()
        )
        active_workout_plan_data = WorkoutPlanSerializer(active_workout_plan).data or {}

        openaidata = {
            "fqa": fwq_data,
            "Mealplan": mealplan_data,
            "Active_Workout_Plan": active_workout_plan_data,
            "Meal_data": meal_data,
        }

        DailyMeal_MealEntry_data = init_mealplan(openaidata)



        for i in range(15):
            day_date = date.today() + timedelta(days=i)
            daily_meal = DailyMeal.objects.create(
                meal_plan=mealplan,
                date=day_date,
                completed=False,
            )

            # Create slots for that day
            for slot_data in DailyMeal_MealEntry_data:
                slot_type = slot_data["meal_plan"].lower()
                meal_slot = MealSlot.objects.create(
                    daily_meal=daily_meal,
                    slot_type=slot_type,
                    completed=False,
                )

                # Create entries inside each slot
                for meal_entry in slot_data["meals"]:

                    meal_id = meal_entry["meal"]

                    if not Meal.objects.filter(id=meal_id).exists():
                        print(f"⚠️ Skipping missing meal ID: {meal_id}")
                        continue

                    MealSlotEntry.objects.create(
                        meal_slot=meal_slot,
                        meal_id=meal_entry["meal"],
                        grams=meal_entry.get("grams", 0),
                        calories=meal_entry.get("calories", 0),
                        protein_g=meal_entry.get("protein_g", 0),
                        fat_g=meal_entry.get("fat_g", 0),
                        carbs_g=meal_entry.get("carbs_g", 0),
                        completed=False,
                    )
            
        result= ''
        if lean != 'EN':
            result = "Plan de comidas creado con éxito"
        else:
            result = "Meal Plan Created Successfully"

        return Response({
            "message": result,
            "meal_plan_id": mealplan.id,
            "days_created": 15,
        })

