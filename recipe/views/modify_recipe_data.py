from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from recipe.models import Recipe, Ingredient, Instruction, CustomUser
from django.db import transaction
from datetime import timedelta

# this will update the recipe, instruction and instruction
@api_view(['PUT'])
def modify_recipe(request, recipe_id, email, password):
    user = CustomUser.objects.filter(email=email, role='creator', is_active=True).first()
    if not user:
        return Response({'status': 'error', 'message': 'Invalid creator.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.check_password(password):
        return Response({'status': 'error', 'message': 'Incorrect password.'}, status=status.HTTP_400_BAD_REQUEST)

    recipe = Recipe.objects.filter(id=recipe_id, custom_user=user).first()
    if not recipe:
        return Response({'status': 'error', 'message': 'Recipe not found or not created by this user.'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    try:
        with transaction.atomic():
            recipe.title = data['title']
            recipe.description = data['description']
            recipe.prep_duration = timedelta(minutes=int(data['prep_duration']))
            recipe.cook_duration = timedelta(minutes=int(data['cooking_time']))
            recipe.save()

            # delete old ingredients and instructions
            Ingredient.objects.filter(recipe=recipe).delete()
            Instruction.objects.filter(recipe=recipe).delete()

            # create ingredients
            for ing in data['ingredients']:
                Ingredient.objects.create(recipe=recipe, name=ing['name'], image=None)

            # create instructions
            for inst in data['instructions']:
                Instruction.objects.create(
                    recipe=recipe,
                    step_number=inst['step_number'],
                    step=inst['description']
                )

        return Response({'status': 'success', 'message': 'Recipe modified successfully'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
