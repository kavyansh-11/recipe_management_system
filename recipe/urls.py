from django.urls import path
from recipe.views import *

urlpatterns = [
    path('create_user/', CreateUser.as_view(), name='create-user'),
    path('login_view/', LoginView.as_view(), name='login-view'),

    # creator
    path('recipe/', Receipe.as_view(), name="recipe"),
    path('recipe/<int:recipe_id>/', Receipe.as_view(), name="recipe"),

    # viewer
    path('recipe_list/', RecipeList.as_view(), name="recipe-list"),
    path('recipe_detail/<int:recipe_id>/', RecipeDetail.as_view(), name="recipe_detail"),
    path('mark_favourite/<int:recipe_id>/', MarkFavorite.as_view(), name="mark_favourite"),
    # path('recipes/<int:recipe_id>/pdf/', viewer.download_recipe_pdf, name="download_recipe_pdf")

]
