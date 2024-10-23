from django.urls import path, include
from django.shortcuts import redirect
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.user_login, name='user_login'),
    path('base_generic/', views.base_generic, name='base_generic'),  

    path('plant_library/', views.plant_library, name='plant_library'),
    path('toggle_plant/<int:plant_id>/', views.toggle_plant, name='toggle_plant'),

    path('plant_care/', views.plant_care, name='plant_care'),
    path('plant_care/<int:tip_id>/', views.plant_care_detail, name='plant_care_detail'),

    path('weather_dashboard/', views.weather_dashboard, name='weather_dashboard'),

    path('garden_ai/', views.garden_ai_view, name='garden_ai'),

    path('view_profile/', views.view_profile, name='view_profile'),
    path('remove_plant/<int:plant_id>/', views.remove_plant, name='remove_plant'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', lambda request: redirect('user_login')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

