# Django Telemedicine Project

This is a Django-based telemedicine project that allows users and doctors to interact, manage appointments, upload medical records. The user can also use the Admin panal for managing the data. This project main concert was to make it simple and efficient.

## 🚀 Features

- Patient & Doctor registration and login
- Appointment management
- Profile picture and medical record uploads
- Admin panel for management

## 🛠️ Setup Instructions

Follow these steps to run the project locally:

1. Clone the repository

2. Install the required packages by running `pip install -r requirements.txt` in your terminal

3. Set up the Database by running `python manage.py makemigrations` and `python manage.py migrate` in your terminal

4. Create a superuser by running `python manage.py createsuperuser` in your terminal

5. Run the project by running `python manage.py runserver` in your terminal

6. Media Files
Ensure the media directory exists for uploaded files (e.g., profile pictures, medical records). 
* [media]
   * [profile_pics]
   * [medical_records]

You can create it manually if it doesn't exist:
`mkdir media` in your terminal
`cd media` in your terminal
`mkdir profile_pics` in your terminal
`mkdir medical_records` in your terminal


