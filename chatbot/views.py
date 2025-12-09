from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from mealplan.models import MealPlan,MealSlotEntry,UserMealFQA
from workoutplan.models import WorkoutPlan,WorkoutEntry,UserWorkoutFQA
from datetime import date
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from accounts.models import Profile



# from .service import chat



class FitnessChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Chat with AI Fitness Assistant",
        operation_description="Sends a user message to the AI Fitness assistant and returns a generated response.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["message"],
            properties={
                "message": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User's message to the AI assistant",
                    example="Create my 3-day high-protein meal plan"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Successful response from the AI assistant",
                examples={
                    "application/json": {
                        "thread_id": 1,
                        "user": "john_doe",
                        "response": "Here’s your 3-day high-protein meal plan..."
                    }
                },
            ),
            400: "Bad Request - Missing message field",
            401: "Unauthorized - Authentication required",
            500: "Server Error - Model not responding"
        },
        tags=["AI Fitness Chat"]
    )

    def post(self, request):
        user = request.user
        user_message = request.data.get("message")

        if not user_message:
            return Response({"error": "Message is required."}, status=400)
        

        result = get_meal_plan(user)


        # response = await chat(thread_id=user, user_message=user_message)

        # if not response:
        #     return Response({"error": "No response from model."}, status=500)

        return Response(result)
    





def get_meal_plan(user):
    """
    Returns the active or most recent completed meal plan with full nested data.
    """

    # 1️⃣ Try to get the active meal plan
    meal_plan = (
        MealPlan.objects
        .filter(
            user=user,
            is_completed=False,
            is_cancelled=False,
            start_date__lte=date.today(),
            end_date__gte=date.today()
        )
        .prefetch_related(
            'daily_meals__meal_slots__entries__meal'
        )
        .first()
    )

    # 2️⃣ If not found, get most recent completed
    if not meal_plan:
        meal_plan = (
            MealPlan.objects
            .filter(user=user, is_completed=True)
            .order_by('-end_date')
            .prefetch_related(
                'daily_meals__meal_slots__entries__meal'
            )
            .first()
        )

    if not meal_plan:
        return None

    # 3️⃣ Build nested data manually (to JSON-like dict)
    plan_data = {
        "id": meal_plan.id,
        "meal_plan_name": meal_plan.meal_plan_name,
        "meal_plan_name_spanish": meal_plan.meal_plan_name_spanish,
        "start_date": meal_plan.start_date,
        "end_date": meal_plan.end_date,
        "is_completed": meal_plan.is_completed,
        "is_cancelled": meal_plan.is_cancelled,
        "daily_meals": [],
    }

    for daily in meal_plan.daily_meals.all().order_by("date"):
        daily_data = {
            "id": daily.id,
            "date": daily.date,
            "completed": daily.completed,
            "meal_slots": [],
        }

        for slot in daily.meal_slots.all():
            slot_data = {
                "id": slot.id,
                "slot_type": slot.slot_type,
                "completed": slot.completed,
                "entries": [],
            }

            for entry in slot.entries.all():
                slot_data["entries"].append({
                    "id": entry.id,
                    "meal_name": entry.meal.food_name if entry.meal else None,
                    "grams": entry.grams,
                    "calories": entry.calories,
                    "protein_g": entry.protein_g,
                    "fat_g": entry.fat_g,
                    "carbs_g": entry.carbs_g,
                    "completed": entry.completed,
                })

            daily_data["meal_slots"].append(slot_data)

        plan_data["daily_meals"].append(daily_data)

    return plan_data
    



def get_workout_plan(user):
    """
    Returns the active or most recent completed workout plan with full nested data.
    """

    # 1️⃣ Try to get active workout plan
    workout_plan = (
        WorkoutPlan.objects
        .filter(
            user=user,
            is_completed=False,
            is_cancelled=False,
            start_date__lte=date.today(),
            end_date__gte=date.today()
        )
        .prefetch_related(
            'daily_workouts__workouts__workout'
        )
        .first()
    )

    # 2️⃣ If no active plan, get the most recent completed one
    if not workout_plan:
        workout_plan = (
            WorkoutPlan.objects
            .filter(user=user, is_completed=True)
            .order_by('-end_date')
            .prefetch_related(
                'daily_workouts__workouts__workout'
            )
            .first()
        )

    if not workout_plan:
        return None

    # 3️⃣ Build nested JSON-like structure
    plan_data = {
        "id": workout_plan.id,
        "workout_plan_name": workout_plan.workout_plan_name,
        "workout_plan_name_spanish": workout_plan.workout_plan_name_spanish,
        "start_date": workout_plan.start_date,
        "end_date": workout_plan.end_date,
        "is_completed": workout_plan.is_completed,
        "is_cancelled": workout_plan.is_cancelled,
        "daily_workouts": [],
    }

    for daily in workout_plan.daily_workouts.all().order_by("date"):
        daily_data = {
            "id": daily.id,
            "date": daily.date,
            "completed": daily.completed,
            "workouts": [],
        }

        for entry in daily.workouts.all():
            daily_data["workouts"].append({
                "id": entry.id,
                "workout_name": entry.workout.workout_name if entry.workout else None,
                "workout_exercise_type": entry.workout.exercise_type if entry.workout else None,
                "series": entry.series,
                "reps": entry.reps,
                "rest": entry.rest,
                "completed": entry.completed,
            })

        plan_data["daily_workouts"].append(daily_data)

    return plan_data




