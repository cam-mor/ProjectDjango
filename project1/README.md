# Study Groups Platform - Plataforma de Grupos de Estudio

Plataforma web colaborativa para gestión de grupos de estudio construida con Django. Los estudiantes pueden crear grupos, compartir materiales, programar sesiones y ver estadísticas de su progreso.

## 🌟 Características Principales

### Para Usuarios:
- 👥 Crear y unirse a grupos de estudio por materia
- 📚 Subir y compartir materiales de estudio (PDFs, links)
- 📅 Programar sesiones de estudio (online o presenciales)
- 💬 Discusiones con comentarios y respuestas
- � **Dashboard de estadísticas personales** con gráficos
- 📈 Ver estadísticas y top 5 miembros por grupo
- 📥 Exportar datos de sesiones en CSV
- 👤 Perfiles de usuario con biografía e intereses
- 🔍 Buscar y filtrar grupos por materia

### Para Administradores del Sistema:
- 🎯 **Dashboard de estadísticas globales** de toda la plataforma
- � Gráficos avanzados (dispersión, histogramas, tendencias)
- 🔍 Filtrar estadísticas por grupo y rango de fechas
- � Exportar datos globales y por grupo en CSV
- 🏆 Ver top miembros por grupo con métricas
- 👨‍💼 Panel admin completo de Django
- 🔐 Control total sobre usuarios y grupos

## 💻 Stack Tecnológico

- **Backend**: Django 5.x
- **Base de Datos**: SQLite (desarrollo), compatible con PostgreSQL/MySQL (producción)
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Gráficos**: Chart.js
- **Autenticación**: Sistema integrado de Django

## 📋 Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git (opcional)

## 🚀 Instalación Paso a Paso

### 1. Clonar o Descargar el Proyecto

```bash
# Si usas Git
git clone <url-de-tu-repositorio>
cd ProjectDjango/project1

# O simplemente descarga y descomprime el proyecto
```

