from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from .models import Profile, AISuggestData
from .service import AISuggestData_get

@receiver(post_save, sender=Profile)
def update_ai_suggest_data(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user

    ai_result = AISuggestData_get(
        date_of_birth=profile.date_of_birth,
        weight=profile.weight,
        height=profile.height,
        gender=profile.gender,
        trainer=profile.trainer,
        fitness_goals=profile.fitness_goals,
        injuries_discomfort=profile.injuries_discomfort,
        dietary_preferences=profile.dietary_preferences,
        allergies=profile.allergies,
        medical_conditions=profile.medical_conditions
    )

    ais_data, created = AISuggestData.objects.get_or_create(
        user=user,
        defaults={
            "calorie_need_daily": ai_result.calorie_goal,
            "water_liter": ai_result.water_intake,
            "sleep_duration": timedelta(hours=float(ai_result.sleep_hours))
        }
    )

    if not created:
        ais_data.calorie_need_daily = ai_result.calorie_goal
        ais_data.water_liter = ai_result.water_intake
        ais_data.sleep_duration = timedelta(hours=float(ai_result.sleep_hours))
        ais_data.save()

