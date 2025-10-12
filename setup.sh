#!/bin/bash

# Script para configuración inicial del bot

echo "🤖 Configuración inicial de Grande Bot"
echo "==========================================="

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instálalo primero."
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "✅ Archivo .env creado. Por favor editalo con tus credenciales."
else
    echo "⚠️  El archivo .env ya existe."
fi

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p data logs downloads

# Verificar permisos
echo "🔧 Configurando permisos..."
chmod 755 data logs downloads

echo ""
echo "✅ Configuración inicial completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Edita el archivo .env con tus credenciales"
echo "2. Ejecuta: docker-compose up -d"
echo "3. Verifica los logs: docker-compose logs -f"
echo ""
echo "📚 Consulta el README.md para más información."