from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from recipe.models import Recipe, Instruction, Ingredient, CustomUser

# it will retrieve the recipe data only for the creator who created it
# only the creator has access to this api
@api_view(['GET'])
def view_recipe_data(request):
    user_email = request.GET.get('email')
    if not user_email:
        return Response({'status': 'error', 'message': 'User email param is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = CustomUser.objects.filter(email=user_email, role='creator', is_active=True).first()
    if not user:
        return Response({'status': 'error', 'message': 'Invalid User or User must be creator.'}, status=status.HTTP_400_BAD_REQUEST)

    recipe = Recipe.objects.filter(is_active=True)
    if not recipe:
        return Response({'status': 'error', 'message': 'No recipe found.'}, status=status.HTTP_400_BAD_REQUEST)
    
    d = {}
    for item in recipe:
        d[item.title] = item.id
    
    instruction = Instruction.objects.all()
    if not instruction.exists():
        return Response({'status': 'error', 'message': 'No instruction found.'}, status=status.HTTP_400_BAD_REQUEST)
    
    ingredient = Ingredient.objects.all()
    if not ingredient.exists():
        return Response({'status': 'error', 'message': 'No ingredient found.'}, status=status.HTTP_400_BAD_REQUEST)
    
    result = {}

    for recipe in recipe:
        recipe_key = recipe.title.lower().replace(" ", "")
        steps = list(instruction.filter(recipe=recipe).order_by('step_number').values_list('step', flat=True))
        ingredients_list = list(ingredient.filter(recipe=recipe).values_list('name', flat=True))

        result[recipe_key] = {
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "prep_duration": str(recipe.prep_duration),
            "cook_duration": str(recipe.cook_duration),
            "instruction": steps,
            "ingredients": ingredients_list
        }

    return Response({'status': 'success', 'data': result}, status=status.HTTP_200_OK)

