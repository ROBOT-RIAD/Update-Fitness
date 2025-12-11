from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions,status
from rest_framework.response import Response
from mealplan.models import MealPlan, UserMealFQA , DailyMeal, MealSlot, MealSlotEntry
from meal.models import Meal
from datetime import datetime, date
from workoutplan.models import WorkoutPlan,DailyWorkout,WorkoutEntry

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



class SingleMealSlotEntryGet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'meal_slot_entry_id',
                openapi.IN_QUERY,
                description="ID of the MealSlotEntry to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'lean',
                openapi.IN_QUERY,
                description="Language code for translation (default is 'EN', supports 'ES')",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
        tags=['Single Meal Slot Entry Get API']
    )
    def get(self, request):
        user = request.user
        entry_id = request.query_params.get("meal_slot_entry_id")
        lean = request.query_params.get("lean", "EN").upper()

        if not entry_id:
            return Response(
                {"error": "meal_slot_entry_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            entry = MealSlotEntry.objects.select_related(
                "meal", "meal_slot__daily_meal__meal_plan__user"
            ).get(
                id=entry_id, 
                meal_slot__daily_meal__meal_plan__user=user
            )
        except MealSlotEntry.DoesNotExist:
            return Response(
                {"error": "MealSlotEntry not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        meal_name = (
            entry.meal.food_name_spanish
            if lean == "ES" else entry.meal.food_name
        ) if entry.meal else None

        image_url = (
            request.build_absolute_uri(entry.meal.image.url)
            if entry.meal and entry.meal.image else None
        )

        response_data = {
            "meal_slot_entry_id": entry.id,
            "slot_id": entry.meal_slot.id if entry.meal_slot else None,
            "slot_type": entry.meal_slot.slot_type if entry.meal_slot else None,
            "meal_id": entry.meal.id if entry.meal else None,
            "meal_name": meal_name,
            "grams": entry.grams,
            "calories": entry.calories,
            "protein_g": entry.protein_g,
            "fat_g": entry.fat_g,
            "carbs_g": entry.carbs_g,
            "completed": entry.completed,
            "image": image_url,
        }

        return Response(response_data, status=status.HTTP_200_OK)




class AllWorkoutPlanGet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'workout_plan_id',
                openapi.IN_QUERY,
                description="ID of the WorkoutPlan to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'lean',
                openapi.IN_QUERY,
                description="Language code for translation (default: EN, supports ES)",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
        tags=['7 days Workout Plan Get API']
    )
    def get(self, request):
        user = request.user
        workout_plan_id = request.query_params.get("workout_plan_id")
        lean = request.query_params.get("lean", "EN").upper()

        if not workout_plan_id:
            return Response(
                {"error": "workout_plan_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        

        try:
            workout_plan = WorkoutPlan.objects.prefetch_related(
                "daily_workouts__workouts__workout"
            ).get(id=workout_plan_id, user=user)
        except WorkoutPlan.DoesNotExist:
            return Response(
                {"error": "WorkoutPlan not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        plan_data = []
        total_workouts = 0
        total_completed_workouts = 0
        for daily in workout_plan.daily_workouts.all():
            daily_data = {
                "daily_workout_id": daily.id,
                "date": daily.date,
                "completed": daily.completed,
                "workouts": []
            }

            for entry in daily.workouts.all():
                if not entry.workout:
                    continue

                total_workouts += 1
                if entry.completed:
                    total_completed_workouts += 1

                workout_name = (
                    entry.workout.workout_name_spanish
                    if lean == "ES" else entry.workout.workout_name
                )

                exercise_type = (
                    entry.workout.exercise_type_spanish
                    if lean == "ES" else entry.workout.exercise_type_spanish
                )



                image_url = (
                    entry.workout.image.url
                    if entry.workout.image and hasattr(entry.workout.image, "url")
                    else None
                )

                daily_data["workouts"].append({
                    "workout_entry_id": entry.id,
                    "workout_id": entry.workout.id,
                    "workout_name": workout_name,
                    "exercise_type":exercise_type,
                    "series": entry.series,
                    "reps": entry.reps,
                    "rest": entry.rest,
                    "completed": entry.completed,
                    "image": image_url,
                })

            plan_data.append(daily_data)

        response_data = {
            "status": {
                "days": workout_plan.daily_workouts.count(),
                "total_workout": total_workouts,
                "total_completed_workout": total_completed_workouts
            },
            "daily_workouts": plan_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
        

        
class DailyWorkoutwisedataget(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'daily_workout_id',
                openapi.IN_QUERY,
                description="ID of the DailyWorkout to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'lean',
                openapi.IN_QUERY,
                description="Language code for translation (default is 'EN', supports 'ES')",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
        tags=['Daily workout Wise Data Get API']
    )
    def get(self, request):
        daily_workout_id = request.query_params.get('daily_workout_id')
        lean = request.query_params.get('lean', 'EN').upper()

        if not daily_workout_id:
            return Response(
                {"error": "daily_workout_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            daily_workout = DailyWorkout.objects.get(
                id=daily_workout_id, workout_plan__user=request.user
            )
        except DailyWorkout.DoesNotExist:
            return Response(
                {"error": "Daily workout not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        entries = WorkoutEntry.objects.filter(daily_workout=daily_workout)

        total_workout = entries.count()
        total_completed_workout = entries.filter(completed=True).count()
        total_incompleted_workout = total_workout - total_completed_workout

        # Build response data
        workouts_data = []
        for entry in entries:
            if not entry.workout:
                continue

            workout_name = (
                entry.workout.workout_name_spanish
                if lean == "ES" else entry.workout.workout_name
            )

            exercise_type = (
                entry.workout.exercise_type_spanish
                if lean == "ES" else entry.workout.exercise_type
            )

            image_url = (
                request.build_absolute_uri(entry.workout.image.url)
                if entry.workout.image else None
            )

            workouts_data.append({
                "workout_entry_id": entry.id,
                "workout_id": entry.workout.id,
                "workout_name": workout_name,
                "exercise_type": exercise_type,
                "series": entry.series,
                "reps": entry.reps,
                "rest": entry.rest,
                "completed": entry.completed,
                "image": image_url,
            })

        response_data = {
            "status": {
                "total_workout": total_workout,
                "total_completed_workout": total_completed_workout,
                "total_incompleted_workout": total_incompleted_workout,
            },
            "daily_workout": {
                "date": daily_workout.date,
                "completed": daily_workout.completed,
                "workouts": workouts_data
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)




class SingleWorkoutEntryGet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'workout_entry_id',
                openapi.IN_QUERY,
                description="ID of the WorkoutEntry to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'lean',
                openapi.IN_QUERY,
                description="Language code for translation (default is 'EN', supports 'ES')",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
        tags=['Single Workout Entry Get API']
    )
    def get(self, request):
        workout_entry_id = request.query_params.get("workout_entry_id")
        lean = request.query_params.get("lean", "EN").upper()

        if not workout_entry_id:
            return Response(
                {"error": "workout_entry_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Ensure the entry belongs to the authenticated user
        try:
            entry = WorkoutEntry.objects.select_related(
                "workout", "daily_workout__workout_plan__user"
            ).get(
                id=workout_entry_id,
                daily_workout__workout_plan__user=request.user
            )
        except WorkoutEntry.DoesNotExist:
            return Response(
                {"error": "WorkoutEntry not found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ Language-based fields
        workout_name = (
            entry.workout.workout_name_spanish
            if lean == "ES" else entry.workout.workout_name
        )

        exercise_type = (
            entry.workout.exercise_type_spanish
            if lean == "ES" else entry.workout.exercise_type
        )

        image_url = (
            request.build_absolute_uri(entry.workout.image.url)
            if entry.workout and entry.workout.image else None
        )

        # ✅ Build response
        data = {
            "workout_entry_id": entry.id,
            "workout_id": entry.workout.id if entry.workout else None,
            "workout_name": workout_name,
            "exercise_type": exercise_type,
            "series": entry.series,
            "reps": entry.reps,
            "rest": entry.rest,
            "completed": entry.completed,
            "image": image_url,
        }

        return Response(data, status=status.HTTP_200_OK)





class TodaysMealPlanGet(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
                description="Language code for translation (default is 'EN', supports 'ES')",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
        tags=['Single Date / Today Meal Plan']
    )
    def get(self, request):
        # Get query params
        date_str = request.query_params.get("date")
        lean = request.query_params.get("lean", "EN").upper()

        # Validate date
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format, use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            target_date = date.today()

        # Get active meal plan for user
        active_meal_plan = MealPlan.objects.filter(
            user=request.user,
            is_completed=False,
            is_cancelled=False,
            start_date__lte=target_date,
            end_date__gte=target_date
        ).first()

        if not active_meal_plan:
            return Response(
                {"message": "No active meal plan found for this date."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get daily meal for target date
        daily_meal = active_meal_plan.daily_meals.filter(date=target_date).first()
        if not daily_meal:
            return Response(
                {"message": "No daily meal found for this date."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Build response
        mealplan_data = []
        for slot in daily_meal.meal_slots.all():
            for entry in slot.entries.all():
                meal_name = None
                if entry.meal:
                    meal_name = entry.meal.food_name if lean == "EN" else (
                        entry.meal.food_name_spanish or entry.meal.food_name
                    )

                mealplan_data.append({
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

        all_15_day_total_calories = 0
        all_15_day_total_protein_g = 0
        all_15_day_total_fat_g = 0
        all_15_day_total_carbs_g = 0

        complete_total_calories = 0
        complete_total_protein_g = 0
        complete_total_fat_g = 0
        complete_total_carbs_g = 0

        all_daily_meals = active_meal_plan.daily_meals.all()
        for daily in all_daily_meals:
            for slot in daily.meal_slots.all():
                for entry in slot.entries.all():
                    all_15_day_total_calories += entry.calories or 0
                    all_15_day_total_protein_g += entry.protein_g or 0
                    all_15_day_total_fat_g += entry.fat_g or 0
                    all_15_day_total_carbs_g += entry.carbs_g or 0

                    if entry.completed:
                        complete_total_calories += entry.calories or 0
                        complete_total_protein_g += entry.protein_g or 0
                        complete_total_fat_g += entry.fat_g or 0
                        complete_total_carbs_g += entry.carbs_g or 0

        response_data = {
            "status": {
                "all_15_day_total_calories": round(all_15_day_total_calories, 2),
                "all_15_day_total_protein_g": round(all_15_day_total_protein_g, 2),
                "all_15_day_total_fat_g": round(all_15_day_total_fat_g, 2),
                "all_15_day_total_carbs_g": round(all_15_day_total_carbs_g, 2),
                "complete_total_calories": round(complete_total_calories, 2),
                "complete_total_protein_g": round(complete_total_protein_g, 2),
                "complete_total_fat_g": round(complete_total_fat_g, 2),
                "complete_total_carbs_g": round(complete_total_carbs_g, 2),
            },
            "meal_plan_id": active_meal_plan.id,
            # "meal_plan_name": active_meal_plan.meal_plan_name if lean == "EN" else (
            #     active_meal_plan.meal_plan_name_spanish or active_meal_plan.meal_plan_name
            # ),
            "date": target_date,
            "daily_meal_completed": daily_meal.completed,
            "meal_slots": mealplan_data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    



class TodaysWorkoutPlanGet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get today's workout plan or specific date workout plan for the authenticated user.",
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
                description="Language code for translation (default is 'EN', supports 'ES')",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
        tags=['Single Date / Today Workout Plan']
    )
    def get(self, request):
        # Get query params
        date_str = request.query_params.get("date")
        lean = request.query_params.get("lean", "EN").upper()

        # Validate date
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response({"error": "Invalid date format, use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_date = date.today()

        # Get active workout plan for user
        active_workout_plan = WorkoutPlan.objects.filter(
            user=request.user,
            is_completed=False,
            is_cancelled=False,
            start_date__lte=target_date,
            end_date__gte=target_date
        ).first()

        if not active_workout_plan:
            return Response({"message": "No active workout plan found for this date."}, status=status.HTTP_404_NOT_FOUND)

        # Get daily workout for target date
        daily_workout = active_workout_plan.daily_workouts.filter(date=target_date).first()
        if not daily_workout:
            return Response({"message": "No daily workout found for this date."}, status=status.HTTP_404_NOT_FOUND)

        # Build workout entries data
        workout_entries = []
        total_workouts = daily_workout.workouts.count()
        total_completed = daily_workout.workouts.filter(completed=True).count()
        total_incompleted = total_workouts - total_completed

        for entry in daily_workout.workouts.all():
            if entry.workout:
                workout_name = entry.workout.workout_name if lean == "EN" else (entry.workout.workout_name_spanish or entry.workout.workout_name)
                exercise_type = entry.workout.exercise_type if lean == "EN" else (entry.workout.exercise_type_spanish or entry.workout.exercise_type)
            else:
                workout_name = None
                exercise_type = None

            workout_entries.append({
                "id": entry.id,
                "workout_id": entry.workout.id if entry.workout else None,
                "workout_name": workout_name,
                "exercise_type": exercise_type,
                "series": entry.series,
                "reps": entry.reps,
                "rest": entry.rest,
                "completed": entry.completed
            })

        response_data = {
            "workout_plan_id": active_workout_plan.id,
            "date": target_date,
            "daily_workout_completed": daily_workout.completed,
            "status": {
                "total_workouts": total_workouts,
                "total_completed_workouts": total_completed,
                "total_incompleted_workouts": total_incompleted
            },
            "workout_entries": workout_entries
        }

        return Response(response_data, status=status.HTTP_200_OK)





class UpdateTodayMealEntryStatus(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update completion status for a specific MealSlotEntry belonging to today's active meal plan.",
        manual_parameters=[
            openapi.Parameter(
                'meal_slot_entry_id',
                openapi.IN_PATH,
                description="ID of the MealSlotEntry to update.",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["completed"],
            properties={
                "completed": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="New completion status (true or false)."
                ),
            },
            example={
                "completed": True
            }
        ),
        responses={
            200: openapi.Response(
                description="Meal entry updated successfully",
                examples={
                    "application/json": {
                        "message": "Meal entry updated successfully.",
                        "meal_slot_entry_id": 12,
                        "completed": True
                    }
                },
            ),
            400: openapi.Response(description="Missing or invalid parameters"),
            404: openapi.Response(description="Meal entry or active plan not found"),
        },
        tags=["Meal plan update"],
    )
    def patch(self, request, meal_slot_entry_id, *args, **kwargs):
        user = request.user
        completed = request.data.get("completed")

        # ✅ Validate input
        if completed is None:
            return Response(
                {"error": "'completed' is required in the body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Get active meal plan
        active_plan = MealPlan.objects.filter(
            user=user, is_completed=False, is_cancelled=False
        ).first()

        if not active_plan:
            return Response(
                {"error": "No active meal plan found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        today_entry = MealSlotEntry.objects.filter(
            id=meal_slot_entry_id,
            meal_slot__daily_meal__meal_plan=active_plan,
        ).first()

        if not today_entry:
            return Response(
                {"error": "Meal entry not found for today."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ✅ Update completion
        today_entry.completed = bool(completed)
        today_entry.save()

        return Response(
            {
                "message": "Meal entry updated successfully.",
                "meal_slot_entry_id": today_entry.id,
                "completed": today_entry.completed,
            },
            status=status.HTTP_200_OK,
        )





class UpdateWorkoutEntryStatus(APIView):
    """
    API to update completion status of a specific WorkoutEntry
    belonging to the user's active workout plan.
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update completion status for a specific WorkoutEntry in the user's active workout plan.",
        manual_parameters=[
            openapi.Parameter(
                'workout_entry_id',
                openapi.IN_PATH,
                description="ID of the WorkoutEntry to update.",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["completed"],
            properties={
                "completed": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="New completion status (true or false)."
                ),
            },
            example={"completed": True}
        ),
        responses={
            200: openapi.Response(
                description="Workout entry updated successfully",
                examples={
                    "application/json": {
                        "message": "Workout entry updated successfully.",
                        "workout_entry_id": 15,
                        "completed": True
                    }
                },
            ),
            400: openapi.Response(description="Missing or invalid parameters"),
            404: openapi.Response(description="Workout entry or active plan not found"),
        },
        tags=["Workout Plan Update"],
    )
    def patch(self, request, workout_entry_id, *args, **kwargs):
        user = request.user
        completed = request.data.get("completed")

        # ✅ Validate input
        if completed is None:
            return Response(
                {"error": "'completed' is required in the body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Find user's active workout plan
        active_plan = WorkoutPlan.objects.filter(
            user=user, is_completed=False, is_cancelled=False
        ).first()

        if not active_plan:
            return Response(
                {"error": "No active workout plan found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ✅ Find WorkoutEntry belonging to this plan
        entry = WorkoutEntry.objects.filter(
            id=workout_entry_id,
            daily_workout__workout_plan=active_plan,
        ).first()

        if not entry:
            return Response(
                {"error": "Workout entry not found for your active plan."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ✅ Update completion
        entry.completed = bool(completed)
        entry.save()

        return Response(
            {
                "message": "Workout entry updated successfully.",
                "workout_entry_id": entry.id,
                "completed": entry.completed,
            },
            status=status.HTTP_200_OK,
        )
    
    

