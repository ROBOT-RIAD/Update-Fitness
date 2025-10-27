from rest_framework import serializers
from .models import User,Profile
from .constants import GENDER


# jwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer




class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required= True)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'password']
    
    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
        )
        Profile.objects.create(user=user)
        return user
    



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        data = super().validate({'email': user.email, 'password': password})

        # Add user info to response
        data['user'] = {
            'id' : user.id,
            'email': user.email,
            'role': user.role,
            'name': user.profile.fullname if hasattr(user, 'profile') else '',
        }

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['id'] = user.id
        token['email'] = user.email
        token['role'] = user.role
        return token
    



class ProfileFullSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id','user_id', 'user_email', 'image', 'fullname', 'date_of_birth', 'weight', 'height',
            'abdominal', 'sacroiliac', 'subscapularis', 'triceps', 'train_duration',
            'gender', 'trainer', 'fitness_goals', 'injuries_discomfort',
            'dietary_preferences', 'allergies', 'medical_conditions',
            'gender_spanish', 'trainer_spanish', 'fitness_goals_spanish', 'injuries_discomfort_spanish',
            'dietary_preferences_spanish', 'allergies_spanish', 'medical_conditions_spanish',
            'created_at', 'updated_at'
        ]





class UpdateProfileSerializer(serializers.ModelSerializer): 
    image = serializers.ImageField(required=False)
    fullname = serializers.CharField(max_length=200, required=False)
    date_of_birth = serializers.DateField(required=False)
    weight = serializers.FloatField(required=False, help_text="Weight in kilograms")
    height = serializers.FloatField(required=False, help_text="Height in centimeters")
    abdominal = serializers.FloatField(required=False)
    sacroiliac = serializers.FloatField(required=False)
    subscapularis = serializers.FloatField(required=False)
    triceps = serializers.FloatField(required=False)
    train_duration = serializers.CharField(required=False)

    

    #transletable data
    gender = serializers.ChoiceField(choices=GENDER, required=False)
    trainer = serializers.CharField(required=False)
    fitness_goals = serializers.CharField(required=False)
    injuries_discomfort = serializers.CharField(required=False)
    dietary_preferences = serializers.CharField(required=False)
    allergies = serializers.CharField(required=False)
    medical_conditions = serializers.CharField(required=False)

    class Meta:
        model = Profile
        fields = [
            'image', 'fullname', 'date_of_birth', 'weight', 'height', 'abdominal',
            'sacroiliac', 'subscapularis', 'triceps', 'train_duration',
            'gender', 'trainer', 'fitness_goals', 'injuries_discomfort',
            'dietary_preferences', 'allergies', 'medical_conditions',
            'gender_spanish', 'trainer_spanish', 'fitness_goals_spanish',
            'injuries_discomfort_spanish', 'dietary_preferences_spanish',
            'allergies_spanish', 'medical_conditions_spanish',
        ]



    