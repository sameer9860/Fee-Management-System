
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        SCHOOL_ADMIN = "school_admin", "School Admin"
        STUDENT = "student", "Student"

    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    profile_pic = models.ImageField(upload_to="profile_pics", null=True, blank=True)

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.SCHOOL_ADMIN,
    )
    grade = models.ForeignKey(
        "school.Grade", on_delete=models.SET_NULL, null=True, blank=True
    )
    stu_visible_pass = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.username


class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_otp(email, length=8):
        import random

        user = CustomUser.objects.filter(email=email).first()
        if user is None:
            raise Exception("User does not exist")

        # try to generate a unique otp at most 3 times
        for _ in range(3):
            otp = "".join(str(random.randint(0, 9)) for _ in range(length))
            if not OTP.objects.filter(otp=otp).exists():
                break

        new_otp = OTP(user=user, otp=otp)
        new_otp.save()

        return new_otp.otp

    def is_expired(self):
        from django.utils import timezone
        import datetime

        now = timezone.now()
        return now - self.created_at > datetime.timedelta(minutes=10)

    @staticmethod
    def check_otp(otp_value):
        otp_record = OTP.objects.filter(otp=otp_value).first()
        if otp_record and not otp_record.is_expired():  # otp is valid and used
            user_id = otp_record.user.id
            otp_record.delete()
            return user_id
        return None

    def __str__(self):
        return self.otp