### 2. Crear y Activar Entorno Virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install django pillow
```

### 4. Configurar la Base de Datos

```bash
# Crear las migraciones y aplicarlas
python manage.py migrate
```

### 5. Cargar Datos Iniciales (Materias)

```bash
python manage.py loaddata core/fixtures/initial_subjects.json
```

### 6. Crear Usuario Administrador

```bash
python manage.py createsuperuser
```

Se te pedirá:
- **Nombre de usuario**
- **Email** (opcional)
- **Contraseña** (mínimo 8 caracteres)

> ⚠️ **Importante:** Solo los superusuarios tienen acceso al dashboard global de estadísticas en `/stats/`

### 7. (Opcional) Crear Datos de Prueba

```bash
python create_samples.py
```

Esto creará:
- Usuario demo: `demo_student` / `student123`
- Grupos de ejemplo
- Sesiones y materiales de prueba

### 8. Ejecutar el Servidor de Desarrollo

```bash
python manage.py runserver
```

Visita: **http://127.0.0.1:8000/**

## 🔐 Niveles de Acceso y Funcionalidades

### 👤 Usuario Anónimo
- Ver página principal
- Buscar grupos públicos
- Registrarse en el sistema

### 🎓 Usuario Autenticado (Estudiante)
- **Grupos:**
  - Crear grupos de estudio
  - Unirse a grupos existentes
  - Ver detalles de sus grupos
  
- **Sesiones:**
  - Ver sesiones programadas
  - Crear sesiones (si es admin/moderador del grupo)
  
- **Materiales:**
  - Subir archivos y links
  - Descargar materiales compartidos
  
- **Comentarios:**
  - Publicar comentarios en grupos
  - Responder a comentarios
  
- **Estadísticas Personales** (`/my-stats/`):
  - 📊 Total de sesiones creadas
  - ⏱️ Horas totales estudiadas
  - 📈 Gráfico de horas por semana
  - 📊 Gráfico de sesiones por semana
  - 🏢 Gráfico de sesiones por grupo
  - 🎯 Dispersión: hora de inicio vs duración
  - 📊 Histograma de distribución de duraciones
  - 📅 Filtros por fecha (últimas 4w, 8w, 12w, 26w o personalizado)
  
- **Estadísticas por Grupo:**
  - Ver stats en el sidebar del detalle de grupo
  - Top 5 miembros del grupo
  - Exportar sesiones del grupo en CSV
  - Exportar top miembros en CSV

### 👨‍💼 Administrador de Grupo
- Todo lo anterior, más:
  - Editar configuración del grupo
  - Cambiar roles de miembros (member/moderator/admin)
  - Remover miembros
  - Gestionar sesiones y materiales

### 🔧 Superusuario (Admin del Sistema)
- **Panel Admin** (`/admin/`):
  - Acceso completo a Django Admin
  - Gestión de todos los usuarios, grupos, sesiones
  
- **Dashboard Global de Estadísticas** (`/stats/`):
  - 📊 **Totales Globales:**
    - Total de usuarios
    - Total de grupos
    - Total de sesiones
    - Total de materiales
    - Total de comentarios
    - Horas estudiadas (en el período seleccionado)
    - Usuarios activos (últimos 30 días)
  
  - 📈 **Gráficos:**
    - Horas por semana (12 semanas)
    - Sesiones por semana (12 semanas)
    - Nuevos usuarios/miembros por mes (6 meses)
    - Dispersión: hora de inicio vs duración
    - Histograma: distribución de duraciones
  
  - 🔍 **Filtros:**
    - Ver datos globales o por grupo específico
    - Filtrar por rango de fechas personalizado
    - Presets rápidos: 4w, 8w, 12w, 26w
  
  - 📥 **Exportaciones CSV:**
    - Exportar todas las sesiones (global o por grupo)
    - Exportar top miembros de un grupo seleccionado
    - Incluye: fecha, hora, duración, título, usuario, grupo, etc.

## 🎯 Guía de Uso Rápido

### Crear un Grupo de Estudio

1. Iniciar sesión
2. Click en **"Create Group"** en la navegación
3. Completar:
   - Nombre del grupo
   - Descripción
   - Materia
   - Número máximo de miembros
4. Click en **"Create"**

### Programar una Sesión

1. Entrar al detalle del grupo
2. Click en **"Schedule Session"** (solo admin/moderador)
3. Completar:
   - Título y descripción
   - Fecha y hora de inicio/fin
   - Tipo: Online (con link de reunión) o Presencial (con ubicación)
4. Click en **"Create"**

### Subir Material de Estudio

1. Entrar al detalle del grupo
2. Click en **"Upload Material"**
3. Seleccionar:
   - Archivo PDF/documento, o
   - Link a recurso externo
4. Agregar título y descripción
5. Click en **"Upload"**

### Ver Estadísticas Personales

1. Iniciar sesión como usuario normal
2. Click en **"Mis Estadísticas"** en el navbar
3. Visualizar:
   - Gráficos de progreso personal
   - Sesiones por grupo
   - Horas estudiadas
4. Aplicar filtros de fecha según necesidad

### Ver Estadísticas Globales (Solo Admin)

1. Iniciar sesión como **superusuario**
2. Click en **"Estadísticas"** en el navbar
3. Opciones:
   - Ver datos **globales** de toda la plataforma
   - Seleccionar un **grupo específico** del dropdown
   - Aplicar **filtros de fecha** personalizados o presets
4. **Exportar datos:**
   - Click en "Exportar CSV" para sesiones
   - Click en "Exportar Top Miembros" (requiere grupo seleccionado)

## 📊 Estructura de Dashboards de Estadísticas

### `/my-stats/` - Dashboard Personal (Usuarios)

**Métricas:**
- Total de sesiones creadas por el usuario
- Horas totales estudiadas
- Número de grupos en los que participa

**Gráficos:**
1. **Horas por semana** - Línea temporal de horas estudiadas
2. **Sesiones por semana** - Barras de sesiones creadas
3. **Sesiones por grupo** - Barras horizontales por grupo
4. **Dispersión** - Hora de inicio vs duración de sesiones
5. **Histograma** - Distribución de duraciones (0-0.5h, 0.5-1h, etc.)

**Controles:**
- Filtro de fecha: desde/hasta
- Presets: 4w, 8w, 12w, 26w
- Botón "Aplicar"

### `/stats/` - Dashboard Global (Solo Admin)

**Métricas:**
- Total usuarios, grupos, sesiones, materiales, comentarios
- Horas estudiadas en el período
- Usuarios activos (30 días)

**Gráficos:**
1. **Horas por semana** (12 semanas)
2. **Sesiones por semana** (12 semanas)
3. **Nuevos usuarios/miembros por mes** (6 meses)
4. **Dispersión** - Hora de inicio vs duración
5. **Histograma** - Distribución de duraciones

**Controles:**
- Selector de grupo (opcional)
- Filtros de fecha
- Presets rápidos
- Botones de exportación CSV

### Grupo Detail - Sidebar Stats

**Visibles para todos los miembros del grupo:**

**Métricas:**
- Total sesiones del grupo
- Horas estudiadas (grupo)
- Total materiales
- Total comentarios

**Gráficos:**
1. Horas por semana
2. Sesiones por semana
3. Dispersión
4. Histograma

**Extras:**
- Top 5 Miembros (tabla con usuario, sesiones, horas)
- Botón exportar sesiones CSV
- Botón exportar top miembros CSV

## 🗂️ Estructura del Proyecto

```
project1/
├── core/                          # Aplicación principal Django
│   ├── admin.py                   # Configuración del panel admin
│   ├── forms.py                   # Formularios (registro, grupos, sesiones, etc.)
│   ├── models.py                  # Modelos de base de datos
│   ├── urls.py                    # Rutas URL de la app
│   ├── views.py                   # Vistas y lógica de negocio
│   ├── fixtures/                  # Datos iniciales
│   │   └── initial_subjects.json  # Materias predefinidas
│   ├── templates/                 # Plantillas HTML
│   │   ├── core/
│   │   │   ├── base.html         # Template base con navbar
│   │   │   ├── home.html         # Página principal
│   │   │   ├── stats.html        # Dashboard admin global
│   │   │   ├── my_stats.html     # Dashboard personal usuario
│   │   │   ├── group_detail.html # Detalle de grupo con stats
│   │   │   ├── group_list.html   # Lista de grupos
│   │   │   ├── group_form.html   # Crear/editar grupo
│   │   │   ├── profile.html      # Perfil de usuario
│   │   │   ├── session_form.html # Crear/editar sesión
│   │   │   ├── material_form.html # Subir material
│   │   │   ├── comments/
│   │   │   │   └── comment_section.html
│   │   │   └── ...
│   │   └── registration/
│   │       ├── login.html
│   │       └── register.html
│   └── migrations/                # Migraciones de base de datos
├── project1/                      # Configuración del proyecto Django
│   ├── settings.py               # Configuración general
│   ├── urls.py                   # URLs raíz
│   ├── wsgi.py                   # WSGI para deployment
│   └── asgi.py                   # ASGI (opcional)
├── exports/                       # Scripts de exportación (opcional)
│   ├── *.csv                     # Datos exportados
│   └── ...
├── tools/                         # Scripts de utilidades
│   ├── create_superuser.py
│   └── generate_sample_data.py
├── manage.py                      # Script de gestión Django
├── create_samples.py              # Generador de datos de prueba
├── db.sqlite3                    # Base de datos SQLite (se crea automáticamente)
└── README.md                     # Esta documentación
```

## 🔧 Comandos Útiles de Django

### Migraciones
```bash
# Crear migraciones después de cambios en models.py
python manage.py makemigrations

