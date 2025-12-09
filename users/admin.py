from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'father_name', 'age', 'dob', 'address')
    search_fields = ['name', 'father_name']

admin.site.register(UserProfile, UserProfileAdmin)
