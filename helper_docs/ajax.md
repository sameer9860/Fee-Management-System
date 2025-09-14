- A **Django `ModelForm`** with text + file fields.
- A **template** that uses AJAX (`fetch`) for both **GET** (load form) and **POST** (submit form).
- CSRF token handling for AJAX.
- JSON response from the backend.

---

## **1. `models.py`**

```python
from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="uploads/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

---

## **2. `forms.py`**

```python
from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "file"]
```

---

## **3. `views.py`**

```python
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .forms import DocumentForm
from .models import Document

# GET form view
def document_form_view(request):
    form = DocumentForm()
    return render(request, "document_form.html", {"form": form})

# AJAX POST handler
@require_http_methods(["POST"])
def document_submit_ajax(request):
    form = DocumentForm(request.POST, request.FILES)
    if form.is_valid():
        doc = form.save()
        return JsonResponse({
            "success": True,
            "message": "Document uploaded successfully.",
            "id": doc.id,
            "title": doc.title
        })
    return JsonResponse({"success": False, "errors": form.errors}, status=400)

# GET form data (example for AJAX GET)
@require_http_methods(["GET"])
def document_list_ajax(request):
    docs = Document.objects.values("id", "title", "file", "created_at")
    return JsonResponse(list(docs), safe=False)
```

---

## **4. `urls.py`**

```python
from django.urls import path
from . import views

urlpatterns = [
    path("documents/form/", views.document_form_view, name="document_form"),
    path("documents/submit/", views.document_submit_ajax, name="document_submit_ajax"),
    path("documents/list/", views.document_list_ajax, name="document_list_ajax"),
]
```

---

## **5. `templates/document_form.html`**

```html
{% load static %}
<!DOCTYPE html>
<html>
  <head>
    <title>AJAX Form Upload</title>
    <meta name="csrf-token" content="{{ csrf_token }}" />
  </head>
  <body>
    <h2>Upload Document (AJAX)</h2>

    <form id="docForm" enctype="multipart/form-data">
      {% csrf_token %} {{ form.as_p }}
      <button type="submit">Submit</button>
    </form>

    <hr />
    <button id="loadDocs">Load Documents (AJAX GET)</button>
    <ul id="docList"></ul>

    <script>
      // Get CSRF token from cookie (Django docs recommended way)
      function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
          const cookies = document.cookie.split(";");
          for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
              cookieValue = decodeURIComponent(
                cookie.substring(name.length + 1)
              );
              break;
            }
          }
        }
        return cookieValue;
      }
      const csrftoken = getCookie("csrftoken");

      // Handle form submission
      document
        .getElementById("docForm")
        .addEventListener("submit", function (e) {
          e.preventDefault();

          const formData = new FormData(this);

          fetch("{% url 'document_submit_ajax' %}", {
            method: "POST",
            headers: { "X-CSRFToken": csrftoken },
            body: formData,
          })
            .then((response) => response.json())
            .then((data) => {
              if (data.success) {
                alert(data.message);
              } else {
                alert("Error: " + JSON.stringify(data.errors));
              }
            })
            .catch((err) => console.error(err));
        });

      // Handle AJAX GET
      document
        .getElementById("loadDocs")
        .addEventListener("click", function () {
          fetch("{% url 'document_list_ajax' %}")
            .then((response) => response.json())
            .then((data) => {
              const list = document.getElementById("docList");
              list.innerHTML = "";
              data.forEach((doc) => {
                const li = document.createElement("li");
                li.textContent = `${doc.title} (${doc.file})`;
                list.appendChild(li);
              });
            });
        });
    </script>
  </body>
</html>
```

---

## **How it works**

1. **GET Form**

   - `/documents/form/` → Renders the form in HTML.
   - Form has `{% csrf_token %}` so Django cookies store it.

2. **AJAX POST**

   - JS intercepts submit.
   - Sends `FormData` with `fetch` to `/documents/submit/`.
   - Backend validates with `DocumentForm` and returns JSON.

3. **AJAX GET**

   - Clicking “Load Documents” fetches `/documents/list/` and displays them.

---
