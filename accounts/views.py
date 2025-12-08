from django.shortcuts import render
from rest_framework import status
from .models import User,Profile
from .serializers import RegisterSerializer,UpdateProfileSerializer,CustomTokenObtainPairSerializer,ProfileFullSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .translations import translate_text
from rest_framework.exceptions import ValidationError
from .models import AISuggestData
from .service import AISuggestData_get
from datetime import datetime, timedelta




#$swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from django.views.decorators.csrf import csrf_exempt

#jwt
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

# Create your views here.



class RegisterApiView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        tags=["Authentication"],
        request_body=RegisterSerializer,
        responses={201: openapi.Response("User registered successfully")}
    )
    @csrf_exempt
    def post(self, request, *args, **kwargs):

        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "A user with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "name": user.profile.fullname if hasattr(user, "profile") else "",
            }
        }, status=status.HTTP_201_CREATED)




class LoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request,*args,**kwargs)
        except ValidationError as ve:
            return Response({"error": ve.detail}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e :
            return Response({"error": str(e)}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)




class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e :
            return Response({"error":str(e)} , status= status.HTTP_500_INTERNAL_SERVER_ERROR)




class ProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Partially update the logged-in user's profile and translate fields if needed.",
        request_body=UpdateProfileSerializer,
        responses={
            200: openapi.Response("Profile updated successfully"),
            400: "Bad Request",
            401: "Unauthorized",
        },
        tags=['Profile'],
        manual_parameters=[
            openapi.Parameter(
                'lean',
                openapi.IN_QUERY,
                description="Language code for translation (default is 'EN')",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
    )

    def patch(self, request, *args, **kwargs):
        user = request.user
        lean = request.query_params.get('lean', 'EN').upper()

        profile, _ = Profile.objects.get_or_create(user=user)

        # Fetch fields from request.data, fallback to current value
        image = request.data.get("image", profile.image)
        fullname = request.data.get("fullname", profile.fullname)
        date_of_birth = request.data.get("date_of_birth", profile.date_of_birth)
        weight = request.data.get("weight", profile.weight)
        height = request.data.get("height", profile.height)
        abdominal = request.data.get("abdominal", profile.abdominal)
        sacroiliac = request.data.get("sacroiliac", profile.sacroiliac)
        subscapularis = request.data.get("subscapularis", profile.subscapularis)
        triceps = request.data.get("triceps", profile.triceps)
        train_duration = request.data.get("train_duration", profile.train_duration)

        gender = request.data.get("gender", profile.gender)
        trainer = request.data.get("trainer", profile.trainer)
        fitness_goals = request.data.get("fitness_goals", profile.fitness_goals)
        injuries_discomfort = request.data.get("injuries_discomfort", profile.injuries_discomfort)
        dietary_preferences = request.data.get("dietary_preferences", profile.dietary_preferences)
        allergies = request.data.get("allergies", profile.allergies)
        medical_conditions = request.data.get("medical_conditions", profile.medical_conditions)

        profile_data ={}
        
        print("🤣🤣🤣🤣🤣🤣🤣🤣",lean)
        # Translate to Spanish if lean != EN
        if lean != 'EN':
            profile_data = {
            "image": image,
            "fullname": fullname,
            "date_of_birth": date_of_birth,
            "weight": weight,
            "height": height,
            "abdominal": abdominal,
            "sacroiliac": sacroiliac,
            "subscapularis": subscapularis,
            "triceps": triceps,
            "train_duration": train_duration,

            #english data 
            "gender": translate_text(gender, 'EN'),
            "trainer":translate_text(trainer, 'EN'),
            "fitness_goals": translate_text(fitness_goals, 'EN'),
            "injuries_discomfort": translate_text(injuries_discomfort, 'EN'),
            "dietary_preferences": translate_text(dietary_preferences, 'EN'),
            "allergies": translate_text(allergies, 'EN'),
            "medical_conditions": translate_text(medical_conditions, 'EN'),

            #english data 
            "gender_spanish": gender,
            "trainer_spanish": trainer,
            "fitness_goals_spanish": fitness_goals,
            "injuries_discomfort_spanish": injuries_discomfort,
            "dietary_preferences_spanish": dietary_preferences,
            "allergies_spanish": allergies,
            "medical_conditions_spanish": medical_conditions,
        }
            
        else:

            profile_data = {
            "image": image,
            "fullname": fullname,
            "date_of_birth": date_of_birth,
            "weight": weight,
            "height": height,
            "abdominal": abdominal,
            "sacroiliac": sacroiliac,
            "subscapularis": subscapularis,
            "triceps": triceps,
            "train_duration": train_duration,

            #english data 
            "gender": gender,
            "trainer":trainer,
            "fitness_goals": fitness_goals,
            "injuries_discomfort": injuries_discomfort,
            "dietary_preferences": dietary_preferences,
            "allergies": allergies,
            "medical_conditions": medical_conditions, 

            #english data 
            "gender_spanish": translate_text(gender, "ES"),
            "trainer_spanish":translate_text(trainer, "ES"),
            "fitness_goals_spanish": translate_text(fitness_goals, "ES"),
            "injuries_discomfort_spanish": translate_text(injuries_discomfort, "ES"),
            "dietary_preferences_spanish": translate_text(dietary_preferences, "ES"),
            "allergies_spanish": translate_text(allergies, "ES"),
            "medical_conditions_spanish":translate_text(medical_conditions, "ES"),
        }
            
        print(profile_data)
            
            
        serializer = UpdateProfileSerializer(profile, data=profile_data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            data = ProfileFullSerializer(profile).data
            result = {}

            if lean != 'EN':
                result = {
                    "image": data.get("image"),
                    "fullname": data.get("fullname"),
                    "date_of_birth": data.get("date_of_birth"),
                    "weight": data.get("weight"),
                    "height": data.get("height"),
                    "abdominal": data.get("abdominal"),
                    "sacroiliac": data.get("sacroiliac"),
                    "subscapularis": data.get("subscapularis"),
                    "triceps": data.get("triceps"),
                    "train_duration": data.get("train_duration"),
                    "gender": data.get("gender_spanish"),
                    "trainer": data.get("trainer_spanish"),
                    "fitness_goals": data.get("fitness_goals_spanish"),
                    "injuries_discomfort": data.get("injuries_discomfort_spanish"),
                    "dietary_preferences": data.get("dietary_preferences_spanish"),
                    "allergies": data.get("allergies_spanish"),
                    "medical_conditions": data.get("medical_conditions_spanish"),
                }
            else:
                result = {
                    "image": data.get("image"),
                    "fullname": data.get("fullname"),
                    "date_of_birth": data.get("date_of_birth"),
                    "weight": data.get("weight"),
                    "height": data.get("height"),
                    "abdominal": data.get("abdominal"),
                    "sacroiliac": data.get("sacroiliac"),
                    "subscapularis": data.get("subscapularis"),
                    "triceps": data.get("triceps"),
                    "train_duration": data.get("train_duration"),
                    "gender": data.get("gender"),
                    "trainer": data.get("trainer"),
                    "fitness_goals": data.get("fitness_goals"),
                    "injuries_discomfort": data.get("injuries_discomfort"),
                    "dietary_preferences": data.get("dietary_preferences"),
                    "allergies": data.get("allergies"),
                    "medical_conditions": data.get("medical_conditions"),
                }

            # ai_result = AISuggestData_get(
            #         date_of_birth = profile.date_of_birth,
            #         weight = profile.weight,
            #         height = profile.height,
            #         gender = profile.gender,
            #         trainer = profile.trainer,
            #         fitness_goals = profile.fitness_goals,
            #         injuries_discomfort = profile.injuries_discomfort,
            #         dietary_preferences = profile.dietary_preferences,
            #         allergies = profile.allergies,
            #         medical_conditions = profile.medical_conditions
            # )

            # # ai_result is a UserProfile model output (water_intake, sleep_hours, calorie_goal)

            # ais_data, _ = AISuggestData.objects.get_or_create(user=request.user)
            # ais_data.calorie_need_daily = ai_result.calorie_goal
            # ais_data.water_liter = ai_result.water_intake
            # ais_data.sleep_duration = timedelta(hours=float(ai_result.sleep_hours))
            # ais_data.save()
            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ProfileRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve the logged-in user's profile in English or Spanish.",
        responses={
            200: openapi.Response("Profile data retrieved successfully"),
            400: "Bad Request",
            401: "Unauthorized",
        },
        tags=['Profile'],
        manual_parameters=[
            openapi.Parameter(
                'lean',
                openapi.IN_QUERY,
                description="Language code for translation (EN or ES). Default: EN",
                type=openapi.TYPE_STRING,
                default='EN'
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        lean = request.query_params.get('lean', 'EN').upper()

        # Get or create profile
        profile, _ = Profile.objects.get_or_create(user=user)
        data = ProfileFullSerializer(profile).data

        # Prepare response data based on language
        if lean != 'EN':
            result = {
                "image": data.get("image"),
                "fullname": data.get("fullname"),
                "date_of_birth": data.get("date_of_birth"),
                "weight": data.get("weight"),
                "height": data.get("height"),
                "abdominal": data.get("abdominal"),
                "sacroiliac": data.get("sacroiliac"),
                "subscapularis": data.get("subscapularis"),
                "triceps": data.get("triceps"),
                "train_duration": data.get("train_duration"),

                # Spanish fields
                "gender": data.get("gender_spanish"),
                "trainer": data.get("trainer_spanish"),
                "fitness_goals": data.get("fitness_goals_spanish"),
                "injuries_discomfort": data.get("injuries_discomfort_spanish"),
                "dietary_preferences": data.get("dietary_preferences_spanish"),
                "allergies": data.get("allergies_spanish"),
                "medical_conditions": data.get("medical_conditions_spanish"),
            }
        else:
            result = {
                "image": data.get("image"),
                "fullname": data.get("fullname"),
                "date_of_birth": data.get("date_of_birth"),
                "weight": data.get("weight"),
                "height": data.get("height"),
                "abdominal": data.get("abdominal"),
                "sacroiliac": data.get("sacroiliac"),
                "subscapularis": data.get("subscapularis"),
                "triceps": data.get("triceps"),
                "train_duration": data.get("train_duration"),

                # English fields
                "gender": data.get("gender"),
                "trainer": data.get("trainer"),
                "fitness_goals": data.get("fitness_goals"),
                "injuries_discomfort": data.get("injuries_discomfort"),
                "dietary_preferences": data.get("dietary_preferences"),
                "allergies": data.get("allergies"),
                "medical_conditions": data.get("medical_conditions"),
            }

        return Response(result, status=status.HTTP_200_OK)
