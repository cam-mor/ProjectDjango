import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project1.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Subject, StudyGroup, GroupMembership, StudySession

# Create demo user
demo_user, created = User.objects.get_or_create(
    username='demo_student',
    defaults={
        'email': 'student@example.com',
        'is_active': True
    }
)
if created:
    demo_user.set_password('student123')
    demo_user.save()
    print("Created demo user - Username: demo_student, Password: student123")
else:
    print("Demo user already exists")

# Create sample study groups
subjects = {
    'Mathematics': ['Calculus Study Group', 'Weekly calculus practice and problem solving'],
    'Programming': ['Python Beginners Group', 'Learn Python programming fundamentals'],
    'Physics': ['Physics Lab Prep Group', 'Prepare for physics lab experiments'],
}

for subject_name, (group_name, description) in subjects.items():
    subject = Subject.objects.get(name=subject_name)
    group, created = StudyGroup.objects.get_or_create(
        name=group_name,
        defaults={
            'description': description,
            'subject': subject,
            'created_by': demo_user,
            'max_members': 10
        }
    )
    
    # Make demo user an admin of their groups
    GroupMembership.objects.get_or_create(
        user=demo_user,
        group=group,
        defaults={'role': 'admin'}
    )
    
    # Create upcoming study session
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    StudySession.objects.get_or_create(
        group=group,
        title=f'Next {subject.name} Session',
        defaults={
            'description': 'Upcoming study session - Topics will be posted soon',
            'date': next_week,
            'start_time': '18:00',
            'end_time': '20:00',
            'location': 'Online',
            'is_online': True,
            'created_by': demo_user
        }
    )
    
    if created:
        print(f"Created study group: {group_name}")
    else:
        print(f"Study group already exists: {group_name}")

print("\nSetup complete! You can now:")
print("1. Login as admin (username: admin, password: AdminPass123)")
print("2. Login as student (username: demo_student, password: student123)")
print("3. Visit http://127.0.0.1:8000/ to see the study groups")