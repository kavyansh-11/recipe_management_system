from datetime import datetime, time
import pandas as pd
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from recipe.serializers import CreateUserSerializer, LoginSerializer, RecipeDataSerializer, RecipeListSerializer, UploadReceipeSerializer
from recipe.models import Favourite, Ingredient, Instruction, Recipe, User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from recipe.permissions import *

def validate_column(column,mandatory_column):
    return list(column) != mandatory_column

class LoginView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(email=email, password=password)

        if not user or not user.is_active:
            return Response({'error': 'invalid user'}, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken.for_user(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }

        return Response({'data': data}, status=status.HTTP_200_OK)


class CreateUser(APIView):
    permission_classes = [IsSuperAdmin]
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response({'message': 'user created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)


class Receipe(APIView):
    permission_classes = [IsCreator]
    def post(self, request):
        serializer = UploadReceipeSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        user = validated_data['user']

        upload_recipe = validated_data['recipe']
        upload_ingredient = validated_data['ingredient']
        upload_instruction = validated_data['instruction']

        if not upload_recipe or not upload_ingredient or not upload_instruction:
            return Response({'error': 'Must upload all files.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not upload_recipe.name.endswith(('.xlsx', '.xls')) or not upload_ingredient.name.endswith(('.xlsx', '.xls')) or not upload_instruction.name.endswith(('.xlsx', '.xls')):
            return Response({'error': 'File must be an Excel file (.xlsx or .xls).'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():

            try:
                recipe = pd.read_excel(upload_recipe)
                ingredient = pd.read_excel(upload_ingredient)
                instruction = pd.read_excel(upload_instruction)
            except Exception as e:
                return Response(
                    {
                        'status': 'error',
                        'message': 'Invalid Excel file.',
                        'err': str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe_columns = recipe.columns.str.strip()
            ingredient_columns = ingredient.columns.str.strip()
            instruction_columns = instruction.columns.str.strip()

            mandatory_recipe_columns = [
                'title','description','prep_duration',
                'cook_duration'
            ]
            mandatory_ingredient_columns = [
                'recipe_name','ingredient_name','ingredient_image'
            ]
            mandatory_instruction_columns = [
                'recipe_name','step_number','step'
            ]

            invalid_recipe_columns = validate_column(
                recipe_columns, mandatory_recipe_columns
            )
            invalid_ingredient_columns = validate_column(
                ingredient_columns, mandatory_ingredient_columns
            )
            invalid_instruction_columns = validate_column(
                instruction_columns, mandatory_instruction_columns
            )

            if invalid_recipe_columns:
                return Response(
                    {'error': f'Invalid recipe columns {recipe_columns}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if invalid_ingredient_columns:
                return Response(
                    {'error': f'Invalid ingredient columns {ingredient_columns}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if invalid_instruction_columns:
                return Response(
                    {'error': f'Invalid instruction columns {instruction_columns}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # create recipes

            recipes_to_create = []

            for _, row in recipe.iterrows():
                recipes_to_create.append(
                    Recipe(
                        title=row['title'],
                        description=row['description'],
                        prep_duration=time(0, int(row['prep_duration'])),
                        cook_duration=time(0, int(row['cook_duration'])),
                        user=user
                    )
                )
            
            Recipe.objects.bulk_create(recipes_to_create)

            recipe_map = dict(
                Recipe.objects.filter(user=user)
                .values_list('title', 'id')
            )

            # create instructions

            instructions_to_create = []

            for _, row in instruction.iterrows():
                recipe_id = recipe_map[row['recipe_name']]
                instructions_to_create.append(
                    Instruction(
                        step=row['step'],
                        step_number=row['step_number'],
                        recipe_id=recipe_id
                    )
                )

            Instruction.objects.bulk_create(instructions_to_create)

            # create ingredients

            ingredients_to_create = []

            for _, row in ingredient.iterrows():
                recipe_id = recipe_map[row['recipe_name']]
                ingredients_to_create.append(
                    Ingredient(
                        name=row['ingredient_name'],
                        recipe_id=recipe_id
                    )
                )
            
            Ingredient.objects.bulk_create(ingredients_to_create)

        return Response(
            {'status': 'success'},
            status=status.HTTP_201_CREATED
        )
    
    def get(self, request):
        user = User.objects.filter(id=request.user.id, role='creator', is_active=True).first()
        if not user:
            return Response({'status': 'error', 'message': 'Invalid User or User must be creator.'}, status=status.HTTP_400_BAD_REQUEST)
        
        recipe = Recipe.objects.filter(user_id=user.id, is_active=True)
        if not recipe:
            return Response({'status': 'error', 'message': 'No recipe found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }

        serializer = RecipeDataSerializer(recipe, many=True)

        return Response({'data': data, 'recipe_data': serializer.data}, status=status.HTTP_200_OK)
    
    def put(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)

        user = User.objects.filter(id=request.user.id, role='creator', is_active=True).first()
        if not user:
            return Response({'status': 'error', 'message': 'Invalid user or user must be creator'}, status=status.HTTP_400_BAD_REQUEST)
        
        recipe = Recipe.objects.filter(id=recipe.id, user_id=user.id).first()
        if not recipe:
            return Response({'status': 'error', 'message': 'Recipe not found or recipe is not assiciated with user'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        with transaction.atomic():
            recipe.title = data['title']
            recipe.description = data['description']
            recipe.prep_duration = time(0, int(data['prep_duration']))
            recipe.cook_duration = time(0, int(data['cook_duration']))
            recipe.save()

            # delete old ingredients and instructions
            Ingredient.objects.filter(recipe=recipe).delete()
            Instruction.objects.filter(recipe=recipe).delete()

            # create ingredients
            for ing in data['ingredients']:
                Ingredient.objects.create(recipe=recipe, name=ing)

            # create instructions
            for inst in data['instructions']:
                Instruction.objects.create(
                    recipe=recipe,
                    step_number=inst['step_number'],
                    step=inst['description']
                )

        return Response({'status': 'success', 'message': 'Recipe modified successfully'}, status=status.HTTP_200_OK)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)

        user = User.objects.filter(id=request.user.id, role='creator', is_active=True).first()
        if not user:
            return Response({'status': 'error', 'message': 'Invalid user or user must be creator'}, status=status.HTTP_400_BAD_REQUEST)
        
        recipe = Recipe.objects.filter(id=recipe.id, user_id=user.id).first()
        if not recipe:
            return Response({'status': 'error', 'message': 'Recipe not found or recipe is not assiciated with user'}, status=status.HTTP_404_NOT_FOUND)
        
        Instruction.objects.filter(recipe=recipe).delete()
        Ingredient.objects.filter(recipe=recipe).delete()
        recipe.delete()
        
        return Response({'status': 'success', 'message': 'Recipe deleted successfully.'}, status=status.HTTP_200_OK)


class RecipeList(APIView):
    permission_classes = [IsViewer]
    def get(self, request):
        user_id = request.user.id

        user = User.objects.filter(id=user_id, role='viewer', is_active=True).first()
        if not user:
            return Response({'status': 'error', 'message': 'Invalid User or User must be a viewer.'}, status=status.HTTP_400_BAD_REQUEST)
        
        recipes = Recipe.objects.filter(is_active=True)

        serializer = RecipeListSerializer(recipes, many=True)

        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    

class RecipeDetail(APIView):
    permission_classes = [IsViewer]
    def get(self, request, recipe_id):
        user_id = request.user.id

        user = User.objects.filter(id=user_id, role='viewer', is_active=True).first()
        if not user:
            return Response({'status': 'error', 'message': 'Invalid User or User must be a viewer.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            recipe = Recipe.objects.get(id=recipe_id, is_active=True)
        except Recipe.DoesNotExist:
            return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RecipeDataSerializer(recipe)
        
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    

class MarkFavorite(APIView):
    permission_classes = [IsViewer]
    def post(self, request, recipe_id):
        user_id = request.user.id

        user = User.objects.filter(id=user_id, role='viewer', is_active=True).first()
        if not user:
            return Response({'status': 'error', 'message': 'Invalid User or User must be a viewer.'}, status=status.HTTP_400_BAD_REQUEST)
        
        stats = request.data.get('stats')
        if not isinstance(stats, bool):
            return Response({"error": "stats must be of bool type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            recipe = Recipe.objects.get(id=recipe_id, is_active=True)
        except Recipe.DoesNotExist:
            return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)
        
        recipe_data = Favourite.objects.filter(recipe_id=recipe.id, user_id=user.id).first()
        if not recipe_data:
            Favourite.objects.create(recipe_id=recipe.id, user_id=user.id, favourite=True)
        else:
            recipe_data.favourite = stats
            recipe_data.save()
        
        return Response({'message': 'Marked as favourite'}, status=status.HTTP_201_CREATED)
