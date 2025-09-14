from django import forms
from .models import CustomUser
from django.forms import widgets as widget


class SchoolAdminLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "input w-full p-2 mb-2",
                "placeholder": "Username",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "input w-full p-2 mb-2",
                "placeholder": "Password",
            }
        )
    )


class SchoolAdminRegisterForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "input w-full p-2 mb-2",
                "placeholder": "Username",
            }
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "input w-full p-2 mb-2",
                "placeholder": "Email",
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "input w-full p-2 mb-2",
                "placeholder": "Password",
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "input w-full p-2 mb-2",
                "placeholder": "Confirm Password",
            }
        )
    )
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "input w-full p-2 mb-2",
                "placeholder": "First Name",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "input w-full p-2 mb-2",
                "placeholder": "Last Name",
            }
        ),
    )
    phone_number = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "class": "input w-full p-2 mb-2",
                "placeholder": "Phone",
            }
        ),
    )
    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "input w-full p-2 mb-2",
                "placeholder": "Address",
            }
        ),
    )
    profile_pic = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={"class": "file-input w-full p-2"}),
        required=False,
    )

    def clean(self):
        if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
            raise forms.ValidationError("Passwords do not match")

        if CustomUser.objects.filter(username=self.cleaned_data["username"]).exists():
            raise forms.ValidationError("Username already exists")

    def save(self, commit=True):
        user = CustomUser(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            phone_number=self.cleaned_data["phone_number"],
            address=self.cleaned_data["address"],
            profile_pic=self.cleaned_data["profile_pic"],
        )
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
