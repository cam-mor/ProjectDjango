import os
import sys
from pathlib import Path
import random
import argparse
import csv
from datetime import datetime, timedelta, time

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project1.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from faker import Faker
from core.models import Profile, Subject, StudyGroup, GroupMembership, StudySession, StudyMaterial, Comment

User = get_user_model()
fake = Faker()


def create_users(n):
    users = []
    for i in range(n):
        username = f'user{i+1:03d}'
        email = f'{username}@example.com'
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
        else:
            user = User.objects.create_user(username=username, email=email, password='password')
        # create or update profile
        Profile.objects.update_or_create(
            user=user,
            defaults={
                'major': random.choice(['Mathematics','Physics','Programming','Chemistry','Biology','History','Economics']),
                'bio': fake.sentence(nb_words=12),
                'interests': ', '.join(fake.words(nb=5))
            }
        )
        users.append(user)
    return users


def create_groups(n, users):
    subjects = list(Subject.objects.all())
    groups = []
    for i in range(n):
        name = f"{fake.word().capitalize()} Study Group {i+1}"
        description = fake.paragraph(nb_sentences=3)
        subject = random.choice(subjects)
        creator = random.choice(users)
        max_members = random.randint(5, 25)
        group, created = StudyGroup.objects.get_or_create(
            name=name,
            defaults={
                'description': description,
                'subject': subject,
                'created_by': creator,
                'max_members': max_members,
                'is_active': True,
            }
        )
        # ensure creator is a member and admin
        GroupMembership.objects.update_or_create(user=creator, group=group, defaults={'role': 'admin'})
        groups.append(group)
    return groups


def add_memberships(target_count, users, groups):
    created = 0
    attempts = 0
    while created < target_count and attempts < target_count * 10:
        user = random.choice(users)
        group = random.choice(groups)
        attempts += 1
        if GroupMembership.objects.filter(user=user, group=group).exists():
            continue
        if group.members.count() >= group.max_members:
            continue
        GroupMembership.objects.create(user=user, group=group, role=random.choice(['member','member','moderator']))
        created += 1
    return created


def create_sessions(n, groups):
    sessions = []
    for i in range(n):
        group = random.choice(groups)
        title = f"{fake.word().capitalize()} Session {i+1}"
        description = fake.sentence(nb_words=20)
        # date between 60 days ago and 30 days in future
        start_date = timezone.now().date() - timedelta(days=60)
        rand_days = random.randint(0, 90)
        date = start_date + timedelta(days=rand_days)
        start_hour = random.randint(8, 20)
        duration_hours = random.choice([1, 1.5, 2, 2.5, 3])
        start_time = time(start_hour, random.choice([0, 15, 30, 45]))
        end_hour = start_hour + int(duration_hours)
        end_min = 0
        end_time = time(end_hour % 24, end_min)
        is_online = random.choice([True, False, False])
        meeting_link = fake.url() if is_online else ''
        created_by = group.created_by
        status = 'scheduled' if date >= timezone.now().date() else 'completed'
        session = StudySession.objects.create(
            group=group,
            title=title,
            description=description,
            date=date,
            start_time=start_time,
            end_time=end_time,
            location=fake.city() if not is_online else 'Online',
            is_online=is_online,
            meeting_link=meeting_link,
            status=status,
            created_by=created_by
        )
        sessions.append(session)
    return sessions


def create_materials(n, groups, users):
    materials = []
    for i in range(n):
        group = random.choice(groups)
        uploader = random.choice(users)
        title = fake.sentence(nb_words=4)
        description = fake.sentence(nb_words=12)
        link = fake.url() if random.random() < 0.7 else ''
        mat = StudyMaterial.objects.create(
            group=group,
            title=title,
            description=description,
            link=link,
            uploaded_by=uploader
        )
        materials.append(mat)
    return materials


