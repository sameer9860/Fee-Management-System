# 🚀 Fee Management System - Installation Guide

# 1. Clone the Repository
git clone https://github.com/sameer9860/Fee-Management-System.git

cd Fee-Management-System

# 2. Create Virtual Environment
python -m venv env

# 3. Activate Virtual Environment
# Windows (PowerShell)
.\env\Scripts\activate
# windows(CMD)
env\Scripts\activate
# macOS/Linux
source env/bin/activate

# 4. Install Dependencies
pip install -r requirements.txt

# 5. Apply Database Migrations
python manage.py migrate

# 6. Create Superuser (Admin)
python manage.py createsuperuser
# 👉 Follow the prompts to set up your admin account

# 7. Run Development Server
python manage.py runserver

# 8. Run Tailwind Server
python manage.py tailwind start 

# 9.Run Tailwind and django server at once 
python manage.py tailwind dev

# 10. Access the Application
# Open your browser and go to:
# http://127.0.0.1:8000

# Fee Management System Image

![Fee Management System](theme/static/images/fmsfinal.png)
![Login](Screenshots/login.png)
![Register](Screenshots/register.png)
![Dashboards](Screenshots/dashboard.png)![Dashboard](Screenshots/dashboard2.png)
![Classes](Screenshots/classes.png)
![Fees](Screenshots/Fees.png)
![Students](Screenshots/students.png)
![AdminProfile](Screenshots/profileadmin.png)
![StudentProfile](Screenshots/studentProfile.png)
![Payments](Screenshots/paydue.png)
![Payments](Screenshots/makepayment.png)
![Payments](Screenshots/gateway.png)
![Payments](Screenshots/esewa.png)
![Payments](Screenshots/esewa2.png)
![Payments](Screenshots/esewa3.png)
![Payments](Screenshots/khalti.png)
![Payments](Screenshots/khalti2.png)





