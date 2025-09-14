# Django Email Setup Guide

## 1. Basic Email Configuration in settings.py

### SMTP Configuration (Production)

```python
# settings.py

# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# SMTP settings
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use app password for Gmail

# Default from email
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

```

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost' # MailHog's SMTP server is usually hosted on localhost
EMAIL_PORT = 1025 # MailHog's default SMTP port
EMAIL_USE_TLS = False # MailHog doesn't use TLS by default
EMAIL_HOST_USER = '' # No authentication needed for MailHog
EMAIL_HOST_PASSWORD = '' # No password required
DEFAULT_FROM_EMAIL = 'webmaster@localhost' # Default sender email

```

### Console Backend (Development)

```python
# For development - prints emails to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### File Backend (Testing)

```python
# For testing - saves emails to files
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages'  # Directory for email files
```

## 2. Environment Variables Setup

Create a `.env` file for sensitive information:

```bash
# .env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Load in settings.py:

```python
import os
from decouple import config  # pip install python-decouple

EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

## 3. Common Email Providers Configuration

### Gmail

```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# Note: Use App Passwords, not regular password
```

### Outlook/Hotmail

```python
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

### Yahoo

```python
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

### SendGrid

```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
```

## 4. Sending Emails in Views

### Basic Email Sending

```python
from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib import messages

def send_email_view(request):
    try:
        send_mail(
            subject='Subject here',
            message='Here is the message.',
            from_email='from@example.com',
            recipient_list=['to@example.com'],
            fail_silently=False,
        )
        messages.success(request, 'Email sent successfully!')
    except Exception as e:
        messages.error(request, f'Error sending email: {str(e)}')

    return render(request, 'email_form.html')
```

### HTML Email with Templates

```python
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_html_email(request):
    subject = 'Welcome to Our Site'

    # Render HTML template
    html_message = render_to_string('emails/welcome.html', {
        'user': request.user,
        'site_name': 'Your Site'
    })

    # Create plain text version
    plain_message = strip_tags(html_message)

    # Send email
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email='noreply@yoursite.com',
        to=['user@example.com']
    )
    email.attach_alternative(html_message, "text/html")
    email.send()
```

### Mass Email Sending

```python
from django.core.mail import send_mass_mail

def send_mass_email():
    message1 = ('Subject 1', 'Message 1', 'from@example.com', ['user1@example.com'])
    message2 = ('Subject 2', 'Message 2', 'from@example.com', ['user2@example.com'])

    send_mass_mail((message1, message2), fail_silently=False)
```

## 5. Email Templates

### HTML Email Template (emails/welcome.html)

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <title>Welcome to {{ site_name }}</title>
    <style>
      body {
        font-family: Arial, sans-serif;
      }
      .header {
        background-color: #f8f9fa;
        padding: 20px;
      }
      .content {
        padding: 20px;
      }
      .footer {
        background-color: #e9ecef;
        padding: 10px;
        text-align: center;
      }
    </style>
  </head>
  <body>
    <div class="header">
      <h1>Welcome to {{ site_name }}!</h1>
    </div>
    <div class="content">
      <p>Hello {{ user.first_name }},</p>
      <p>Thank you for joining our platform. We're excited to have you!</p>
      <p>Get started by exploring our features.</p>
    </div>
    <div class="footer">
      <p>&copy; 2025 {{ site_name }}. All rights reserved.</p>
    </div>
  </body>
</html>
```

## 6. Email with Attachments

```python
from django.core.mail import EmailMessage
from django.conf import settings
import os

def send_email_with_attachment():
    email = EmailMessage(
        subject='Your Report',
        body='Please find the attached report.',
        from_email='sender@example.com',
        to=['recipient@example.com'],
    )

    # Attach file
    file_path = os.path.join(settings.MEDIA_ROOT, 'reports/monthly_report.pdf')
    email.attach_file(file_path)

    # Or attach content directly
    email.attach('filename.txt', 'file content', 'text/plain')

    email.send()
```

## 7. Custom Email Backend

Create a custom backend for special requirements:

```python
# backends.py
from django.core.mail.backends.base import BaseEmailBackend

class CustomEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        # Custom logic here
        for message in email_messages:
            # Process each email message
            pass
        return len(email_messages)

# In settings.py
EMAIL_BACKEND = 'myapp.backends.CustomEmailBackend'
```

## 8. Testing Email Functionality

### Test in Django Shell

```python
python manage.py shell

from django.core.mail import send_mail

send_mail(
    'Test Subject',
    'Test message',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

### Unit Tests

```python
from django.test import TestCase
from django.core import mail
from django.core.mail import send_mail

class EmailTest(TestCase):
    def test_send_email(self):
        send_mail(
            'Test Subject',
            'Test message',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )

        # Check that one message has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Check email content
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Test Subject')
        self.assertEqual(email.body, 'Test message')
        self.assertEqual(email.from_email, 'from@example.com')
        self.assertEqual(email.to, ['to@example.com'])
```

## 9. Form Integration Example

### Contact Form

```python
# forms.py
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)

# views.py
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import ContactForm

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            send_mail(
                subject=f'Contact Form: {subject}',
                message=f'From: {name} ({email})\n\n{message}',
                from_email=email,
                recipient_list=['admin@yoursite.com'],
            )

            return redirect('contact_success')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})
```

## 10. Advanced Features

### Email with Dynamic Content

```python
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

def send_dynamic_email(user, order):
    template = get_template('emails/order_confirmation.html')
    context = {
        'user': user,
        'order': order,
        'items': order.items.all(),
        'total': order.get_total(),
    }

    html_content = template.render(context)

    email = EmailMultiAlternatives(
        subject=f'Order Confirmation #{order.id}',
        body='Thank you for your order!',
        from_email='orders@yoursite.com',
        to=[user.email]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()
```

### Async Email Sending (with Celery)

```python
# tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    return send_mail(subject, message, from_email, recipient_list)

# In your view
from .tasks import send_email_task

def some_view(request):
    # Send email asynchronously
    send_email_task.delay(
        'Subject',
        'Message',
        'from@example.com',
        ['to@example.com']
    )
```

## 11. Security Best Practices

1. **Use App Passwords**: For Gmail, use App Passwords instead of regular passwords
2. **Environment Variables**: Store sensitive email credentials in environment variables
3. **Rate Limiting**: Implement rate limiting to prevent email spam
4. **Validation**: Always validate email addresses before sending
5. **Fail Silently**: Consider using `fail_silently=True` in production to prevent errors from exposing sensitive information

## 12. Common Issues and Solutions

### Gmail Authentication Error

- Enable 2-factor authentication
- Generate an App Password
- Use the App Password instead of your regular password

### Emails Going to Spam

- Set up SPF, DKIM, and DMARC records
- Use a reputable email service
- Include unsubscribe links
- Avoid spam trigger words

### Connection Timeout

- Check firewall settings
- Verify SMTP server and port
- Test with telnet: `telnet smtp.gmail.com 587`

This guide covers the essential aspects of setting up and using email functionality in Django. Choose the configuration that best fits your needs and remember to test thoroughly in development before deploying to production.
