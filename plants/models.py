from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Plant(models.Model):
    name = models.CharField(max_length=100, default="Unknown Plant")
    sun_exposure = models.CharField(max_length=100, default="Unknown")
    water_requirements = models.CharField(max_length=100, default="Unknown")
    growth_habit = models.CharField(max_length=100, default="Unknown")
    care_instructions = models.TextField(default="No instructions available.")
    image = models.ImageField(upload_to='plant_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class UserPlant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.plant.name}"

class NotebookEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    entry_text = models.TextField(default="No entry text available.")
    entry_date = models.DateTimeField(auto_now_add=True)

class SoilTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ph_level = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    nitrogen_level = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    phosphorus_level = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    potassium_level = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    organic_matter = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    soil_texture = models.CharField(max_length=100, default="Unknown")
    preferred_plants = models.ManyToManyField(Plant)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    first_name = models.CharField(max_length=100, default="User")
    
    def __str__(self):
        return self.user.username