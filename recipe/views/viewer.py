from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from recipe.models import Recipe, Instruction, Ingredient, CustomUser, Favourite
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse

# this file will contain all the APIs that are accessible only to the viewer

# this will return all the detail of recipe
@api_view(['GET'])
def list_recipes(request):
    email = request.GET.get('email')

    user = CustomUser.objects.filter(email=email, role='viewer', is_active=True).first()
    if not user:
        return Response({'status': 'error', 'message': 'Invalid User or User must be a viewer.'}, status=status.HTTP_400_BAD_REQUEST)

    recipes = Recipe.objects.filter(is_active=True)
    data = []

    for r in recipes:
        data.append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "prep_duration": str(r.prep_duration),
            "cook_duration": str(r.cook_duration)
        })
    return Response({"status": "success", "recipes": data}, status=status.HTTP_200_OK)


# returns a specific recipe based on the ID provided by the viewer
# includes the recipe details along with its instructions and ingredients
@api_view(['GET'])
def recipe_detail(request):
    email = request.GET.get('email')
    recipe_id = request.GET.get('recipe_id')

    user = CustomUser.objects.filter(email=email, role='viewer', is_active=True).first()
    if not user:
        return Response({'status': 'error', 'message': 'Invalid User or User must be a viewer.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        recipe = Recipe.objects.get(id=recipe_id, is_active=True)
    except Recipe.DoesNotExist:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)

    instructions = list(Instruction.objects.filter(recipe=recipe).order_by('step_number').values('step_number', 'step'))
    ingredients = list(Ingredient.objects.filter(recipe=recipe).values('name', 'image'))

    for ing in ingredients:
        ing['image'] = request.build_absolute_uri('/media/' + ing['image'])  # if using default media setup

    data = {
        "title": recipe.title,
        "description": recipe.description,
        "prep_duration": str(recipe.prep_duration),
        "cook_duration": str(recipe.cook_duration),
        "instructions": instructions,
        "ingredients": ingredients,
        "thumbnail": request.build_absolute_uri(recipe.thumbnail.url)
    }
    return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)


# this will mark the recipe as favourite based on ID provided by the viewer
@api_view(['POST'])
def mark_favourite(request):
    user_email = request.data.get('email')
    recipe_id = request.data.get('recipe_id')

    user = CustomUser.objects.filter(email=user_email, role='viewer', is_active=True).first()
    if not user:
        return Response({'status': 'error', 'message': 'Invalid User or User must be a viewer.'}, status=status.HTTP_400_BAD_REQUEST)

    recipe = Recipe.objects.filter(id=recipe_id, is_active=True).first()
    if not recipe:
        return Response({'error': 'Invalid recipe_id.'}, status=status.HTTP_400_BAD_REQUEST)
    
    check = Favourite.objects.filter(recipe_id=recipe.id, user_id=user.id, favourite=True)
    if check:
        return Response({'message': 'Already marked as favourite'}, status=status.HTTP_200_OK)

    Favourite.objects.create(recipe_id=recipe.id, user_id=user.id, favourite=True)
    
    return Response({'message': 'Marked as favourite'}, status=status.HTTP_201_CREATED)


# this will dounload the recipe in file based on the id provided by the viewer
@api_view(['GET'])
def download_recipe_pdf(request, recipe_id):
    try:
        recipe = Recipe.objects.get(id=recipe_id, is_active=True)
    except Recipe.DoesNotExist:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)

    instructions = Instruction.objects.filter(recipe=recipe).order_by('step_number')
    ingredients = Ingredient.objects.filter(recipe=recipe)

    html = render_to_string('recipe_pdf.html', {
        'recipe': recipe,
        'instructions': instructions,
        'ingredients': ingredients
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{recipe.title}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return Response({'error': 'PDF generation failed'}, status=500)
    
    return response

