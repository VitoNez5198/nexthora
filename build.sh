#!/usr/bin/env bash
# Salir si ocurre un error
set -o errexit

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Recolectar archivos estáticos para WhiteNoise
python manage.py collectstatic --no-input

# 3. Aplicar migraciones a la base de datos de producción
python manage.py migrate