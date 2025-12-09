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




class AllMealPlanGet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'mealplan_id',
                openapi.IN_QUERY,
                description="ID of the meal plan to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'lean',
                openapi.IN_QUERY,
                description="Language code for translation (default is 'EN')",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
        tags=['15 days Mealplan get API']
    )
    def get(self, request):
        user = request.user
        mealplan_id = request.query_params.get("mealplan_id")
        lean = request.query_params.get("lean", "EN").upper()

        if not mealplan_id:
            return Response(
                {"error": "mealplan_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            meal_plan = MealPlan.objects.get(id=mealplan_id, user=user)
        except MealPlan.DoesNotExist:
            return Response(
                {"error": "Meal plan not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        daily_meals = (
            meal_plan.daily_meals
            .prefetch_related("meal_slots__entries__meal")
            .order_by("date")
        )

        data = []
        total_calories = 0
        total_meals = 0

        for daily in daily_meals:
            day_meals = []
            day_calories = 0
            for slot in daily.meal_slots.all():
                for entry in slot.entries.all():
                    meal_name = (
                        entry.meal.food_name_spanish
                        if lean == "ES" else entry.meal.food_name
                    ) if entry.meal else None

                    day_calories += entry.calories or 0
                    total_meals += 1

                    day_meals.append({
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
                        "image": entry.meal.image.url if entry.meal and entry.meal.image and hasattr(entry.meal.image, 'url') else None
                    })
            total_calories += day_calories


            data.append({
                "DailyMeal_id":daily.id,
                "date": daily.date,
                "this_day_meal": day_meals
            })
        data = data[:15]

        total_days = len(data)
        avg_calories = total_calories / total_days if total_days > 0 else 0

        response_data = {
            "status": {
                "total_day": total_days,
                "average_per_day_calorie": round(avg_calories, 2),
                "total_meal": total_meals,
            },
            "data": data
        }
        return Response(response_data, status=status.HTTP_200_OK)



class DailyMealwisedataget(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'daily_id',
                openapi.IN_QUERY,
                description="ID of the DailyMeal to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'lean',
                openapi.IN_QUERY,
                description="Language code for translation (default is 'EN')",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
        tags=['Daily Meal Wise Data Get API']
    )
    def get(self, request):
        user = request.user
        daily_id = request.query_params.get("daily_id")
        lean = request.query_params.get("lean", "EN").upper()

        # ✅ Validate required parameter
        if not daily_id:
            return Response(
                {"error": "daily_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Find the DailyMeal
        try:
            daily_meal = DailyMeal.objects.select_related("meal_plan__user").prefetch_related(
                "meal_slots__entries__meal"
            ).get(id=daily_id, meal_plan__user=user)
        except DailyMeal.DoesNotExist:
            return Response(
                {"error": "Daily meal not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ Build response data
        day_meals = []
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        total_meals = 0

        for slot in daily_meal.meal_slots.all():
            for entry in slot.entries.all():
                if not entry.meal:
                    continue

                meal_name = (
                    entry.meal.food_name_spanish
                    if lean == "ES" else entry.meal.food_name
                )

                image_url = (
                    entry.meal.image.url
                    if entry.meal.image and hasattr(entry.meal.image, "url")
                    else None
                )

                # ✅ Totals
                total_calories += entry.calories or 0
                total_protein += entry.protein_g or 0
                total_fat += entry.fat_g or 0
                total_carbs += entry.carbs_g or 0
                total_meals += 1

                day_meals.append({
                    "slot_id": slot.id,
                    "slot_type": slot.slot_type,
                    "meal_slot_entry_id": entry.id,
                    "grams": entry.grams,
                    "calories": entry.calories,
                    "protein_g": entry.protein_g,
                    "fat_g": entry.fat_g,
                    "carbs_g": entry.carbs_g,
                    "completed": entry.completed,
                    "meal_id": entry.meal.id,
                    "meal_name": meal_name,
                    "image": image_url
                })

        response_data = {
            "status": {
                "date": daily_meal.date,
                "this_day_total_calories": round(total_calories, 2),
                "this_day_total_protein": round(total_protein, 2),
                "this_day_total_fat": round(total_fat, 2),
                "this_day_total_carbs": round(total_carbs, 2),
            },
            "data": {
                "this_day_meal": day_meals,
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

    