def create_comments(n, groups, users):
    comments = []
    for i in range(n):
        group = random.choice(groups)
        author = random.choice(users)
        content = fake.sentence(nb_words=20)
        parent = random.choice(comments) if comments and random.random() < 0.2 else None
        comment = Comment.objects.create(group=group, author=author, content=content, parent=parent)
        comments.append(comment)
    return comments


def export_csvs(export_dir):
    os.makedirs(export_dir, exist_ok=True)
    # Users
    users_qs = User.objects.all().values('id','username','email','first_name','last_name','is_staff','is_superuser','is_active','date_joined')
    with open(os.path.join(export_dir,'users.csv'),'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(users_qs[0].keys() if users_qs else [])
        for row in users_qs:
            w.writerow(row.values())
    # Profiles
    prof_qs = Profile.objects.all().values('id','user_id','major','bio','interests','created_at')
    with open(os.path.join(export_dir,'profiles.csv'),'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(prof_qs[0].keys() if prof_qs else [])
        for row in prof_qs:
            w.writerow(row.values())
    # Groups
    grp_qs = StudyGroup.objects.all().values('id','name','description','subject_id','created_by_id','max_members','is_active','created_at')
    with open(os.path.join(export_dir,'groups.csv'),'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(grp_qs[0].keys() if grp_qs else [])
        for row in grp_qs:
            w.writerow(row.values())
    # Memberships
    mem_qs = GroupMembership.objects.all().values('id','user_id','group_id','role','joined_at')
    with open(os.path.join(export_dir,'memberships.csv'),'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(mem_qs[0].keys() if mem_qs else [])
        for row in mem_qs:
            w.writerow(row.values())
    # Sessions
    ses_qs = StudySession.objects.all().values('id','group_id','title','description','date','start_time','end_time','location','is_online','meeting_link','status','created_by_id','created_at')
    with open(os.path.join(export_dir,'sessions.csv'),'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(ses_qs[0].keys() if ses_qs else [])
        for row in ses_qs:
            w.writerow(row.values())
    # Materials
    mat_qs = StudyMaterial.objects.all().values('id','group_id','title','description','file','link','uploaded_by_id','created_at')
    with open(os.path.join(export_dir,'materials.csv'),'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(mat_qs[0].keys() if mat_qs else [])
        for row in mat_qs:
            w.writerow(row.values())
    # Comments
    com_qs = Comment.objects.all().values('id','group_id','author_id','content','parent_id','created_at')
    with open(os.path.join(export_dir,'comments.csv'),'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(com_qs[0].keys() if com_qs else [])
        for row in com_qs:
            w.writerow(row.values())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate sample data for Study Groups app')
    parser.add_argument('--users', type=int, default=30)
    parser.add_argument('--groups', type=int, default=15)
    parser.add_argument('--memberships', type=int, default=150)
    parser.add_argument('--sessions', type=int, default=200)
    parser.add_argument('--materials', type=int, default=150)
    parser.add_argument('--comments', type=int, default=300)
    parser.add_argument('--export-dir', type=str, default=str(PROJECT_ROOT / 'exports'))
    args = parser.parse_args()

    start = datetime.now()
    print('Generating sample data — this can take some time...')
    with transaction.atomic():
        users = create_users(args.users)
        print(f'Created/updated {len(users)} users')
        groups = create_groups(args.groups, users)
        print(f'Created {len(groups)} groups')
        created_members = add_memberships(args.memberships, users, groups)
        print(f'Created {created_members} additional memberships')
        sessions = create_sessions(args.sessions, groups)
        print(f'Created {len(sessions)} sessions')
        materials = create_materials(args.materials, groups, users)
        print(f'Created {len(materials)} materials')
        comments = create_comments(args.comments, groups, users)
        print(f'Created {len(comments)} comments')

    print('Exporting CSVs to', args.export_dir)
    export_csvs(args.export_dir)
    end = datetime.now()
    print('Done — elapsed', end - start)
    print('Exports saved in', args.export_dir)
