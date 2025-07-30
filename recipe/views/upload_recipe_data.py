import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from recipe.decorators import validate_keys
from django.db import transaction
from datetime import timedelta
from recipe.models import Recipe, Instruction, Ingredient, CustomUser

def validate_column(column,mandatory_column):
    return list(column) != mandatory_column

# this api is used for inserting the data in db 
# only creator have access to it
# 3 files are uploaded and the headers are
# recipe_columns = ['title','description','prep_duration','cook_duration','thumbnail_image']
# ingredient_columns = ['recipe_name','ingredient_name','ingredient_image']
# instruction_columns = ['recipe_name','step_number','step']
@api_view(['POST'])
@validate_keys(['email','role'])
def upload_receipe_excel_file(request):
    data = request.data
    email = data['email']
    role = data['role'].lower()
    
    if role!='creator':
        return Response({'status': 'error', 'message': 'Only creator is allowed to upload data.'}, status=status.HTTP_400_BAD_REQUEST)

    user = CustomUser.objects.filter(email=email, role=role, is_active=True).first()
    if not user:
        return Response({'status': 'error', 'message': 'Invalid User.'}, status=status.HTTP_400_BAD_REQUEST)

    upload_recipe = request.FILES.get('recipe')
    upload_ingredient = request.FILES.get('ingredient')
    upload_instruction = request.FILES.get('instruction')
    
    with transaction.atomic():
        if not upload_recipe or not upload_ingredient or not upload_instruction:
            return Response({'error': 'Must upload all files.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not upload_recipe.name.endswith(('.xlsx', '.xls')) or not upload_ingredient.name.endswith(('.xlsx', '.xls')) or not upload_instruction.name.endswith(('.xlsx', '.xls')):
            return Response({'error': 'File must be an Excel file (.xlsx or .xls).'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            recipe = pd.read_excel(upload_recipe)
            ingredient = pd.read_excel(upload_ingredient)
            instruction = pd.read_excel(upload_instruction)
        except Exception as e:
            return Response({'status': 'error', 'message': 'One or all Excel files are invalid.', 'err': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        
        recipe_columns = recipe.columns.str.strip()
        ingredient_columns = ingredient.columns.str.strip()
        instruction_columns = instruction.columns.str.strip()

        mandatory_recipe_columns = ['title','description','prep_duration','cook_duration','thumbnail_image']
        mandatory_ingredient_columns = ['recipe_name','ingredient_name','ingredient_image']
        mandatory_instruction_columns = ['recipe_name','step_number','step']

        invalid_recipe_columns = validate_column(recipe_columns,mandatory_recipe_columns)
        invalid_ingredient_columns = validate_column(ingredient_columns,mandatory_ingredient_columns)
        invalid_instruction_columns = validate_column(instruction_columns,mandatory_instruction_columns)

        if invalid_recipe_columns:
            return Response({'status': 'error',
                            'message': f'Invalid columns in recipe file {invalid_recipe_columns}',
                            'expected_columns': mandatory_recipe_columns,
                            'received_columns': list(recipe_columns)},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if invalid_ingredient_columns:
            return Response({'status': 'error',
                            'message': f'Invalid columns in incredient file {invalid_ingredient_columns}',
                            'expected_columns': mandatory_ingredient_columns,
                            'received_columns': list(ingredient_columns)},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if invalid_instruction_columns:
            return Response({'status': 'error',
                            'message': f'Invalid columns in incredient file {invalid_instruction_columns}',
                            'expected_columns': mandatory_instruction_columns,
                            'received_columns': list(instruction_columns)},
                            status=status.HTTP_400_BAD_REQUEST)
        
        for _,row in recipe.iterrows():
            Recipe.objects.create(title=row['title'],
                                description=row['description'],
                                prep_duration=timedelta(minutes=int(row['prep_duration'])),
                                cook_duration=timedelta(minutes=int(row['cook_duration'])),
                                thumbnail=row['thumbnail_image'],
                                custom_user_id=user.id
                                )
        
        detail = dict(Recipe.objects.filter(is_active=True).values_list('title','id'))

        for _,row in instruction.iterrows():
            id = detail[row['recipe_name']]
            Instruction.objects.create(step=row['step'], step_number=row['step_number'], recipe_id=id)
        
        for _,row in ingredient.iterrows():
            id = detail[row['recipe_name']]
            Ingredient.objects.create(name=row['ingredient_name'], image=row['ingredient_image'], recipe_id=id)

        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)


        
        
