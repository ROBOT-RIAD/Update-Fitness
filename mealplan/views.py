from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import UserMealFQA
from meal.models import Meal
from accounts.models import Profile
from accounts.translations import translate_text



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
                "user" : user.id,
                
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

                "user" : user.id,
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
        
        # fqa = UserMealFQA.objects.create(**fqadata)





        return Response(fqadata)

