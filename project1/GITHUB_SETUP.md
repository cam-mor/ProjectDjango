# GitHub Setup Guide

Este documento te guía para subir tu proyecto a GitHub y que tus compañeros puedan clonarlo.

## Opción 1: Instalar Git y usar comandos (Recomendado)

### Paso 1: Instalar Git

Descarga e instala Git desde: https://git-scm.com/download/win

Durante la instalación, acepta los valores predeterminados.

### Paso 2: Configurar Git (primera vez)

Abre PowerShell o Git Bash y ejecuta:

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@example.com"
```

### Paso 3: Inicializar repositorio local

```bash
cd C:\Users\iamxa\Desktop\ProjectDjango\project1
git init
git add .
git commit -m "Initial commit: Study Groups MVP"
```

### Paso 4: Crear repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `study-groups-mvp` (o el que prefieras)
3. Descripción: "Django platform for students to create study groups"
4. **NO** marques "Initialize this repository with a README" (ya tienes uno)
5. Click "Create repository"

### Paso 5: Conectar y subir

GitHub te mostrará comandos. Usa estos (reemplaza `<tu-usuario>`):

```bash
git remote add origin https://github.com/<tu-usuario>/study-groups-mvp.git
git branch -M main
git push -u origin main
```

Si pide autenticación, usa tu **Personal Access Token** en lugar de contraseña:
- Ve a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- Generate new token con permisos de `repo`
- Copia el token y úsalo como contraseña

---

## Opción 2: Usar GitHub Desktop (Más fácil, sin comandos)

### Paso 1: Instalar GitHub Desktop

Descarga desde: https://desktop.github.com/

### Paso 2: Iniciar sesión

Abre GitHub Desktop y haz login con tu cuenta de GitHub.

### Paso 3: Agregar repositorio local

1. File → Add Local Repository
2. Busca: `C:\Users\iamxa\Desktop\ProjectDjango\project1`
3. Si dice "This directory does not appear to be a Git repository", click **"Create a repository"**
4. Name: `study-groups-mvp`
5. Desmarca "Initialize this repository with a README"
6. Click "Create Repository"

### Paso 4: Hacer el commit inicial

1. En GitHub Desktop, verás todos los archivos en "Changes"
2. Escribe en Summary: "Initial commit: Study Groups MVP"
3. Click **"Commit to main"**

### Paso 5: Publicar a GitHub

1. Click **"Publish repository"** arriba
2. Name: `study-groups-mvp`
3. Description: "Django platform for students to create study groups"
4. **Desmarca** "Keep this code private" si quieres que sea público
5. Click **"Publish Repository"**

¡Listo! Tu repositorio estará en `https://github.com/<tu-usuario>/study-groups-mvp`

---

## Compartir con tus compañeros

Una vez publicado, envíales:

### El enlace del repositorio:
```
https://github.com/<tu-usuario>/study-groups-mvp
```

### Instrucciones para clonar:

**Opción A - GitHub Desktop:**
1. Instalar GitHub Desktop
2. File → Clone Repository
3. Pegar la URL del repositorio
4. Elegir dónde guardarlo localmente
5. Seguir las instrucciones del README.md

**Opción B - Línea de comandos:**
```bash
git clone https://github.com/<tu-usuario>/study-groups-mvp.git
cd study-groups-mvp
```

Luego seguir las instrucciones del **README.md** para:
- Crear virtual environment
- Instalar Django
- Correr migraciones
- Crear superuser
- Ejecutar el servidor

---

## Actualizaciones futuras

### Para subir cambios (Git commands):

```bash
git add .
git commit -m "Descripción de los cambios"
git push
```

### Para subir cambios (GitHub Desktop):

1. Verás los cambios automáticamente en "Changes"
2. Escribe un resumen del cambio
3. Click "Commit to main"
4. Click "Push origin" arriba

### Para que tus compañeros obtengan actualizaciones:

**GitHub Desktop:**
- Click "Fetch origin" y luego "Pull origin"

**Comandos:**
```bash
git pull
```

---

## Archivos importantes ya incluidos

✅ `.gitignore` - Ignora archivos innecesarios (venv, db.sqlite3, __pycache__, etc.)
✅ `README.md` - Instrucciones completas de setup
✅ Todo el código del proyecto

## Notas de seguridad

⚠️ **NUNCA subas:**
- Contraseñas o API keys → usa `.env` y agrégalo a `.gitignore`
- `db.sqlite3` con datos reales de usuarios
- Archivos de virtual environment (`venv/`)

El `.gitignore` ya está configurado para evitar esto.

---

## ¿Necesitas ayuda?

- Documentación Git: https://git-scm.com/doc
- Guías GitHub: https://docs.github.com/es
- GitHub Desktop: https://docs.github.com/es/desktop

## Siguiente paso

Una vez en GitHub, tus compañeros podrán:
1. Clonar el repositorio
2. Seguir el `README.md` paso a paso
3. Tener el proyecto funcionando en minutos
4. Colaborar con pull requests
