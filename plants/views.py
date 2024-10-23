import json
import logging
import requests
from datetime import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd

from plants.models import *
from plants.forms import *

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('base_generic') 
        else:
            return HttpResponse('Invalid login credentials')   

    return render(request, 'login.html')

@login_required
def base_generic(request):
    return render(request, 'base_generic.html')

@login_required
def plant_library(request):
    form = SuggestedPlantTestForm(request.GET or None)  

    if form.is_valid():
        sun_exposure = form.cleaned_data.get('sun_exposure')
        water_requirements = form.cleaned_data.get('water_requirements')
        growth_habit = form.cleaned_data.get('growth_habit')

        query = Plant.objects.all()

        if sun_exposure and sun_exposure != 'any':
            query = query.filter(sun_exposure=sun_exposure)

        if water_requirements and water_requirements != 'any':
            query = query.filter(water_requirements=water_requirements)

        if growth_habit and growth_habit != 'any':
            query = query.filter(growth_habit=growth_habit)

        query = query.order_by('name')
    else:
        query = Plant.objects.all().order_by('name')

    return render(request, 'plant_library.html', {'form': form, 'plants': query})

@login_required
@require_POST
def toggle_plant(request, plant_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        plant = get_object_or_404(Plant, pk=plant_id)
        user_plant, created = UserPlant.objects.get_or_create(user=request.user, plant=plant)

        if data['action'] == 'add':
            user_plant.save()
            return JsonResponse({'success': True})
        elif data['action'] == 'remove':
            user_plant.delete()
            return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def plant_care(request):
    care_tips = [
        {
            "id": 1,
            "title": "Handling Toxic Plants",
            "description": "Learn how to identify and safely handle toxic plants to prevent harm to yourself and others."
        },
        {
            "id": 2,
            "title": "Using Protective Gear",
            "description": "Discover the importance of wearing appropriate protective gear while gardening to prevent injuries."
        },
        {
            "id": 3,
            "title": "Pesticide Use and Storage",
            "description": "Understand how to use and store pesticides safely to protect your health and the environment."
        },
        {
            "id": 4,
            "title": "Preventing Allergies and Respiratory Issues",
            "description": "Find out how to reduce the risk of allergies and respiratory problems while working in the garden."
        },
        {
            "id": 5,
            "title": "Preparing for Spring Planting",
            "description": "Get ready for a successful spring planting season with these essential preparation tips."
        },
        {
            "id": 6,
            "title": "Summer Watering Strategies",
            "description": "Explore effective watering techniques to keep your garden thriving during the hot summer months."
        },
        {
            "id": 7,
            "title": "Fall Harvesting and Cleanup",
            "description": "Learn how to efficiently harvest your crops and prepare your garden for the winter season."
        },
        {
            "id": 8,
            "title": "Winter Garden Care",
            "description": "Discover strategies for maintaining your garden during the cold winter months and preparing for spring."
        },
        {
            "id": 9,
            "title": "Choosing the Right Tools",
            "description": "Learn how to select the right gardening tools for your specific needs and maintain them properly."
        },
        {
            "id": 10,
            "title": "Understanding Soil Types",
            "description": "Explore the different soil types and how to amend them for optimal plant growth and health."
        },
        {
            "id": 11,
            "title": "Organic vs. Chemical Fertilizers",
            "description": "Compare organic and chemical fertilizers to make informed decisions for your garden's nutrition."
        },
        {
            "id": 12,
            "title": "The Best Time to Plant",
            "description": "Discover how to choose the best time to plant based on your climate and plant hardiness zone."
        },
        {
            "id": 13,
            "title": "Managing Garden Weeds",
            "description": "Learn effective strategies to manage and control weeds without harming your plants."
        },
        {
            "id": 14,
            "title": "Companion Planting Techniques",
            "description": "Explore companion planting techniques to enhance plant growth and reduce pests naturally."
        },
        {
            "id": 15,
            "title": "Maximizing Sunlight for Growth",
            "description": "Understand how to position your plants for maximum sunlight exposure and optimal growth."
        },
        {
            "id": 16,
            "title": "Building a Compost System",
            "description": "Learn how to create and maintain a compost system to recycle garden waste into nutrient-rich soil."
        }
    ]
    context = {'care_tips': care_tips}
    return render(request, 'plant_care.html', context)


@login_required
def plant_care_detail(request, tip_id):
    care_tip_details = {
        1: {
            "title": "Handling Toxic Plants",
            "content": "Some common houseplants and garden plants can be toxic to humans and pets. For example, philodendrons, peace lilies, and oleanders contain compounds that can cause skin irritation or more severe reactions if ingested. It is crucial to identify these plants in your garden or home and ensure they are out of reach of curious pets and small children. Always wear gloves when handling unknown plants, and research their properties before planting or relocating them in your garden."
        },
        2: {
            "title": "Using Protective Gear",
            "content": "When working in the garden, especially with plants that have thorns or spines, such as roses or cacti, wearing protective clothing can prevent injuries. Gloves, long sleeves, and safety goggles protect your skin and eyes from cuts, scratches, and potential allergic reactions. Additionally, using tools with long handles can help avoid unnecessary contact with prickly plants."
        },
        3: {
            "title": "Pesticide Use and Storage",
            "content": "Pesticides and herbicides are often used to manage pests and weeds but can be dangerous if misused. Always follow the instructions on the label and wear appropriate protective gear. Store chemicals in their original containers, clearly labeled, and in a secure location away from children and pets. Consider using natural alternatives, such as neem oil or insecticidal soap, to reduce chemical exposure in your garden."
        },
        4: {
            "title": "Preventing Allergies and Respiratory Issues",
            "content": "Pollen, mold, and dust from plants can cause allergies and respiratory problems for sensitive individuals. Choose plants known for low pollen production, such as ferns or palms, to minimize allergic reactions. Regularly clean leaves with a damp cloth to reduce dust buildup, and avoid overwatering, which can promote mold growth. If you experience persistent symptoms, consider consulting an allergist."
        },
        5: {
            "title": "Preparing for Spring Planting",
            "content": "Spring is a time of renewal and growth in the garden. To prepare for planting, start by clearing away winter debris and cleaning your gardening tools. Test your soil to determine its nutrient content and pH level, and amend it as needed. Consider starting seeds indoors to get a head start on the growing season, and plan your garden layout, keeping companion planting and crop rotation principles in mind."
        },
        6: {
            "title": "Summer Watering Strategies",
            "content": "During the hot summer months, proper watering is crucial to keep your plants healthy. Water early in the morning or late in the evening to minimize evaporation and ensure deep root penetration. Use mulch to retain soil moisture and reduce weeds. Consider installing a drip irrigation system for efficient and consistent watering, and pay special attention to container plants, which dry out faster than those in the ground."
        },
        7: {
            "title": "Fall Harvesting and Cleanup",
            "content": "Fall is the time to harvest the last of your crops and prepare your garden for winter. Pick fruits and vegetables at their peak ripeness, and store or preserve them for future use. Clean up plant debris to prevent pests and diseases from overwintering in your garden. Consider planting cover crops, such as clover or rye, to enrich the soil and protect it from erosion during the winter months."
        },
        8: {
            "title": "Winter Garden Care",
            "content": "Even in winter, your garden requires attention. Protect sensitive plants from frost by covering them with burlap or using cloches. Prune dead or damaged branches to prevent disease and encourage healthy growth in the spring. Take this time to plan next year's garden, order seeds, and start a garden journal to track successes and areas for improvement. Regularly check stored produce for spoilage, and enjoy winter crops like kale and Brussels sprouts."
        },
        9: {
            "title": "Choosing the Right Tools",
            "content": "Using the right tools can make gardening tasks easier and more efficient. Select high-quality tools that match your garden's needs, such as pruners, spades, and trowels. Regularly clean and sharpen your tools to prolong their lifespan and maintain performance. Consider ergonomically designed tools to reduce strain and fatigue during prolonged use."
        },
        10: {
            "title": "Understanding Soil Types",
            "content": "Soil is the foundation of a healthy garden, and understanding its composition is crucial for plant success. Learn about different soil types—clay, sandy, loamy—and their characteristics. Conduct a soil test to determine pH and nutrient levels, and amend the soil with organic matter or other additives to improve structure and fertility."
        },
        11: {
            "title": "Organic vs. Chemical Fertilizers",
            "content": "Choosing between organic and chemical fertilizers depends on your garden's needs and your environmental considerations. Organic fertilizers, like compost and manure, improve soil health and structure over time. Chemical fertilizers provide a quick nutrient boost but can lead to soil degradation if overused. Balance both types to maximize plant health and sustainability."
        },
        12: {
            "title": "The Best Time to Plant",
            "content": "Timing your planting is crucial for success. Research your climate zone and plant hardiness to determine the best planting schedule. Use frost dates and soil temperature guides to ensure optimal growing conditions. Some plants, like leafy greens, thrive in cooler weather, while others, like tomatoes, require warm soil to flourish."
        },
        13: {
            "title": "Managing Garden Weeds",
            "content": "Weeds compete with your plants for nutrients, light, and water. Regularly remove weeds by hand or use mulching to suppress growth. Consider using landscape fabric in problem areas, and plant densely to outcompete weeds. Natural herbicides can be used for persistent problems, but always follow application guidelines."
        },
        14: {
            "title": "Companion Planting Techniques",
            "content": "Companion planting involves growing different plants together to enhance growth and deter pests. For example, planting marigolds near vegetables can repel nematodes, while basil improves the flavor of tomatoes. Research plant pairings to optimize your garden layout and increase biodiversity."
        },
        15: {
            "title": "Maximizing Sunlight for Growth",
            "content": "Sunlight is essential for photosynthesis and plant growth. Position plants based on their light requirements—full sun, partial shade, or full shade. Use reflective surfaces, such as white mulch, to increase light exposure in darker areas. Prune trees and shrubs that block sunlight to allow more light to reach your garden."
        },
        16: {
            "title": "Building a Compost System",
            "content": "Composting turns organic waste into nutrient-rich soil amendments. Start a compost pile with layers of green (nitrogen-rich) and brown (carbon-rich) materials. Maintain moisture and aeration by turning the pile regularly. Finished compost improves soil structure, adds nutrients, and helps retain moisture."
        }
    }

    care_tip = care_tip_details.get(tip_id, {"title": "Unknown", "content": "No content available for this tip."})
    return render(request, 'plant_care_detail.html', {'care_tip': care_tip})

def weather_dashboard(request):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 39.9569,
        "longitude": 86.0172,
        "current_weather": True,
        "hourly": ["temperature_2m", "precipitation_probability", "precipitation", "soil_temperature_6cm"],
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() 
        data = response.json()  

        current_temp = round(data['current_weather']['temperature'], 3)
        
        hourly = data['hourly']
        hourly_precipitation_probability = hourly['precipitation_probability']
        hourly_soil_temperature_6cm = hourly['soil_temperature_6cm']
        
        precipitation_probability_today = round(hourly_precipitation_probability[0], 3)
        soil_temperature_today = round(hourly_soil_temperature_6cm[0], 3)
        
        daily = data['daily']
        daily_temperature_2m_max = daily['temperature_2m_max']
        daily_temperature_2m_min = daily['temperature_2m_min']
        dates = pd.to_datetime(daily['time'])

        weekly_forecast = []
        for index in range(1, len(dates)):  
            day_data = {
                "date": dates[index].strftime("%Y-%m-%d"),
                "max_temp": round(daily_temperature_2m_max[index], 3),
                "min_temp": round(daily_temperature_2m_min[index], 3),
                "precipitation_probability": round(max(hourly_precipitation_probability[index*24:(index+1)*24]), 3),
                "soil_temperature": round(hourly_soil_temperature_6cm[index*24], 3)
            }
            weekly_forecast.append(day_data)

        context = {
            "current_temp": current_temp,
            "max_temp": round(daily_temperature_2m_max[0], 3),
            "min_temp": round(daily_temperature_2m_min[0], 3),
            "precipitation_probability_today": precipitation_probability_today,  
            "soil_temperature_today": soil_temperature_today,
            "weekly_forecast": weekly_forecast,
        }
    except Exception as e:
        print(f"Error retrieving weather data: {e}")
        context = {
            "error": "Unable to retrieve weather data at this time."
        }

    return render(request, 'weather_dashboard.html', context)

def safe_extract(values, index, default=0):
    try:
        return values[index]
    except (IndexError, ValueError, TypeError):
        return default

def get_ai_response(user_query):
    # port 5005
    rasa_url = "http://localhost:5005/webhooks/rest/webhook"
    headers = {'Content-Type': 'application/json'}
    data = {
        "sender": "user",
        "message": user_query
    }
    
    response = requests.post(rasa_url, json=data, headers=headers)
    if response.status_code == 200:
        messages = response.json()
        if messages:
            return messages[0].get('text', 'Sorry, I could not understand your question.')
        return 'No response from AI.'
    return 'Error communicating with AI server.'

@login_required
def garden_ai_view(request):
    response = None
    if request.method == "POST":
        user_query = request.POST.get("user_query", "")
        response = get_ai_response(user_query)

    return render(request, 'garden_ai.html', {'response': response})

@login_required
def view_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_plants = UserPlant.objects.filter(user=request.user).select_related('plant')

    context = {
        'user': request.user,
        'bio': user_profile.bio,
        'account_creation_date': request.user.date_joined,
        'user_plants': user_plants,
    }
    return render(request, 'view_profile.html', context)

@login_required
@require_POST
def remove_plant(request, plant_id):
    try:
        data = json.loads(request.body)
        action = data.get('action')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Malformed data, expecting valid JSON'}, status=400)

    if action == 'remove':
        plant = get_object_or_404(Plant, pk=plant_id)
        try:
            user_plant = UserPlant.objects.get(user=request.user, plant=plant)
            user_plant.delete()
            return JsonResponse({'success': True})
        except UserPlant.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Plant not found in your collection'}, status=404)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)