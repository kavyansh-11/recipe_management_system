from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from recipe.models import Recipe, Instruction, Ingredient, CustomUser

# only intended creator has access to it
# it delete the data from 3 tables of db recipe, ingredient and instruction
@api_view(['DELETE'])
def delete_recipe(request, recipe_id, email, password):
    user = CustomUser.objects.filter(email=email, role='creator', is_active=True).first()
    if not user:
        return Response({'status': 'error', 'message': 'Invalid user.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.check_password(password):
        return Response({'status': 'error', 'message': 'Incorrect password.'}, status=status.HTTP_400_BAD_REQUEST)
    
    recipe = Recipe.objects.filter(id=recipe_id, custom_user_id=user.id).first()
    if not recipe:
        return Response({'status': 'error', 'message': 'Recipe not found or Invalid User.'}, status=status.HTTP_404_NOT_FOUND)
    
    Instruction.objects.filter(recipe=recipe).delete()
    Ingredient.objects.filter(recipe=recipe).delete()
    recipe.delete()
    
    return Response({'status': 'success', 'message': 'Recipe deleted successfully.'}, status=status.HTTP_200_OK)
