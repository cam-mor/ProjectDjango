import os
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project1.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import StudyGroup, GroupMembership

print("=" * 60)
print("VERIFICACIÓN DE ROLES Y MEMBRESÍAS")
print("=" * 60)

# Verificar que exista el usuario admin
try:
    admin_user = User.objects.get(username='admin')
    print(f"\n✅ Usuario admin existe: {admin_user.username}")
    print(f"   Email: {admin_user.email}")
    print(f"   Is superuser: {admin_user.is_superuser}")
except User.DoesNotExist:
    print("\n❌ Usuario admin NO existe. Ejecuta: python tools\\create_superuser.py")

# Listar todos los grupos
groups = StudyGroup.objects.all()
print(f"\n📚 Total de grupos: {groups.count()}")

for group in groups:
    print(f"\n{'=' * 60}")
    print(f"Grupo: {group.name}")
    print(f"{'=' * 60}")
    
    memberships = GroupMembership.objects.filter(group=group).select_related('user')
    
    if memberships.exists():
        print(f"Miembros ({memberships.count()}):")
        for m in memberships:
            role_emoji = "👑" if m.role == "admin" else "⭐" if m.role == "moderator" else "👤"
            print(f"  {role_emoji} {m.user.username} - {m.role.upper()}")
    else:
        print("  ❌ No hay miembros en este grupo")

print(f"\n{'=' * 60}")
print("RESUMEN")
print(f"{'=' * 60}")

total_users = User.objects.count()
total_memberships = GroupMembership.objects.count()
total_admins = GroupMembership.objects.filter(role='admin').count()
total_moderators = GroupMembership.objects.filter(role='moderator').count()
total_members = GroupMembership.objects.filter(role='member').count()

print(f"Usuarios totales: {total_users}")
print(f"Membresías totales: {total_memberships}")
print(f"  - Admins: {total_admins}")
print(f"  - Moderators: {total_moderators}")
print(f"  - Members: {total_members}")

# Verificar si el admin está en algún grupo
if 'admin_user' in locals():
    admin_groups = StudyGroup.objects.filter(members=admin_user)
    print(f"\nGrupos donde está 'admin': {admin_groups.count()}")
    for g in admin_groups:
        membership = GroupMembership.objects.get(user=admin_user, group=g)
        print(f"  - {g.name} ({membership.role})")

print(f"\n{'=' * 60}")
print("INSTRUCCIONES:")
print(f"{'=' * 60}")
print("1. Si el admin NO está en ningún grupo, únete a uno desde la web")
print("2. Login: http://127.0.0.1:8000/admin/ (admin / AdminPass123!)")
print("3. Ve a un grupo y haz clic en 'Join Group'")
print("4. Como creador del grupo, serás admin automáticamente")
print(f"{'=' * 60}\n")