def get_profile_data(user):

    profile = user.profile

    profile_dat = {
        "fullname": profile.fullname,
        "date_of_birth": profile.date_of_birth,
        "weight": profile.weight,
        "height": profile.height,
        "abdominal": profile.abdominal,
        "sacroiliac": profile.sacroiliac,
        "subscapularis": profile.subscapularis,
        "triceps": profile.triceps,
        "gender": profile.gender,
        "trainer": profile.trainer,
        "fitness_goals": profile.fitness_goals,
        "injuries_discomfort": profile.injuries_discomfort,
        "dietary_preferences": profile.dietary_preferences,
        "allergies": profile.allergies,
        "medical_conditions": profile.medical_conditions,
    }

    active_meal_plan = user.meal_plans.filter(
        is_completed=False,
        is_cancelled=False,
        end_date__gte=date.today()
    ).first()


    if active_meal_plan:
        meal_fqa = active_meal_plan.fqa
        meal_fqa_data = {
            "activeness_level": meal_fqa.activeness_level,
            "event": meal_fqa.event,
            "doctor_clearance": meal_fqa.doctor_clearance,
            "training_environment": meal_fqa.training_environment,
            "preferences": meal_fqa.preferences,
            "skipped": meal_fqa.skipped,
            "profile_json": meal_fqa.profile_json,
        }
    else:
        meal_fqa_data = None


    active_workout_plan = user.workout_plans.filter(
        is_completed=False,
        is_cancelled=False,
        end_date__gte=date.today()
    ).first()


    if active_workout_plan:
        workout_fqa = active_workout_plan.fqa
        workout_fqa_data = {
            "session_duration": workout_fqa.session_duration,
            "days_per_week": workout_fqa.days_per_week,
            "training_environment": workout_fqa.training_environment,
            "equipments_access": workout_fqa.equipments_access,
            "training_style": workout_fqa.training_style,
            "activeness_level": workout_fqa.activeness_level,
            "motivation_factor": workout_fqa.motivation_factor,
            "event": workout_fqa.event,
            "recent_injuries": workout_fqa.recent_injuries,
            "fitness_level": workout_fqa.fitness_level,
            "doctor_clearance": workout_fqa.doctor_clearance,
            "profile_json": workout_fqa.profile_json,
        }
    else:
        workout_fqa_data = None

    return {
        'profile':profile_dat,
        "UserMealFQA": meal_fqa_data,
        'UserWorkoutFQA': workout_fqa_data,
    }




def bulk_update_meal_slot_entries(entries_data):

    """
    Update multiple MealSlotEntry objects.
    Input example:
    [
        {
            "id": 155,
            "grams": 140,
            "calories": 210,
            "protein_g": 12,
            "fat_g": 8,
            "carbs_g": 16,
            "completed": false
        }
    ]
    """

    allowed_fields = ["grams", "calories", "protein_g", "fat_g", "carbs_g", "completed"]

    for item in entries_data:
        entry_id = item.get("id")
        if not entry_id:
            continue

        try:
            entry = MealSlotEntry.objects.get(id=entry_id)
        except MealSlotEntry.DoesNotExist:
            continue

        for field in allowed_fields:
            if field in item:
                setattr(entry, field, item[field])

        entry.save()

    return {"message": "MealSlotEntry updated successfully"}




def bulk_update_workout_entries(entries_data):
    """
    Update multiple WorkoutEntry instances.
    
    Expected input:
    [
        {
            "id": 22,
            "series": 3,
            "reps": 12,
            "rest": 60,
            "completed": false
        }
    ]
    """

    allowed_fields = ["series", "reps", "rest", "completed"]

    for item in entries_data:
        entry_id = item.get("id")
        if not entry_id:
            continue

        try:
            entry = WorkoutEntry.objects.get(id=entry_id)
        except WorkoutEntry.DoesNotExist:
            continue

        for field in allowed_fields:
            if field in item:
                setattr(entry, field, item[field])
        entry.save()
    return {"message": "WorkoutEntry updated successfully"}