# Aplicar migraciones a la base de datos
python manage.py migrate

# Ver SQL de una migración específica
python manage.py sqlmigrate core 0001

# Mostrar migraciones aplicadas
python manage.py showmigrations
```

### Gestión de Datos
```bash
# Cargar datos iniciales
python manage.py loaddata core/fixtures/initial_subjects.json

# Exportar datos a JSON
python manage.py dumpdata core.Subject --indent 2 > subjects.json

# Limpiar la base de datos y empezar de cero
# CUIDADO: Esto borra todos los datos
rm db.sqlite3
python manage.py migrate
python manage.py loaddata core/fixtures/initial_subjects.json
python manage.py createsuperuser
```

### Servidor y Shell
```bash
# Ejecutar servidor en puerto diferente
python manage.py runserver 8080

# Abrir shell de Django (interactivo)
python manage.py shell

# Ejecutar tests
python manage.py test

# Verificar el proyecto (sin ejecutar servidor)
python manage.py check
```

### Usuarios y Permisos
```bash
# Crear superusuario
python manage.py createsuperuser

# Cambiar contraseña de usuario
python manage.py changepassword <nombre_usuario>
```

### Producción
```bash
# Recolectar archivos estáticos
python manage.py collectstatic

# Ejecutar con Gunicorn (servidor de producción)
pip install gunicorn
gunicorn project1.wsgi:application
```

## 🐛 Solución de Problemas Comunes

### Error: "No such table: core_subject"
**Solución:**
```bash
python manage.py migrate
python manage.py loaddata core/fixtures/initial_subjects.json
```

### Error: "Port 8000 is already in use"
**Solución:**
```bash
# Usar otro puerto
python manage.py runserver 8001

