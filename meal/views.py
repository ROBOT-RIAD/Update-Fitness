from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Meal
from .serializers import MealCreateAndUpdateSerializer, MealSerializer
from accounts.permissions import IsAdminRole
from accounts.translations import translate_text
from django.db import IntegrityError
import json


# Create your views here.


#swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser,FormParser




class AdminMealcreateApiview(APIView):
    permission_classes =[permissions.IsAuthenticated]
    parser_classes = (MultiPartParser , FormParser)

    @swagger_auto_schema(
        operation_description="Create a new Meal (Admin only create)",
        manual_parameters=[
            openapi.Parameter('category',openapi.IN_FORM ,type = openapi.TYPE_STRING,description='category'),
            openapi.Parameter('food_name',openapi.IN_FORM ,type = openapi.TYPE_STRING,description='food_name'),
            openapi.Parameter('lean', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Language code (default: EN)", default='EN'),
        ],
        tags=['Admin Meal']
    )
    def post(self , request ,*args, **kwargs):
        lean = request.query_params.get('lean', 'EN').upper()
        data = request.data.copy()
        
        if lean != 'EN' :
            data['category_spanish'] = data.get('category')
            data['food_name_spanish'] = data.get('food_name')

            data['category'] = translate_text(data.get('category'),'EN')
            data['food_name'] = translate_text(data.get('food_name'),'EN')
        else:
            data['category'] = data.get('category')
            data['food_name'] = data.get('food_name')

            data['category_spanish'] = translate_text(data.get('category'),'ES')
            data['food_name_spanish'] = translate_text(data.get('food_name'),'ES')

        
        serializer = MealCreateAndUpdateSerializer(data = data)

        if serializer.is_valid():
            meal_instance = serializer.save()
            data = MealSerializer(meal_instance,context={'request': request}).data
            result ={}
            if lean != 'EN':
                result ={
                    "id" : data['id'],
                    'category' : data['category_spanish'],
                    'food_name' : data['food_name_spanish'],
                    "image": data['image'],
                }
            else:
                result ={
                    "id" : data['id'],
                    'category' : data['category'],
                    'food_name' : data['food_name'],
                    "image": data['image'],
                }

            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class AdminMealUpdateApiview(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser , FormParser)

    @swagger_auto_schema(
        operation_description="Update an existing Meal (Admin only)",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Meal ID'),
            openapi.Parameter('category', openapi.IN_FORM, type=openapi.TYPE_STRING, description='category'),
            openapi.Parameter('food_name', openapi.IN_FORM, type=openapi.TYPE_STRING, description='food_name'),
            openapi.Parameter('lean', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Language code (default: EN)", default='EN'),
        ],
        tags=['Admin Meal']
    )
    def patch(self , request , pk ,*args, **kwargs):

        lean = request.query_params.get('lean', 'EN').upper()
        data = request.data.copy()

        try:
            meal_instance = Meal.objects.get(id=pk)
        except Meal.DoesNotExist:
            return Response({"detail": "Meal not found."}, status=status.HTTP_404_NOT_FOUND)


        if lean != 'EN':
            if 'category' in data:
                data['category_spanish'] = data.get('category')
                data['category'] = translate_text(data.get('category'), 'EN')
            if 'food_name' in data:
                data['food_name_spanish'] = data.get('food_name')
                data['food_name'] = translate_text(data.get('food_name'), 'EN')
        else:
            if 'category' in data:
                data['category_spanish'] = translate_text(data.get('category'), 'ES')
            if 'food_name' in data:
                data['food_name_spanish'] = translate_text(data.get('food_name'), 'ES')

        serializer = MealCreateAndUpdateSerializer(meal_instance, data=data, partial=True)

        if serializer.is_valid():
            meal_instance = serializer.save()
            data = MealSerializer(meal_instance,context={'request': request}).data
            result ={}
            if lean != 'EN':
                result ={
                    "id" : data['id'],
                    'category' : data['category_spanish'],
                    'food_name' : data['food_name_spanish'],
                    "image": data['image'],
                }
            else:
                result ={
                    "id" : data['id'],
                    'category' : data['category'],
                    'food_name' : data['food_name'],
                    "image": data['image'],
                }

            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class AdminMealListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all Meals (Admin only)",
        manual_parameters=[
            openapi.Parameter('lean', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Language code (default: EN)", default='EN'),
        ],
        tags=['Admin Meal']
    )
    def get(self, request, *args, **kwargs):
        lean = request.query_params.get('lean', 'EN').upper()
        meals = Meal.objects.all()
        serializer = MealSerializer(meals, many=True, context={'request': request})
        data = serializer.data
        result = []

        for item in data:
            if lean != 'EN':
                result.append({
                    "id": item['id'],
                    'category': item['category_spanish'],
                    'food_name': item['food_name_spanish'],
                    "image": item['image'],
                })
            else:
                result.append({
                    "id": item['id'],
                    'category': item['category'],
                    'food_name': item['food_name'],
                    "image": item['image'],
                })

        return Response(result, status=status.HTTP_200_OK)
    



class AdminMealRetrieveAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a Meal by ID (Admin only)",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Meal ID'),
            openapi.Parameter('lean', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Language code (default: EN)", default='EN'),
        ],
        tags=['Admin Meal']
    )
    def get(self, request, pk, *args, **kwargs):
        lean = request.query_params.get('lean', 'EN').upper()
        try:
            meal_instance = Meal.objects.get(id=pk)
        except Meal.DoesNotExist:
            return Response({"detail": "Meal not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MealSerializer(meal_instance, context={'request': request})
        data = serializer.data
        result = {}

        if lean != 'EN':
            result = {
                "id": data['id'],
                'category': data['category_spanish'],
                'food_name': data['food_name_spanish'],
                "image": data['image'],
            }
        else:
            result = {
                "id": data['id'],
                'category': data['category'],
                'food_name': data['food_name'],
                "image": data['image'],
            }

        return Response(result, status=status.HTTP_200_OK)
    



class AdminMealDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Delete a Meal by ID (Admin only)",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Meal ID'),
        ],
        tags=['Admin Meal']
    )
    def delete(self, request, pk, *args, **kwargs):
        try:
            meal_instance = Meal.objects.get(id=pk)
        except Meal.DoesNotExist:
            return Response({"detail": "Meal not found."}, status=status.HTTP_404_NOT_FOUND)

        meal_instance.delete()
        return Response({"detail": "Meal deleted successfully."}, status=status.HTTP_204_NO_CONTENT)




class AdminMealBulkUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="""
        Bulk upload Meals via JSON file (Admin only)
        Example JSON:
        [
            {"food": "PRESS BANCA", "category": "Protein"},
            {"food": "PRESS PLANO EN MÁQUINA", "category": "Chest"}
        ]
        """,
        manual_parameters=[
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description='JSON file containing Meal data'
            ),
            openapi.Parameter(
                'lean',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Language code (default: EN)",
                default='EN'
            ),
        ],
        tags=['Admin Meal'],
    )
    def post(self, request, *args, **kwargs):
        # Get language and file
        lean = request.query_params.get('lean', 'EN').upper()
        uploadfile = request.FILES.get('file')

        if not uploadfile:
            return Response({"error": "Please upload a JSON file"}, status=status.HTTP_400_BAD_REQUEST)

        # Parse uploaded JSON
        try:
            data = json.loads(uploadfile.read().decode('utf-8'))
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON file"}, status=status.HTTP_400_BAD_REQUEST)

        created_meals = []
        errors = []

        for item in data:
            try:
                food_name = item.get('food')
                category = item.get('category')

                if not food_name or not category:
                    errors.append({"item": item, "error": "Missing required fields"})
                    continue

                # Prepare meal data
                meal_data = {
                    'food_name': food_name,
                    'category': category,
                }

                # Handle translation
                if lean != 'EN':
                    meal_data['category_spanish'] = category
                    meal_data['food_name_spanish'] = food_name
                    meal_data['category'] = translate_text(category, 'EN')
                    meal_data['food_name'] = translate_text(food_name, 'EN')
                else:
                    meal_data['category_spanish'] = translate_text(category, 'ES')
                    meal_data['food_name_spanish'] = translate_text(food_name, 'ES')

                # Serialize and save
                serializer = MealCreateAndUpdateSerializer(data=meal_data)
                if serializer.is_valid():
                    meal_instance = serializer.save()
                    created_meals.append(meal_instance)
                else:
                    errors.append(serializer.errors)

            except IntegrityError:
                errors.append({"food": item.get("food"), "error": "Meal already exists."})
            except Exception as e:
                errors.append({"food": item.get("food"), "error": str(e)})

        # Serialize created meal instances for JSON response
        created_data = MealCreateAndUpdateSerializer(created_meals, many=True).data

        return Response({
            "created_count": len(created_meals),
            "error_count": len(errors),
            "created_meals": created_data,
            "errors": errors,
        }, status=status.HTTP_201_CREATED)


