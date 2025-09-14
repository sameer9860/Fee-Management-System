# Creating Custom user in Django

## ✅ 1. Using `AbstractUser`

This is the **simplest and most common** way to customize Django’s user model.

### 📁 `accounts/models.py`

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.username
```

---

### 📁 `accounts/admin.py`

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('age', 'phone_number')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
```

---

### 📁 `settings.py`

```python
AUTH_USER_MODEL = 'accounts.CustomUser'
```

✅ Then run:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🔧 2. Using `AbstractBaseUser` (Full Custom User)

This gives you **total control** over the fields and behavior.

### 📁 `accounts/models.py`

```python
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
```

---

### 📁 `accounts/admin.py`

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser

class CustomUserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'name', 'is_staff']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
```

---

### 📁 `settings.py`

```python
AUTH_USER_MODEL = 'accounts.CustomUser'
```

✅ Then run:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🚀 Summary

| Method             | Recommended When…                                           | Setup Effort |
| ------------------ | ----------------------------------------------------------- | ------------ |
| `AbstractUser`     | You just need a few extra fields, like `phone`, `age`, etc. | Low          |
| `AbstractBaseUser` | You want to fully customize login fields, roles, etc.       | Medium/High  |

---
