# Zabbix Disabled Hosts Notifier

Este script envía un correo electrónico con un resumen de los hosts deshabilitados en Zabbix.

## Requisitos

-   Python 3.x
-   pip (gestor de paquetes de Python)
-   virtualenv (para crear entornos virtuales)

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/xrodriguezd/zabbix-disabledHosts.git
cd zabbix-disabledHosts
```

2. Crear y activar el entorno virtual:

```bash
# Instalar virtualenv si no está instalado
pip install virtualenv

# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate
```

3. Instalar las dependencias de Python:

```bash
pip install -r requirements.txt
```

4. Configurar las variables de entorno:
    - Copiar el archivo `.env.example` a `.env`
    - Editar el archivo `.env` con tus credenciales de Zabbix y configuración de correo

## Configuración del Cron

Para programar la ejecución automática del script, edita el crontab del usuario:

```bash
crontab -e
```

Ejemplos de configuración:

-   Para ejecutar de Lunes a Viernes a las 8:00 AM:

```
0 8 * * 1-5 /bin/bash ~/scripts/disabledHosts/run.sh
```

-   Para ejecutar todos los días a las 8:00 AM:

```
0 8 * * * /bin/bash ~/scripts/disabledHosts/run.sh
```

-   Para ejecutar cada 4 horas:

```
0 */4 * * * /bin/bash ~/scripts/disabledHosts/run.sh
```

## Estructura del Proyecto

-   `run.sh`: Script principal que ejecuta el script de Python
-   `disabledHosts.py`: Script de Python que obtiene los hosts deshabilitados y envía el correo
-   `requirements.txt`: Dependencias de Python necesarias
-   `.env.example`: Ejemplo de archivo de configuración
-   `.env`: Archivo de configuración (no incluido en el repositorio)

## Variables de Entorno

El archivo `.env` debe contener las siguientes variables:

```
ZABBIX_URL=https://tu-zabbix-server
ZABBIX_API_TOKEN=token-de-usuario
SMTP_SERVER=tu-servidor-smtp
SMTP_PORT=587
SMTP_USER=tu-usuario-smtp
SMTP_PASSWORD=tu-contraseña-smtp
EMAIL_FROM=tu-correo@dominio.com
EMAIL_TO=destinatario@dominio.com
```

## Notas

-   Asegúrate de que el script `run.sh` tenga permisos de ejecución:

```bash
chmod +x run.sh
```

-   El script asume que Python está en el PATH del sistema.
-   Se recomienda probar el script manualmente antes de configurar el cron.
