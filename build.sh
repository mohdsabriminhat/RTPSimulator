#!/usr/bin/env bash

# Jalankan migration database
python manage.py migrate

# Kumpulkan semua fail statik ke dalam folder STATIC_ROOT
python manage.py collectstatic --noinput
