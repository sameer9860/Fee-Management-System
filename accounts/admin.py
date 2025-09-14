from django.contrib import admin
from .models import CustomUser, OTP

admin.site.register(CustomUser)


class OTPAdmin(admin.ModelAdmin):
    list_display = ("otp", "created_at")


admin.site.register(OTP, OTPAdmin)
