import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tele_Medicine.settings")  # Change to your settings module

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()