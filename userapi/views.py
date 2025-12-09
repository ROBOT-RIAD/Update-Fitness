from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions,status
from rest_framework.response import Response
from mealplan.models import MealPlan, UserMealFQA , DailyMeal, MealSlot, MealSlotEntry
from meal.models import Meal
from datetime import datetime, date
from workoutplan.models import WorkoutPlan


# swagger 
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.


class GetHomePageData(APIView):
    permission_classes=[permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Get today's meal plan or specific date meal plan for the authenticated user.",
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="Optional date in YYYY-MM-DD format. If not provided, today's date is used.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'lean',
                openapi.IN_QUERY,
                description="Language code for translation (default is 'EN')",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
        tags=['Home']
    )
    def get(self , request):

        date_str = request.query_params.get("date")
        lean = request.query_params.get('lean', 'EN').upper()

        # Validate date
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                return Response({"error": "Invalid date format, use YYYY-MM-DD"}, status=400)
        else:
            target_date = date.today()

        # ============================================
        # 1️⃣ MEAL PLAN
        # ============================================
        mealplan = []
        active_meal_plan = MealPlan.objects.filter(
            user=request.user,
            is_completed=False,
            is_cancelled=False,
            start_date__lte=target_date,
            end_date__gte=target_date
        ).first()

        if active_meal_plan:
            daily_meal = active_meal_plan.daily_meals.filter(date=target_date).first()

            if daily_meal:
                for slot in daily_meal.meal_slots.all():
                    for entry in slot.entries.all():

                        if entry.meal:
                            meal_name = entry.meal.food_name if lean == "EN" else (
                                entry.meal.food_name_spanish or entry.meal.food_name
                            )
                        else:
                            meal_name = None

                        mealplan.append({
                            "slot_id": slot.id,
                            "slot_type": slot.slot_type,
                            "meal_slot_entry_id": entry.id,
                            "grams": entry.grams,
                            "calories": entry.calories,
                            "protein_g": entry.protein_g,
                            "fat_g": entry.fat_g,
                            "carbs_g": entry.carbs_g,
                            "completed": entry.completed,
                            "meal_id": entry.meal.id if entry.meal else None,
                            "meal_name": meal_name,
                        })

        # ============================================
        # 2️⃣ WORKOUT PLAN
        # ============================================
        workout_entries = []
        active_workout_plan = WorkoutPlan.objects.filter(
            user=request.user,
            is_completed=False,
            is_cancelled=False,
            start_date__lte=target_date,
            end_date__gte=target_date
        ).first()

        if active_workout_plan:
            daily_workout = active_workout_plan.daily_workouts.filter(date=target_date).first()

            if daily_workout:
                for entry in daily_workout.workouts.all():

                    if entry.workout:
                        workout_name = (
                            entry.workout.workout_name 
                            if lean == "EN" 
                            else (entry.workout.workout_name_spanish or entry.workout.workout_name)
                        )
                        exercise_type = (
                            entry.workout.exercise_type
                            if lean == "EN"
                            else (entry.workout.exercise_type_spanish or entry.workout.exercise_type)
                        )
                    else:
                        workout_name = None
                        exercise_type = None

                    workout_entries.append({
                        "id": entry.id,
                        "workout_id": entry.workout.id if entry.workout else None,
                        "workout_name": workout_name,
                        "workout_exercise_type": exercise_type,
                        "series": entry.series,
                        "reps": entry.reps,
                        "rest": entry.rest,
                        "completed": entry.completed
                    })


        # --------------------------
        # 3️⃣ AI Suggest Data
        # --------------------------
        ai_data = None
        if hasattr(request.user, 'ai_suggest_data'):
            suggest = request.user.ai_suggest_data
            ai_data = {
                "calorie_need_daily": suggest.calorie_need_daily,
                "water_liter": suggest.water_liter,
                "sleep_duration": str(suggest.sleep_duration),
            }

        return Response({
            "ai_suggest_data": ai_data,
            "Today_mealplan": mealplan,
            "Today_workoutplan": workout_entries,
        }, status=200)





class GenaratPageData(APIView):
    permission_classes=[permissions.IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'lean',
                openapi.IN_QUERY,
                description="Language code for translation (default is 'EN')",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
        tags=['Genarate page']
    )
    def get(self, request):
        user = request.user
        lean = request.GET.get('lean', 'EN').upper()
        today = date.today()

        active_meal = MealPlan.objects.filter(
            user=user,
            start_date__lte=today,
            end_date__gte=today,
            is_cancelled=False
        ).first()

        if not active_meal:
            active_meal = MealPlan.objects.filter(
                user=user,
                is_completed=True
            ).order_by('-end_date').first()

        mealplan_data = self.serialize_meal(active_meal , lean) if active_meal else []


        active_workout = WorkoutPlan.objects.filter(
            user=user,
            start_date__lte=today,
            end_date__gte=today,
            is_cancelled=False
        ).first()


        if not active_workout:
            active_workout = WorkoutPlan.objects.filter(
                user=user,
                is_completed=True
            ).order_by('-end_date').first()

        
        workoutplan_data = self.serialize_workout(active_workout, lean) if active_workout else []

        return Response({
            "mealplan": mealplan_data,
            "workoutplan": workoutplan_data,
        })
    

    def serialize_meal(self, plan, lean):
        if lean == "ES":
            return {
                "id": plan.id,
                "start_date": plan.start_date,
                "end_date": plan.end_date,
                "is_completed": plan.is_completed,
                "is_cancelled": plan.is_cancelled,
                "mealplan_name": plan.meal_plan_name_spanish
            }
        # default EN
        return {
            "id": plan.id,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
            "is_completed": plan.is_completed,
            "is_cancelled": plan.is_cancelled,
            "mealplan_name": plan.meal_plan_name
        }


    def serialize_workout(self, plan, lean):
        if lean == "ES":
            return {
                "id": plan.id,
                "start_date": plan.start_date,
                "end_date": plan.end_date,
                "is_completed": plan.is_completed,
                "is_cancelled": plan.is_cancelled,
                "workout_plan_name": plan.workout_plan_name_spanish
            }
        # default EN
        return {
            "id": plan.id,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
            "is_completed": plan.is_completed,
            "is_cancelled": plan.is_cancelled,
            "workout_plan_name": plan.workout_plan_name
        }


        