# O encontrar y terminar el proceso en el puerto 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <numero_pid> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill
```

### Error: "Permission denied" en PowerShell
**Solución:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Olvidé la contraseña del superusuario
**Solución:**
```bash
python manage.py changepassword admin
```

### Los archivos estáticos no cargan
**Solución:**
- En desarrollo, Django los sirve automáticamente con `DEBUG=True`
- Verifica que `STATIC_URL` esté en `settings.py`
- Para producción, ejecuta `python manage.py collectstatic`

### Error: "ModuleNotFoundError: No module named 'django'"
**Solución:**
```bash
# Asegúrate de que el entorno virtual esté activado
# Windows:
.\venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate

# Luego instala Django
pip install django
```

## 📈 Modelos de Base de Datos

### Modelos Principales

1. **Subject** - Materias académicas
   - `name`: Nombre de la materia
   - `code`: Código (ej: "MAT101")
   - `description`: Descripción

2. **StudyGroup** - Grupos de estudio
   - `name`: Nombre del grupo
   - `description`: Descripción
   - `subject`: Materia (FK a Subject)
   - `created_by`: Usuario creador
   - `members`: Usuarios miembros (ManyToMany)
   - `max_members`: Límite de miembros
   - `is_active`: Estado del grupo

3. **GroupMembership** - Relación usuario-grupo
   - `user`: Usuario
   - `group`: Grupo
   - `role`: Rol (member/moderator/admin)
   - `joined_at`: Fecha de unión

4. **StudySession** - Sesiones de estudio
   - `group`: Grupo al que pertenece
   - `title`: Título de la sesión
   - `description`: Descripción
   - `date`: Fecha de la sesión
   - `start_time`: Hora de inicio
   - `end_time`: Hora de fin
   - `is_online`: Booleano (online/presencial)
   - `location`: Ubicación física
   - `meeting_link`: Link de reunión online
   - `created_by`: Usuario que creó la sesión
   - `status`: Estado (scheduled/completed/cancelled)

5. **StudyMaterial** - Materiales compartidos
   - `group`: Grupo
   - `title`: Título
   - `description`: Descripción
   - `file`: Archivo subido (opcional)
   - `link`: URL externa (opcional)
   - `uploaded_by`: Usuario
   - `created_at`: Fecha de subida

6. **Comment** - Comentarios y respuestas
   - `group`: Grupo
   - `author`: Usuario autor
   - `content`: Contenido del comentario
   - `parent`: Comentario padre (para respuestas)
   - `created_at`: Fecha de creación

7. **Profile** - Perfiles extendidos de usuario
   - `user`: Usuario (OneToOne)
   - `bio`: Biografía
   - `major`: Carrera
   - `interests`: Intereses
   - `profile_picture`: Foto de perfil

## 📥 Exportaciones CSV

### Formatos de Exportación

#### 1. Exportar Sesiones
**Columnas:**
- `date`: Fecha de la sesión
- `start_time`: Hora de inicio
- `end_time`: Hora de fin
- `duration_hours`: Duración en horas
- `title`: Título de la sesión
- `created_by`: Usuario que creó la sesión
- `group`: Nombre del grupo (solo en exportación global)
- `is_online`: Sí/No
- `location`: Ubicación (si es presencial)
- `meeting_link`: Link de reunión (si es online)
- `status`: Estado (scheduled/completed/cancelled)

**Ejemplo:**
```csv
date,start_time,end_time,duration_hours,title,created_by,group,is_online,location,meeting_link,status
2025-11-01,14:00:00,16:00:00,2.0,Álgebra Lineal,juan,Matemáticas 101,no,Sala 301,,scheduled
2025-11-02,18:00:00,20:00:00,2.0,Python Basics,maria,Programming,yes,,https://meet.google.com/abc,scheduled
```

#### 2. Exportar Top Miembros
**Columnas:**
- `user`: Nombre de usuario
- `sessions`: Número de sesiones creadas
- `hours`: Total de horas estudiadas

**Ejemplo:**
```csv
user,sessions,hours
juan,15,30.5
maria,12,24.0
pedro,10,20.0
```

### Cómo Exportar

**Como Usuario Normal:**
1. Ve al detalle de un grupo donde eres miembro
2. En el sidebar de "Group Stats":
   - Click en "Exportar CSV" para sesiones
   - Click en "Exportar" (en Top 5 Miembros) para top miembros
3. El archivo se descargará automáticamente

**Como Administrador:**
1. Ve a `/stats/` (Dashboard Global)
2. Selecciona un grupo (opcional) y rango de fechas
3. Click en:
   - "Exportar CSV" para sesiones
   - "Exportar Top Miembros" para ranking (requiere grupo seleccionado)
4. El archivo se descargará con el nombre:
   - `global_sessions_YYYY-MM-DD_to_YYYY-MM-DD.csv`
   - `group_X_sessions_YYYY-MM-DD_to_YYYY-MM-DD.csv`
   - `group_X_top_members_YYYY-MM-DD_to_YYYY-MM-DD.csv`

## 🎨 Personalización

### Cambiar Colores de los Gráficos
Edita las configuraciones de Chart.js en:
- `templates/core/stats.html` (dashboard admin)
- `templates/core/my_stats.html` (dashboard personal)
- `templates/core/group_detail.html` (stats de grupo)

Busca líneas como:
```javascript
backgroundColor: 'rgba(255, 159, 64, 0.2)'
borderColor: 'rgba(255, 159, 64, 1)'
```

### Agregar Nuevas Materias
```bash
python manage.py shell
```

```python
from core.models import Subject
Subject.objects.create(name="Física", code="FIS101", description="Física General")
```

### Cambiar Logo o Estilos
- Logo/Navbar: Edita `templates/core/base.html`
- Estilos: Agrega CSS custom en `<style>` tags o archivos estáticos

## 🚀 Deployment (Producción)

### Preparación para Producción

1. **Actualizar settings.py:**
```python
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com', 'www.tu-dominio.com']
```

2. **Usar base de datos robusta:**
```python
# PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'studygroups_db',
        'USER': 'postgres',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

