# 📅 Nexthora

> 🚧 **Estado del Proyecto: En Desarrollo (MVP)**
> Este proyecto se encuentra actualmente en fase de construcción y mejora continua. Ha sido desarrollado como un Producto Mínimo Viable (MVP) para demostrar arquitectura de software, automatización de procesos y diseño de bases de datos. **Próximamente, Nexthora será desplegado en un entorno de alojamiento profesional para su comercialización como modelo SaaS.**

**Nexthora** es una plataforma web (SaaS) diseñada para que profesionales independientes (barberos, manicuristas, tatuadores, masajistas, etc.) puedan digitalizar y automatizar la gestión de sus reservas.

A través de Nexthora, cada profesional obtiene un enlace público personalizado donde sus clientes pueden ver sus servicios, revisar la disponibilidad en tiempo real y agendar una cita sin colisiones de horario.

## ✨ Características Principales

* **Perfil Público Personalizado:** Cada profesional tiene una URL única (ej: `nexthora.com/mi-negocio`).

* **Gestión de Servicios:** Creación de servicios con duración en minutos, precios sin decimales y opción de ocultar/mostrar (incluye lógica de límite Freemium).

* **Horarios Flexibles:** Configuración de horas de trabajo por lotes semanales.

* **Bloqueo de Fechas:** Opción para bloquear días específicos (vacaciones, feriados, emergencias).

* **Motor de Reservas Anti-Colisión:** El sistema calcula los bloques de tiempo disponibles basándose en la duración del servicio, el horario laboral y las citas ya agendadas.

* **Dashboard de Gestión:** Vista rápida de las citas de hoy y mañana, con accesos directos a WhatsApp para contactar al cliente.

* **Registro de Clientes:** Captura de datos esenciales del cliente (Nombre, Apellido, RUT, Email, WhatsApp chileno).

## 🛠️ Tecnologías Utilizadas

* **Backend:** [Django 5.2](https://www.djangoproject.com/) (Python)

* **Base de Datos:** PostgreSQL (`psycopg2-binary`)

* **Frontend:** HTML5, plantillas nativas de Django, [Tailwind CSS](https://tailwindcss.com/) (vía CDN)

* **Gestión de Entorno:** `python-dotenv` para variables de entorno seguras.

## 🚀 Instalación y Configuración Local (Entorno de Desarrollo)

Sigue estos pasos para levantar el proyecto en tu máquina local para fines de revisión de código.

### 1. Requisitos Previos

* Python 3.10 o superior.

* PostgreSQL instalado y corriendo localmente.

### 2. Clonar el repositorio

```bash
git clone [https://github.com/TU_USUARIO/nexthora.git](https://github.com/TU_USUARIO/nexthora.git)
cd nexthora
```

### 3. Crear y activar un Entorno Virtual
```bash
# En Windows:
python -m venv venv
venv\Scripts\activate
```

# En macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 6. Ejecutar Migraciones
Prepara la base de datos creando las tablas necesarias:

```Bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Levantar el Servidor
```Bash
python manage.py runserver
El proyecto estará disponible en `http://127.0.0.1:8000/`.
```

## 📂 Estructura del Proyecto
* `nexthora_config/`: Configuración principal de Django (settings, urls, wsgi, asgi).

* `booking/`: Aplicación principal que contiene toda la lógica de negocio (modelos, vistas, formularios).

* `models.py`: Modelos de base de datos (ProfessionalProfile, BusinessHours, Service, Appointment, TimeOff).

* `views.py`: Controladores que manejan la lógica de renderizado y acciones del usuario.

* `forms.py`: Formularios de Django para la validación de datos.

* `templates/`: Archivos HTML con la integración de Tailwind CSS.

## 📝 Próximos Pasos (Roadmap Comercial)

* [ ] Panel para que el profesional edite el nombre e información de su negocio (Dashboard).

* [ ] Integración de pasarela de pagos (Stripe / MercadoPago / Webpay) para levantar el límite de servicios.

* [ ] Despliegue en servidor de producción (Ej: Railway, Heroku o AWS) con dominio personalizado.

* [ ] Envío automático de notificaciones por correo electrónico al confirmar la reserva.

Desarrollado para simplificar la vida de los profesionales independientes.