from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Meal
from .serializers import MealCreateAndUpdateSerializer, MealSerializer
from accounts.permissions import IsAdminRole
from accounts.translations import translate_text


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
            openapi.Parameter('subcategory',openapi.IN_FORM ,type = openapi.TYPE_STRING,description='subcategory'),
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
            data['subcategory_spanish'] = data.get('subcategory')
            data['food_name_spanish'] = data.get('food_name')

            data['category'] = translate_text(data.get('category'),'EN')
            data['subcategory'] = translate_text(data.get('subcategory'),'EN')
            data['food_name'] = translate_text(data.get('food_name'),'EN')
        else:
            data['category'] = data.get('category')
            data['subcategory'] = data.get('subcategory')
            data['food_name'] = data.get('food_name')

            data['category_spanish'] = translate_text(data.get('category'),'ES')
            data['subcategory_spanish'] = translate_text(data.get('subcategory'),'ES')
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
                    'subcategory'  : data['subcategory_spanish'],
                    'food_name' : data['food_name_spanish'],
                    "image": data['image'],
                }
            else:
                result ={
                    "id" : data['id'],
                    'category' : data['category'],
                    'subcategory'  : data['subcategory'],
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
            openapi.Parameter('subcategory', openapi.IN_FORM, type=openapi.TYPE_STRING, description='subcategory'),
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
            if 'subcategory' in data:
                data['subcategory_spanish'] = data.get('subcategory')
                data['subcategory'] = translate_text(data.get('subcategory'), 'EN')
            if 'food_name' in data:
                data['food_name_spanish'] = data.get('food_name')
                data['food_name'] = translate_text(data.get('food_name'), 'EN')
        else:
            if 'category' in data:
                data['category_spanish'] = translate_text(data.get('category'), 'ES')
            if 'subcategory' in data:
                data['subcategory_spanish'] = translate_text(data.get('subcategory'), 'ES')
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
                    'subcategory'  : data['subcategory_spanish'],
                    'food_name' : data['food_name_spanish'],
                    "image": data['image'],
                }
            else:
                result ={
                    "id" : data['id'],
                    'category' : data['category'],
                    'subcategory'  : data['subcategory'],
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
                    'subcategory': item['subcategory_spanish'],
                    'food_name': item['food_name_spanish'],
                    "image": item['image'],
                })
            else:
                result.append({
                    "id": item['id'],
                    'category': item['category'],
                    'subcategory': item['subcategory'],
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
                'subcategory': data['subcategory_spanish'],
                'food_name': data['food_name_spanish'],
                "image": data['image'],
            }
        else:
            result = {
                "id": data['id'],
                'category': data['category'],
                'subcategory': data['subcategory'],
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



