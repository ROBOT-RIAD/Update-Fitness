from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from datetime import date,timedelta
from accounts.models import Profile
from .models import UserWorkoutFQA,WorkoutPlan,DailyWorkout,WorkoutEntry
from workout.models import Workout
from .serializers import UserWorkoutFQASerializer,WorkoutPlanSerializer
from accounts.models import Profile
from accounts.translations import translate_text
from workout.serializers import WorkoutSerializer
from .service import init_exercise

#$swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from django.views.decorators.csrf import csrf_exempt

# Create your views here.



class GenarateWorkoutPlan(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Create User FQA input and generate Workout Plan",
        manual_parameters=[
            openapi.Parameter('weight', openapi.IN_FORM, description="Weight in kg", type=openapi.TYPE_NUMBER, required=False),
            openapi.Parameter('height', openapi.IN_FORM, description="Height in cm", type=openapi.TYPE_NUMBER, required=False),
            openapi.Parameter('days_per_week', openapi.IN_FORM, description="Days per week", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('session_duration', openapi.IN_FORM, description="Session duration", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('injuries_discomfort', openapi.IN_FORM, description="Injuries or discomfort", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('allergies', openapi.IN_FORM, description="Allergies", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('medical_conditions', openapi.IN_FORM, description="Medical conditions", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('training_environment', openapi.IN_FORM, description="Training environment", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('equipments_access', openapi.IN_FORM, description="Available equipment", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('training_style', openapi.IN_FORM, description="Training style", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('activeness_level', openapi.IN_FORM, description="Activeness level", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('motivation_factor', openapi.IN_FORM, description="Motivation factor", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('event', openapi.IN_FORM, description="Event or goal", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('recent_injuries', openapi.IN_FORM, description="Recent injuries", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('fitness_level', openapi.IN_FORM, description="Fitness level", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('doctor_clearance', openapi.IN_FORM, description="Doctor's clearance", type=openapi.TYPE_STRING, required=False),

            # Query parameter for language
            openapi.Parameter(
                'lean',
                openapi.IN_QUERY,
                description="Language code for translation (default: EN)",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
        responses={
            200: openapi.Response("Workout Plan Create Successfully"),
            400: "Bad Request",
            401: "Unauthorized",
        },
        tags=['WorkoutPlan'],
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        lean = request.query_params.get('lean', 'EN').upper()

        active_plan = WorkoutPlan.objects.filter(
            user=user,
            is_completed=False,
            is_cancelled=False
        ).first()


        if active_plan:
            return Response({
                "error": "You already have an active workout plan.",
                "active_plan_id": active_plan.id,
                "start_date": active_plan.start_date,
                "end_date": active_plan.end_date,
                "workout_plan_name":  active_plan.workout_plan_name if lean == 'EN' else active_plan.workout_plan_name_spanish
            }, status=status.HTTP_400_BAD_REQUEST)
        

        profile, created = Profile.objects.get_or_create(user=user)
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
            "date_of_birth": profile.date_of_birth,
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
                "session_duration": data.get("session_duration"),
                "days_per_week": data.get("days_per_week"),
                "profile_json" : profile_json,

                #english
                "training_environment": translate_text(data.get("training_environment"),'EN'),
                "equipments_access": translate_text(data.get("equipments_access"),'EN'),
                "training_style": translate_text(data.get("training_style"),'EN'),
                "activeness_level": translate_text(data.get("activeness_level"),'EN'),
                "motivation_factor": translate_text(data.get("motivation_factor"),'EN'),
                "event": translate_text(data.get("event"),'EN'),
                "recent_injuries": translate_text(data.get("recent_injuries"),'EN'),
                "fitness_level": translate_text(data.get("fitness_level"),'EN'),
                "doctor_clearance": translate_text(data.get("doctor_clearance"),'EN'),


                #spanish
                "training_environment_spanish": data.get("training_environment"),
                "equipments_access_spanish": data.get("equipments_access"),
                "training_style_spanish": data.get("training_style"),
                "activeness_level_spanish": data.get("activeness_level"),
                "motivation_factor_spanish": data.get("motivation_factor"),
                "event_spanish": data.get("event"),
                "recent_injuries_spanish": data.get("recent_injuries"),
                "fitness_level_spanish": data.get("fitness_level"),
                "doctor_clearance_spanish": data.get("doctor_clearance"),

            }
        else:
            fqadata = {

                "user" : user,
                "session_duration": data.get("session_duration"),
                "days_per_week": data.get("days_per_week"),
                "profile_json" : profile_json,

                #english
                "training_environment": data.get("training_environment"),
                "equipments_access": data.get("equipments_access"),
                "training_style": data.get("training_style"),
                "activeness_level": data.get("activeness_level"),
                "motivation_factor": data.get("motivation_factor"),
                "event": data.get("event"),
                "recent_injuries": data.get("recent_injuries"),
                "fitness_level": data.get("fitness_level"),
                "doctor_clearance": data.get("doctor_clearance"),
                


                #spanish
                "training_environment_spanish": translate_text(data.get("training_environment"),'ES'),
                "equipments_access_spanish": translate_text(data.get("equipments_access"),'ES'),
                "training_style_spanish": translate_text(data.get("training_style"),'ES'),
                "activeness_level_spanish": translate_text(data.get("activeness_level"),'ES'),
                "motivation_factor_spanish": translate_text(data.get("motivation_factor"),'ES'),
                "event_spanish": translate_text(data.get("event"),'ES'),
                "recent_injuries_spanish": translate_text(data.get("recent_injuries"),'ES'),
                "fitness_level_spanish": translate_text(data.get("fitness_level"),'ES'),
                "doctor_clearance_spanish": translate_text(data.get("doctor_clearance"),'ES'),
            }

        
        fqa = UserWorkoutFQA.objects.create(**fqadata)

        start_date = date.today()
        end_date = start_date + timedelta(days=6)

        workoutplan = WorkoutPlan.objects.create(
            user=user,
            fqa=fqa,
            start_date=start_date,
            end_date=end_date,
            workout_plan_name="7 Days Workout Plan",
            workout_plan_name_spanish="7 días de entrenamiento"
        )

        workoutplan_data = WorkoutPlanSerializer(workoutplan).data

        all_workouts = Workout.objects.all()
        workouts_data = WorkoutSerializer(all_workouts, many=True).data


        fwq_data = UserWorkoutFQASerializer(fqa).data
        

        openaidata = {
            "fqa": fwq_data,
            "workoutplan": workoutplan_data,
            "workouts_data": workouts_data
        }


        DailyWorkout_WorkoutEntry = init_exercise(openaidata)

        daily_workouts = DailyWorkout_WorkoutEntry.get("daily_workouts", [])

        for day_data in daily_workouts:
            date_str = day_data.get("date")
            workout_entries = day_data.get("workouts", [])

            # Create the DailyWorkout
            daily_obj = DailyWorkout.objects.create(
                workout_plan=workoutplan,
                date=date_str,
                completed=False
            )

            # Create WorkoutEntry records for each exercise in that day
            for entry in workout_entries:
                workout_id = entry.get("workout")
                try:
                    workout_instance = Workout.objects.get(id=workout_id)
                except Workout.DoesNotExist:
                    continue 

                WorkoutEntry.objects.create(
                    daily_workout=daily_obj,
                    workout=workout_instance,
                    series=entry.get("series", 3),
                    reps=entry.get("reps", 10),
                    rest=entry.get("rest", 60),
                    completed=False
                )

        return Response({
            "message": "Workout plan created successfully",
        }, status=status.HTTP_201_CREATED)




