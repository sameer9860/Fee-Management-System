from background_task import background
from django.conf import settings
import csv
from school.models import TempCSVFile, Grade
import random
import string
from accounts.models import CustomUser


def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def generate_unique_username(name, existing_usernames):
    username = name.lower().replace(" ", "")
    i = 1
    while username in existing_usernames:
        username = f"{username}{i}"
        i += 1
    return username


@background(schedule=3)
def bulk_create_students_from_csv(file_obj_id, grade_id):  # background task
    print("Bulk student creation started")
    try:
        csv_file = TempCSVFile.objects.get(id=file_obj_id)
        grade = Grade.objects.get(id=grade_id)
    except Exception as e:
        print("Failed to get file or grade. So task failed", e)
        return

    full_file_path = f"{settings.MEDIA_ROOT}/{csv_file.file.name}"

    with open(full_file_path, "r") as file:
        reader = csv.reader(file)
        header = reader.__next__()

        existing_usernames = list(
            CustomUser.objects.filter(role=CustomUser.Roles.STUDENT).values_list(
                "username", flat=True
            )  # ['ram', 'hari', 'asdf', 'locap']
        )

        for row in reader:
            name, email, address, phone = row

            first_name, *middle, last_name = name.split(" ")  # ram kumar thapa magar
            first_name = first_name + " ".join(middle)

            password = generate_random_password()

            unique_username = generate_unique_username(name, existing_usernames)
            existing_usernames.append(unique_username)

            student = CustomUser.objects.create_user(
                username=unique_username,
                email=email,
                address=address,
                phone_number=phone,
                role=CustomUser.Roles.STUDENT,
                first_name=first_name,
                last_name=last_name,
                grade=grade,
                password=password,
                stu_visible_pass=password,
            )
            print("student-created", student)

    deleted_file = csv_file.delete()
    print("Deleted file", deleted_file)
