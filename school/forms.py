from django import forms
from school.models import School, Grade, Fee
from django.utils.text import slugify
from django.contrib.auth import get_user_model


CustomUser = get_user_model()


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        exclude = (
            "admin_user",
            "created_at",
            "slug",
            "code",
            "updated_at",
            "is_active",
        )

        widgets = {
            "established_date": forms.DateInput(attrs={"type": "date"}),
            "theme_color": forms.TextInput(attrs={"type": "color"}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request") if "request" in kwargs else None
        super().__init__(*args, **kwargs)

    def save(self, commit=True, *args, **kwargs):
        school = super(SchoolForm, self).save(commit=False, *args, **kwargs)

        if self.request:
            school.admin_user = self.request.user

        if not school.code:
            school_name = self.cleaned_data.get("name")
            school_name_words = school_name.split(" ")
            estd_year = self.cleaned_data.get("established_date").year
            code = "".join([word[0] for word in school_name_words]) + f"-{estd_year}"
            school.code = code
            school.slug = slugify(school_name)

        if commit:
            school.save()

        return school


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request") if "request" in kwargs else None
        super().__init__(*args, **kwargs)

    def save(self, commit=True, *args, **kwargs):
        grade = super(GradeForm, self).save(commit=False, *args, **kwargs)
        grade.school = self.request.user.school

        if commit:
            grade.save()

        return grade


class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ["name", "amount"]

    def save(self, commit=True, *args, **kwargs):
        grade = kwargs.pop("grade", None)
        fee = super(FeeForm, self).save(commit=False, *args, **kwargs)
        if grade is not None:
            fee.grade = grade

        if commit:
            fee.save()

        return fee


class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        help_text="Set an initial password for the student.",
    )
    grade = forms.ModelChoiceField(queryset=Grade.objects.none())

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "grade",
            "email",
            "phone_number",
            "address",
            "password",
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request") if "request" in kwargs else None
        super().__init__(*args, **kwargs)
        self.fields["grade"].queryset = Grade.objects.filter(
            school=self.request.user.school
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Roles.STUDENT  # enforce role
        user.set_password(self.cleaned_data["password"])  # hash password
        if commit:
            user.save()
        return user


class StudentBulkRegisterForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV File",
        help_text="Upload a CSV file containing student data.",
        required=True,
        widget=forms.FileInput(attrs={"accept": ".csv"}),
    )
    grade = forms.ModelChoiceField(queryset=Grade.objects.none())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request") if "request" in kwargs else None
        super().__init__(*args, **kwargs)

        self.fields["grade"].queryset = Grade.objects.filter(
            school=self.request.user.school
        )
