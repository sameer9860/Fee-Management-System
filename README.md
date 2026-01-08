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

