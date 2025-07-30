from django.urls import path
from recipe.views import create_user, upload_recipe_data, view_recipe_data, delete_recipe_data, modify_recipe_data, viewer

urlpatterns = [
    # creator
    path('create_user/', create_user.create_user, name='create_user'),
    path('upload_recipe_data/', upload_recipe_data.upload_receipe_excel_file, name="upload_receipe_excel_file"),
    path('view_recipe_data/', view_recipe_data.view_recipe_data, name="view_recipe_data"),
    path('delete_recipe/<int:recipe_id>/<str:email>/', delete_recipe_data.delete_recipe, name="delete_recipe"),
    path('modify_recipe/<int:recipe_id>/<str:email>/', modify_recipe_data.modify_recipe, name="modify_recipe"),

    # viewer
    path('all_recipe/', viewer.list_recipes, name="list_recipes"),
    path('recipe_detail/', viewer.recipe_detail, name="recipe_detail"),
    path('mark_favourite/', viewer.mark_favourite, name="mark_favourite"),
    path('recipes/<int:recipe_id>/pdf/', viewer.download_recipe_pdf, name="download_recipe_pdf")

]
