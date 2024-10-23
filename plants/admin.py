from django.contrib import admin
from plants.models import *

admin.site.register(Plant)
admin.site.register(NotebookEntry)
admin.site.register(SoilTest)
admin.site.register(UserProfile)
