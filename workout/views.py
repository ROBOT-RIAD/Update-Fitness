from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Workout
from .serializers import WorkoutCreateAndUpdateSerializer,WorkoutSerializer
from accounts.permissions import IsAdminRole
from accounts.translations import translate_text
from django.db import IntegrityError
import json
# Create your views here.


#$swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser



class AdminWorkoutCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    parser_classes = (MultiPartParser, FormParser)
   
    @swagger_auto_schema(
        operation_description="Create a new workout (Admin only)",
        consumes=["multipart/form-data"],  # ✅ needed for file upload
        manual_parameters=[
            openapi.Parameter('code', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Unique workout code'),
            openapi.Parameter('exercise_type', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Type of exercise'),
            openapi.Parameter('workout_name', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Workout name'),
            openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Workout image'),
            openapi.Parameter('video', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Workout video'),
            openapi.Parameter('lean', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Language code (default: EN)", default='EN'),
        ],
        tags=['Admin Workout']
    )
    def post(self, request, *args, **kwargs):

        lean = request.query_params.get('lean', 'EN').upper()
        data = request.data.copy()

        if lean != 'EN':
            data['exercise_type_spanish'] = data.get('exercise_type', '')
            data['workout_name_spanish'] = data.get('workout_name', '')
            data['exercise_type'] = translate_text(data.get('exercise_type', ''), 'EN')
            data['workout_name'] = translate_text(data.get('workout_name', ''), 'EN')
        else:
            data['exercise_type'] = data.get('exercise_type', '')
            data['workout_name'] = data.get('workout_name', '')
            data['exercise_type_spanish'] = translate_text(data.get('exercise_type', ''), 'ES')
            data['workout_name_spanish'] = translate_text(data.get('workout_name', ''), 'ES')

        
        serializer = WorkoutCreateAndUpdateSerializer(data=data)

        if serializer.is_valid():
            try:
                workout_instance = serializer.save()
                data = WorkoutSerializer(workout_instance, context={'request': request}).data
                result = {}
                if lean != 'EN':
                    result ={
                        "id" : data['id'],
                        "code":data['code'],
                        "exercise_type" : data['exercise_type_spanish'],
                        "workout_name" : data['workout_name_spanish'],
                        "image": data['image'],
                        "video": data['video']
                    }
                else :
                    result ={
                        "id" : data['id'],
                        "code":data['code'],
                        "exercise_type" : data['exercise_type'],
                        "workout_name" : data['workout_name'],
                        "image": data['image'],
                        "video": data['video']
                    }

                return Response(result, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {"error": "Workout code already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class AdminWorkoutUpdateAPIView(APIView):
    """
    Update an existing workout (Admin only) via PUT or PATCH
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="Update an existing workout (Admin only)",
        consumes=["multipart/form-data"],
        manual_parameters=[
            openapi.Parameter('lean', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Language code (default: EN)", default='EN'),
            openapi.Parameter('code', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Unique workout code'),
            openapi.Parameter('exercise_type', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Type of exercise'),
            openapi.Parameter('workout_name', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Workout name'),
            openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Workout image'),
            openapi.Parameter('video', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Workout video'),
        ],
        tags=['Admin Workout']
    )
    def patch(self, request, pk, *args, **kwargs):
        lean = request.query_params.get('lean', 'EN').upper()
        data = request.data.copy()

        try:
            workout = Workout.objects.get(pk=pk)
        except Workout.DoesNotExist:
            return Response({"error": "Workout not found."}, status=status.HTTP_404_NOT_FOUND)

        # Handle translations
        if lean != 'EN':
            data['exercise_type_spanish'] = data.get('exercise_type', workout.exercise_type_spanish)
            data['workout_name_spanish'] = data.get('workout_name', workout.workout_name_spanish)
            data['exercise_type'] = translate_text(data.get('exercise_type', ''), 'EN') if 'exercise_type' in data else workout.exercise_type
            data['workout_name'] = translate_text(data.get('workout_name', ''), 'EN') if 'workout_name' in data else workout.workout_name
        else:
            data['exercise_type'] = data.get('exercise_type', workout.exercise_type)
            data['workout_name'] = data.get('workout_name', workout.workout_name)
            data['exercise_type_spanish'] = translate_text(data.get('exercise_type', ''), 'ES') if 'exercise_type' in data else workout.exercise_type_spanish
            data['workout_name_spanish'] = translate_text(data.get('workout_name', ''), 'ES') if 'workout_name' in data else workout.workout_name_spanish

        serializer = WorkoutCreateAndUpdateSerializer(workout, data=data, partial=True)

        if serializer.is_valid():
            try:
                workout_instance = serializer.save()
                data = WorkoutSerializer(workout_instance, context={'request': request}).data
                result = {}
                if lean != 'EN':
                    result ={
                        "id" : data['id'],
                        "code":data['code'],
                        "exercise_type" : data['exercise_type_spanish'],
                        "workout_name" : data['workout_name_spanish'],
                        "image": data['image'],
                        "video": data['video']
                    }
                else :
                    result ={
                        "id" : data['id'],
                        "code":data['code'],
                        "exercise_type" : data['exercise_type'],
                        "workout_name" : data['workout_name'],
                        "image": data['image'],
                        "video": data['video']
                    }

                return Response(result, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({"error": "Workout code already exists."}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AdminWorkoutListAPIView(APIView):
    """
    List all workouts (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    @swagger_auto_schema(
        operation_description="Get all workouts (Admin only)",
        manual_parameters=[
            openapi.Parameter('lean', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Language code (default: EN)", default='EN'),
        ],
        responses={200: WorkoutSerializer(many=True)},
        tags=['Admin Workout']
    )
    def get(self, request, *args, **kwargs):
        lean = request.query_params.get('lean', 'EN').upper()
        workouts = Workout.objects.all()
        serializer = WorkoutSerializer(workouts, many=True, context={'request': request})
        data = serializer.data
        result_list = []
        for w in data:
            if lean != 'EN':
                result_list.append({
                    "id": w['id'],
                    "code": w['code'],
                    "exercise_type": w['exercise_type_spanish'],
                    "workout_name": w['workout_name_spanish'],
                    "image": w['image'],
                    "video": w['video'],
                    "created_at": w['created_at'],
                    "updated_at": w['updated_at'],
                })
            else:
                result_list.append({
                    "id": w['id'],
                    "code": w['code'],
                    "exercise_type": w['exercise_type'],
                    "workout_name": w['workout_name'],
                    "image": w['image'],
                    "video": w['video'],
                    "created_at": w['created_at'],
                    "updated_at": w['updated_at'],
                })

        return Response(result_list, status=status.HTTP_200_OK)
    


class AdminWorkoutRetrieveAPIView(APIView):
    """
    Retrieve a single workout by ID (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    @swagger_auto_schema(
        operation_description="Retrieve a single workout by ID (Admin only)",
        manual_parameters=[
            openapi.Parameter('lean', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Language code (default: EN)", default='EN'),
        ],
        responses={200: WorkoutSerializer()},
        tags=['Admin Workout']
    )
    def get(self, request, pk, *args, **kwargs):
        lean = request.query_params.get('lean', 'EN').upper()

        try:
            workout = Workout.objects.get(pk=pk)
        except Workout.DoesNotExist:
            return Response({"error": "Workout not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WorkoutSerializer(workout, context={'request': request})
        w = serializer.data


        if lean != 'EN':
            result = {
                "id": w['id'],
                "code": w['code'],
                "exercise_type": w['exercise_type_spanish'],
                "workout_name": w['workout_name_spanish'],
                "image": w['image'],
                "video": w['video'],
                "created_at": w['created_at'],
                "updated_at": w['updated_at'],
            }
        else:
            result = {
                "id": w['id'],
                "code": w['code'],
                "exercise_type": w['exercise_type'],
                "workout_name": w['workout_name'],
                "image": w['image'],
                "video": w['video'],
                "created_at": w['created_at'],
                "updated_at": w['updated_at'],
            }

        return Response(result, status=status.HTTP_200_OK)




class AdminWorkoutDeleteAPIView(APIView):
    """
    Delete a workout by ID (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    @swagger_auto_schema(
        operation_description="Delete a workout by ID (Admin only)",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Workout ID'),
        ],
        tags=['Admin Workout']
    )
    def delete(self, request, pk, *args, **kwargs):
        try:
            workout = Workout.objects.get(pk=pk)
        except Workout.DoesNotExist:
            return Response({"error": "Workout not found."}, status=status.HTTP_404_NOT_FOUND)

        workout.delete()
        return Response({"detail": "Workout deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    



class AdminWorkoutBulkUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="""Bulk upload Workouts Via json file (Admin only)
        Example JSON:
        [
            {"code": "PEC1", "name": "PRESS BANCA", "exercise_type": "chest"},
            {"code": "PEC2", "name": "PRESS PLANO EN MÁQUINA", "exercise_type": "chest"}
        ]   
        """,
        manual_parameters=[
            openapi.Parameter('file',openapi.IN_FORM , type = openapi.TYPE_FILE,description='JSON file containing workout data'),
            openapi.Parameter('lean', openapi.IN_QUERY , type=openapi.TYPE_STRING,description="Language code (default: EN)", default='EN'),
        ],
        tags=['Admin Workout'],
    )

    def post(self , request ,*args, **kwargs):
        lean = request.query_params.get('lean').upper()
        uploadfile = request.FILES.get('file')

        if not uploadfile:
            return Response({"error" : "Please upload a JSON file"}, status= status.HTTP_400_BAD_REQUEST)
        
        try:
            data = json.load(uploadfile)
        except json.JSONDecodeError:
            return Response({"error" : "Invalid json file"} , status= status.HTTP_400_BAD_REQUEST)
        

        created_workouts = []
        errors = []

        for item in data:
            try:
                code = item.get('code')
                workout_name = item.get('name')
                exercise_type = item.get('exercise_type')

                if not code or not workout_name or not exercise_type:
                    errors.append({"code": code, "error" : "missing required fileds"})
                    continue


                workout_data = {
                    "code" : code,
                    "workout_name" : workout_name,
                    "exercise_type" : exercise_type
                }

                if lean != 'EN':
                    workout_data['exercise_type_spanish'] = exercise_type
                    workout_data['workout_name_spanish'] = workout_name
                    workout_data['exercise_type'] = translate_text(exercise_type, 'EN')
                    workout_data['workout_name'] = translate_text(workout_name, 'EN')
                else:
                    workout_data['exercise_type_spanish'] = translate_text(exercise_type, 'ES')
                    workout_data['workout_name_spanish'] = translate_text(workout_name, 'ES')

                print(workout_data)

                serializer = WorkoutCreateAndUpdateSerializer(data=workout_data)

                if serializer.is_valid():
                    workout_instance = serializer.save()
                    created_workouts.append(WorkoutSerializer(workout_instance, context={'request': request}).data)
                else:
                    errors.append({"code": code, "error": serializer.errors})

            except IntegrityError:
                errors.append({"code": item.get("code"), "error": "Workout code already exists."})
            except Exception as e:
                errors.append({"code": item.get("code"), "error": str(e)})
                
        return Response({"created_count": len(created_workouts),"error_count": len(errors),"created_workouts": created_workouts,"errors": errors,}, status=status.HTTP_201_CREATED)




