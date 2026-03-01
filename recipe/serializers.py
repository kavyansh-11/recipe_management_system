from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from recipe.models import Ingredient, Instruction, Recipe, User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["name", "email", "role", "password"]

    def validate_email(self, value):
        email_exists = User.objects.filter(email=value).exists()
        if email_exists:
            raise serializers.ValidationError("email already exist")
        return value
    
    def create(self, validated_data):
        # seperate out password from the above fields
        password = validated_data.pop('password')

        # creates new user but not saved it
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    # class Meta:
    #     model = User
    #     fields = ['email', 'password']


    # def validate(self, attrs):
    #     email = attrs.get('email')
    #     password = attrs.get('password')

    #     user = authenticate(email=email, password=password)

    #     if not user or not user.is_active:
    #         raise serializers.ValidationError("Invalid credentials")
        
    #     refresh = RefreshToken.for_user(user)

    #     return{
    #         'refresh': str(refresh),
    #         'access': str(refresh.access_token),
    #         'name': user.name,
    #         'email': user.email,
    #         'role': user.role
    #     }

class UploadReceipeSerializer(serializers.Serializer):
    recipe = serializers.FileField()
    ingredient = serializers.FileField()
    instruction = serializers.FileField()

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        if not user.is_authenticated:
            raise serializers.ValidationError('user not authenticated')
        
        roles = ['superadmin', 'creator']

        user = User.objects.filter(id=user.id, is_active=True).first()
        
        if user.role not in roles:
            return Response({"error": "role must be {roles}"}, status=status.HTTP_400_BAD_REQUEST)

        if not user:
            raise serializers.ValidationError("Invalid User.")

        data['user'] = user
        return data


class RecipeDataSerializer(serializers.ModelSerializer):
    ingredient = serializers.SerializerMethodField()
    instruction = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'prep_duration', 'cook_duration', 'is_active', 'ingredient', 'instruction']

    def get_ingredient(self, obj):
        if not obj:
            return None
        
        ingredient = Ingredient.objects.filter(recipe=obj.id)

        data = []
        for ingr in ingredient:
            data.append(ingr.name)
        
        return data
    
    def get_instruction(self, obj):
        if not obj:
            return None
        
        instruction = Instruction.objects.filter(recipe=obj.id)

        data = []
        for inst in instruction:
            data.append({
                'step_number': inst.step_number,
                'step': inst.step
            })
        
        return data
        

class RecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'



