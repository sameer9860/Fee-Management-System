from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from school.models import Grade
import random


class Command(BaseCommand):
    """
    Creates a custom command for seeding students data for test
    """

    help = "Updates the database with student data"

    def handle(self, *args, **kwargs):
        """
        Create records based on the given scenario
        """
        self.stdout.write(self.style.SUCCESS("Started seeding student data..."))

        grades = Grade.objects.all()

        for i in range(10):
            user, created = CustomUser.objects.get_or_create(
                username=f"student{i}",
                defaults={
                    "first_name": f"student{i}",
                    "last_name": f"student{i}",
                    "email": f"student{i}@localhost",
                    "address": f"student{i} address",
                    "phone_number": "1234567890",
                    "role": CustomUser.Roles.STUDENT,
                    "password": "password1",
                    "grade": random.choice(grades),
                },
            )
            if not created:
                user.first_name = f"student{i}"
                user.last_name = f"student{i}"
                user.email = f"student{i}@localhost"
                user.address = f"student{i} address"
                user.phone_number = "1234567890"
                user.role = CustomUser.Roles.STUDENT
                user.grade = random.choice(grades)

                user.set_password("password1")
                user.save()

        self.stdout.write(self.style.SUCCESS("Finished seeding student data..."))
