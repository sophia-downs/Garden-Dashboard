from django import forms
from plants.models import *

class SuggestedPlantTestForm(forms.Form):
    SUN_EXPOSURE_CHOICES = [('any', 'Any')] + [(choice, choice) for choice in Plant.objects.values_list('sun_exposure', flat=True).distinct()]
    WATER_REQUIREMENTS_CHOICES = [('any', 'Any')] + [(choice, choice) for choice in Plant.objects.values_list('water_requirements', flat=True).distinct()]
    GROWTH_HABIT_CHOICES = [('any', 'Any')] + [(choice, choice) for choice in Plant.objects.values_list('growth_habit', flat=True).distinct()]

    sun_exposure = forms.ChoiceField(choices=SUN_EXPOSURE_CHOICES, required=False)
    water_requirements = forms.ChoiceField(choices=WATER_REQUIREMENTS_CHOICES, required=False)
    growth_habit = forms.ChoiceField(choices=GROWTH_HABIT_CHOICES, required=False)
