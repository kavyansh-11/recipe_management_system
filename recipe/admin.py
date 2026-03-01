from django.contrib import admin
from recipe.models import User, Recipe, Ingredient, Instruction

admin.site.register(User)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Instruction)
