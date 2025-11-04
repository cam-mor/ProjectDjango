# Sistema de Autenticación y Perfiles - Habilitado

## ✅ Funcionalidades Implementadas

### 1. **Registro de Usuarios**
- **URL**: `/register/`
- **Template**: `core/templates/registration/register.html`
- **Campos**:
  - Username (requerido)
  - Email (requerido)
  - Password (requerido)
  - Confirm Password (requerido)
  - Major (opcional)
  - Bio (opcional)
- **Características**:
  - Validación de contraseñas
  - Creación automática de perfil
  - Login automático después del registro
  - Redirección a la página principal

### 2. **Login de Usuarios**
- **URL**: `/accounts/login/` o `/login/`
- **Template**: `core/templates/registration/login.html`
- **Campos**:
  - Username
  - Password
- **Características**:
  - Mensajes de error claros
  - Soporte para parámetro `next` (redirección después del login)
  - Link a página de registro

### 3. **Logout**
- **URL**: `/accounts/logout/`
- **Funcionalidad**: Cierra sesión y redirige a la página principal

### 4. **Perfil de Usuario**
- **URL**: `/profile/`
- **Vista**: Muestra información del usuario y sus grupos
- **Secciones**:
  - Información personal (username, email, fecha de registro)
  - Major y Bio
  - Grupos del usuario
  - Sesiones próximas
  - Botón para editar perfil

### 5. **Edición de Perfil** ⭐ NUEVO
- **URL**: `/profile/edit/`
- **Template**: `core/templates/core/profile_edit.html`
- **Campos Editables**:
  - First Name
  - Last Name
  - Email
  - Major
  - Bio
  - Interests
- **Características**:
  - Formulario con validación
  - Mensajes de éxito
  - Botón de cancelar
  - Actualiza tanto User como Profile

---

## 🎯 Cómo Usar

### Para Nuevos Usuarios:

1. **Registro**:
   ```
   http://127.0.0.1:8000/register/
   ```
   - Completa el formulario con username, email y contraseña
   - (Opcional) Agrega tu carrera y bio
   - Haz clic en "Sign Up"
   - Serás redirigido automáticamente y ya estarás logueado

2. **Acceder después**:
   ```
   http://127.0.0.1:8000/accounts/login/
   ```
   O haz clic en "Login" en el navbar

### Para Usuarios Existentes:

1. **Ver Perfil**:
   - Navbar → Haz clic en tu nombre → "My Profile"
   - O ve a: `http://127.0.0.1:8000/profile/`

2. **Editar Perfil**:
   - En tu perfil → Botón "Edit Profile"
   - O ve a: `http://127.0.0.1:8000/profile/edit/`
   - Modifica la información que desees
   - Haz clic en "Save Changes"

3. **Cerrar Sesión**:
   - Navbar → Haz clic en tu nombre → "Logout"

---

## 📋 Archivos Creados/Modificados

### Creados:
- ✅ `core/templates/registration/login.html` - Template de login
- ✅ `core/templates/core/profile_edit.html` - Template de edición de perfil
- ✅ `AUTENTICACION.md` - Este archivo

### Modificados:
- ✅ `core/forms.py` - Agregado `ProfileEditForm`
- ✅ `core/views.py` - Agregada función `profile_edit`
- ✅ `core/urls.py` - Agregada ruta `profile/edit/`
- ✅ `core/templates/core/profile.html` - Agregado botón "Edit Profile"
- ✅ `project1/settings.py` - Agregadas configuraciones de login/logout
- ✅ `core/templates/registration/register.html` - Mejorado (renderizado manual de campos)

---

## 🔐 Configuración en settings.py

```python
# Authentication redirects
LOGIN_REDIRECT_URL = 'core:home'       # Después de login exitoso
LOGOUT_REDIRECT_URL = 'core:home'      # Después de logout
LOGIN_URL = 'login'                     # Para @login_required
```

---

## 📝 URLs Disponibles

| URL | Descripción | Template |
|-----|-------------|----------|
| `/register/` | Registro de nuevos usuarios | `registration/register.html` |
| `/accounts/login/` | Login | `registration/login.html` |
| `/accounts/logout/` | Logout | (redirige a home) |
| `/profile/` | Ver perfil del usuario | `core/profile.html` |
| `/profile/edit/` | Editar perfil | `core/profile_edit.html` |

---

## 🎨 Navbar - Opciones según Estado

### Usuario NO autenticado:
```
Study Groups | Find Groups | Search | [Login] | [Register]
```

### Usuario autenticado:
```
Study Groups | Find Groups | Create Group | Search | [👤 username ▼]
                                                       ├─ My Profile
                                                       ├─ My Groups
                                                       └─ Logout
```

---

## ✅ Testing Checklist

Para probar todas las funcionalidades:

1. **Registro**:
   - [ ] Ir a `/register/`
   - [ ] Crear cuenta con username, email, contraseña
   - [ ] Verificar que te loguea automáticamente
   - [ ] Verificar que aparece tu username en el navbar

2. **Login/Logout**:
   - [ ] Hacer logout
   - [ ] Ir a `/accounts/login/`
   - [ ] Login con las credenciales
   - [ ] Verificar redirección a home

3. **Perfil**:
   - [ ] Navbar → Username → "My Profile"
   - [ ] Verificar que muestra información correcta
   - [ ] Verificar que muestra grupos si tienes alguno

4. **Editar Perfil**:
   - [ ] En perfil → "Edit Profile"
   - [ ] Cambiar email, nombre, major, bio
   - [ ] Guardar cambios
   - [ ] Verificar mensaje de éxito
   - [ ] Verificar que los cambios se guardaron

5. **Navegación**:
   - [ ] Intentar acceder a `/groups/create/` sin login → debe redirigir a login
   - [ ] Después de login → debe volver a `/groups/create/`

---

## 🚀 Usuarios de Prueba

### Admin:
- **Username**: `admin`
- **Password**: `AdminPass123!`
- Tiene permisos de superusuario

### Demo Student:
- **Username**: `demo_student`
- **Password**: `student123`
- Usuario regular con grupos de ejemplo

---

## 💡 Notas Importantes

1. **No se requiere verificación de email**: Los usuarios pueden registrarse solo con username, email y contraseña.

2. **Perfil automático**: Cuando un usuario se registra, se crea automáticamente su perfil.

3. **Campos opcionales**: Major, Bio e Interests son opcionales y pueden dejarse en blanco.

4. **Seguridad**: Las contraseñas se validan con los validadores de Django (mínimo 8 caracteres, no enteramente numérica, etc.).

5. **@login_required**: Todas las funciones que requieren autenticación están protegidas con este decorador.

---

## 🎉 ¡Todo Listo!

El sistema de autenticación y perfiles está completamente funcional. Los usuarios pueden:
- ✅ Registrarse fácilmente
- ✅ Iniciar sesión
- ✅ Ver su perfil
- ✅ Editar su información
- ✅ Cerrar sesión

**Próximos pasos sugeridos**:
1. Prueba registrando un nuevo usuario
2. Edita tu perfil
3. Únete a algunos grupos
4. ¡Empieza a usar la plataforma!
