# 📋 Comandos de Grande Bot

Grande Bot incluye varios comandos útiles para obtener información y gestionar el bot.

## 🆔 Comando `/id`

El comando más útil del bot. Te proporciona **toda la información de IDs** que necesitas.

### **¿Qué hace?**
- 📨 Muestra el ID del mensaje actual
- 💬 Muestra información completa del chat/grupo/canal
- 👤 Muestra información del usuario que envía el comando
- 📤 Si es un mensaje reenviado, muestra información del origen
- ↩️ Si respondes a un mensaje, muestra información del mensaje original
- 📋 Formatea los IDs para copiar directamente en tu `.env`

### **¿Cómo usarlo?**

#### **En cualquier chat:**
```
/id
```
Te mostrará toda la información del chat actual.

#### **Respondiendo a un mensaje:**
1. Responde a cualquier mensaje con `/id`
2. Obtendrás información del mensaje original y su autor

#### **Con un mensaje reenviado:**
1. Reenvía un mensaje de otro chat
2. Usa `/id` en el mensaje reenviado
3. Verás tanto la información actual como la del origen

### **Ejemplo de respuesta:**
```
🆔 INFORMACIÓN DE IDs
==============================

📨 Mensaje ID: 12345
📅 Fecha: 2025-10-11 15:30:00

💬 INFORMACIÓN DEL CHAT
👥 Tipo: Supergrupo
🆔 ID: -1001234567890
📝 Título: Mi Grupo de Telegram
🔗 Username: @mi_grupo
👥 Miembros: 150

👤 INFORMACIÓN DEL REMITENTE
👤 Tipo: Conversación privada
🆔 ID: 987654321
📝 Título: Juan Pérez
🔗 Username: @juanperez

📋 PARA COPIAR EN .ENV
```
TARGET_GROUP_ID=-1001234567890
TARGET_GROUP_USERNAME=mi_grupo
CHAT_ID=-1001234567890
TYPE=SUPERGROUP
```
```

## 🏠 Comando `/start`

Comando de bienvenida que explica las funcionalidades del bot.

### **¿Qué hace?**
- 👋 Muestra mensaje de bienvenida
- 📋 Lista los comandos disponibles
- ℹ️ Explica las funcionalidades automáticas

### **Uso:**
```
/start
```

## ❓ Comando `/help`

Comando de ayuda detallada con toda la información del bot.

### **¿Qué hace?**
- 📖 Explica todos los comandos en detalle
- 🔧 Lista las funcionalidades automáticas
- 💡 Proporciona consejos de uso
- 📊 Explica qué datos guarda el bot

### **Uso:**
```
/help
```

## 💡 Casos de Uso Prácticos

### **1. Configurar el bot para un grupo nuevo:**
1. Añade el bot al grupo
2. Envía `/id` en el grupo
3. Copia el `TARGET_GROUP_ID` y `TARGET_GROUP_USERNAME`
4. Pégalos en tu archivo `.env`

### **2. Encontrar el ID de un canal:**
1. Reenvía cualquier mensaje del canal a un chat con el bot
2. Usa `/id` en el mensaje reenviado
3. Obtendrás el ID del canal original

### **3. Obtener información de un usuario:**
1. Que el usuario envíe cualquier mensaje
2. Responde a su mensaje con `/id`
3. Verás toda su información

### **4. Verificar IDs de mensajes específicos:**
1. Responde al mensaje que te interese con `/id`
2. Obtendrás el ID del mensaje original
3. Útil para hacer referencias o debugging

## 🔧 Funcionalidades Automáticas

Además de los comandos, Grande Bot **procesa automáticamente** todos los mensajes del grupo configurado:

### **📝 Texto:**
- Detecta enlaces, emails, números de teléfono
- Analiza idioma y longitud del texto
- Identifica contenido especial

### **🎥 Videos:**
- Detecta archivos de más de 20MB automáticamente
- Los descarga para procesamiento posterior
- Registra tamaño y tipo de archivo

### **🖼️ Imágenes:**
- Analiza y registra información básica
- Detecta diferentes formatos
- Prepara para procesamiento futuro

### **🎬 Animaciones/GIFs:**
- Identifica GIFs y animaciones
- Registra tamaño y características
- Lista para definir acciones específicas

### **🎭 Stickers:**
- Detecta y categoriza stickers
- Registra para estadísticas de uso
- Prepara para análisis posterior

## 📊 Datos Que Guarda

Grande Bot mantiene un registro persistente de:

- ✅ **Todos los mensajes procesados** con IDs únicos
- ✅ **Respuestas del bot** vinculadas a mensajes originales
- ✅ **Archivos descargados** con rutas y metadatos
- ✅ **Estadísticas de uso** por tipo de contenido
- ✅ **Información de usuarios** y chats
- ✅ **Cola de procesamiento** para tareas pendientes

## 🚀 Próximos Comandos

Comandos planeados para futuras versiones:

- `/stats` - Estadísticas detalladas del bot
- `/download <mensaje_id>` - Descargar archivo específico
- `/search <término>` - Buscar en mensajes procesados
- `/export` - Exportar datos a formato JSON
- `/config` - Configurar comportamiento del bot

---

**💡 Tip:** Usa `/id` liberalmente, es el comando más útil para configurar y hacer debugging del bot.