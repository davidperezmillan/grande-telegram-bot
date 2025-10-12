#!/usr/bin/env python3
"""
Test script para verificar la configuración de VIDEO_CLEANUP_FILES
"""
import os

# Leer directamente del archivo .env
env_file = ".env"
env_vars = {}

try:
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value

    # Verificar configuración de limpieza
    cleanup_files_env = env_vars.get('VIDEO_CLEANUP_FILES', 'true').strip().lower()
    cleanup_files = cleanup_files_env in ['true', '1', 'yes', 'on']

    print(f"Variable VIDEO_CLEANUP_FILES: '{cleanup_files_env}'")
    print(f"Limpieza habilitada: {cleanup_files}")

    # Verificar otras configuraciones relacionadas
    clip_duration = env_vars.get('VIDEO_CLIP_DURATION', '30')
    clip_start = env_vars.get('VIDEO_CLIP_START_OFFSET', '')
    advanced_enabled = env_vars.get('ENABLE_ADVANCED_VIDEO_PROCESSING', 'false')

    print(f"VIDEO_CLIP_DURATION: {clip_duration}")
    print(f"VIDEO_CLIP_START_OFFSET: '{clip_start}'")
    print(f"ENABLE_ADVANCED_VIDEO_PROCESSING: {advanced_enabled}")
    
except Exception as e:
    print(f"Error leyendo .env: {e}")