3. **Configurar archivos estáticos:**
```bash
python manage.py collectstatic
```

4. **Variables de entorno:**
Usa librerías como `python-decouple` para gestionar secrets:
```bash
pip install python-decouple
```

```python
from decouple import config
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```

5. **Servidor WSGI:**
```bash
pip install gunicorn
gunicorn project1.wsgi:application --bind 0.0.0.0:8000
```

### Opciones de Hosting

- **Heroku**: Fácil deployment con Git
- **PythonAnywhere**: Hosting gratuito para proyectos pequeños
- **DigitalOcean/AWS/Google Cloud**: VPS para control total
- **Railway**: Alternativa moderna a Heroku

## 📚 Recursos Adicionales

- [Documentación oficial de Django](https://docs.djangoproject.com/)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [Django REST Framework](https://www.django-rest-framework.org/) (si quieres agregar API)

## 👥 Contribuir al Proyecto

1. Crea una rama para tu feature:
```bash
git checkout -b feature/nueva-funcionalidad
```

2. Haz commit de tus cambios:
```bash
git add .
git commit -m "Add: descripción de los cambios"
```

3. Push a tu rama:
```bash
git push origin feature/nueva-funcionalidad
```

4. Abre un Pull Request en GitHub

## ⚠️ Notas Importantes

1. **Primer Usuario:** El primer usuario creado con `createsuperuser` es el único con acceso a `/stats/` (dashboard global)

2. **Roles en Grupos:**
   - **Admin**: Control total del grupo, puede editar, cambiar roles, remover miembros
   - **Moderator**: Puede crear/editar sesiones y gestionar materiales
   - **Member**: Puede ver y participar, subir materiales, comentar

3. **Seguridad:**
   - Nunca compartas tu `SECRET_KEY` en repositorios públicos
   - Usa `DEBUG = False` en producción
   - Mantén Django actualizado: `pip install --upgrade django`

4. **Backups:**
   - Respalda regularmente tu base de datos:
     ```bash
     # SQLite
     cp db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3
     
     # PostgreSQL
     pg_dump studygroups_db > backup_$(date +%Y%m%d).sql
     ```

## 📞 Soporte y Ayuda

Para problemas o preguntas:
1. Revisa esta documentación completa
2. Consulta los logs en la consola donde corre el servidor
3. Verifica la [documentación oficial de Django](https://docs.djangoproject.com/)
4. Crea un issue en el repositorio de GitHub

---

## 🎓 ¡Listo para Empezar!

Sigue los pasos de instalación y en pocos minutos tendrás tu plataforma de grupos de estudio funcionando. 

**Comandos rápidos para empezar:**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install django pillow
python manage.py migrate
python manage.py loaddata core/fixtures/initial_subjects.json
python manage.py createsuperuser
python manage.py runserver
```

Visita `http://127.0.0.1:8000/` y ¡disfruta tu plataforma! 📚✨

---

**Desarrollado con ❤️ para facilitar el estudio colaborativo**

```bash
git clone <your-repo-url>
cd project1
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install django
```

*(Consider creating `requirements.txt` with `pip freeze > requirements.txt` for easier dependency management)*

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Load Initial Data (Optional)

Load sample subjects:
```bash
python manage.py loaddata core/fixtures/initial_subjects.json
```

Or create comprehensive sample data:
```bash
python create_samples.py
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Follow prompts to set username, email, and password for admin access.

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** in your browser.

### 8. Access Admin Panel

Go to **http://127.0.0.1:8000/admin/** and log in with your superuser credentials to manage data.

## Default Demo Users (if using create_samples.py)

1. **Admin User:**
   - Username: `admin`
   - Password: `AdminPass123`
   - Full admin access

2. **Demo Student:**
   - Username: `demo_student`
   - Password: `student123`
   - Regular user account

## Database Schema

### Core Models

1. **Subject** - Academic subjects for organizing groups
2. **StudyGroup** - Study group with name, description, subject, members
3. **GroupMembership** - Links users to groups with roles (member/moderator/admin)
4. **StudySession** - Scheduled study sessions with date/time/location
5. **StudyMaterial** - Files and links shared within groups
6. **Comment** - Discussion threads with reply support
7. **Profile** - Extended user profiles with bio, major, interests
8. **Notification** - Email and in-app notifications

## Project Structure

```
project1/
├── core/                    # Main Django app
│   ├── migrations/          # Database migrations
│   ├── templates/           # HTML templates
│   │   ├── core/
│   │   │   ├── comments/    # Comment section templates
│   │   │   ├── materials/   # Materials section
│   │   │   ├── email/       # Email templates
│   │   │   └── ...          # Other templates
│   │   ├── registration/    # Auth templates
│   │   └── admin/           # Custom admin templates
│   ├── fixtures/            # Initial data (subjects)
│   ├── admin.py             # Admin interface config
│   ├── models.py            # Database models
│   ├── views.py             # Views/controllers
│   ├── urls.py              # App URL routing
│   └── forms.py             # Django forms
├── project1/                # Project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # Root URL config
│   └── wsgi.py              # WSGI config
├── exports/                 # SQL Server export scripts (optional)
│   ├── *.csv                # Exported data
│   ├── *.tsv                # Tab-separated (for SQL Server)
│   ├── convert_csvs_to_tsv.ps1  # PowerShell converter
│   └── import_to_sqlserver.sql  # SQL Server import
├── tools/                   # Utility scripts
├── manage.py                # Django management script
├── create_samples.py        # Sample data generator
├── db.sqlite3               # SQLite database (created after migrations)
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Usage Guide

### For Students:

1. **Register** - Create account at `/register/`
2. **Browse Groups** - View available study groups by subject
3. **Join Groups** - Request to join groups (auto-approved if space available)
4. **Participate** - Comment, download materials, attend sessions
5. **Update Profile** - Add bio, major, and interests

### For Group Creators/Admins:

1. **Create Group** - Set name, description, subject, max members
2. **Upload Materials** - Share PDFs, links, and resources
3. **Schedule Sessions** - Create online or in-person study sessions
4. **Moderate** - Manage comments, materials, and member roles
5. **Communicate** - Notifications sent for new sessions

## Development Commands

```bash
# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files (for production)
python manage.py collectstatic

# Run on different port
python manage.py runserver 8001

# Create sample data
python create_samples.py

# Django shell
python manage.py shell
```

## SQL Server Export (Optional)

For analytics or production database, export to SQL Server:

1. **Generate data**: `python create_samples.py`
2. **Export to CSV**: Django admin or custom management command
3. **Convert to TSV**: Run `.\exports\convert_csvs_to_tsv.ps1` in PowerShell
4. **Import to SQL Server**: Execute `exports\import_to_sqlserver.sql` in SSMS

## Troubleshooting

**Migration errors:**
```bash
python manage.py migrate --run-syncdb
```

**Static files not loading in development:**
- Django automatically serves static files with `DEBUG=True`
- Check `STATIC_URL` in `settings.py`

**Port already in use:**
```bash
python manage.py runserver 8001
```

**Permission denied on PowerShell script:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\exports\convert_csvs_to_tsv.ps1
```

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature-name`
2. Make changes and test locally
3. Commit: `git commit -m "Add: description of changes"`
4. Push: `git push origin feature/your-feature-name`
5. Open Pull Request on GitHub

## Team & Credits

Created by [Your Team Names] for [Course/Project Name]

## License

Educational project - free to use and modify for learning purposes.