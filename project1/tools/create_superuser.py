import os
import sys
from pathlib import Path

# Ensure project root is on sys.path (script lives in tools/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project1.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'admin'
email = 'admin@example.com'
password = 'AdminPass123!'

if User.objects.filter(username=username).exists():
    print('superuser exists')
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print('superuser created')
