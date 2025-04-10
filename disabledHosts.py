#!/usr/bin/env python3
import os
import sys
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de Zabbix
ZABBIX_URL = os.getenv('ZABBIX_URL')
ZABBIX_API_TOKEN = os.getenv('ZABBIX_API_TOKEN')

# Configuración del servidor SMTP
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# Configuración del correo
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')

# Verificar que todas las variables de entorno estén configuradas
required_vars = [
    'ZABBIX_URL', 'ZABBIX_API_TOKEN',
    'SMTP_SERVER', 'SMTP_USER', 'SMTP_PASSWORD',
    'EMAIL_FROM', 'EMAIL_TO'
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"Error: Las siguientes variables de entorno no están configuradas: {', '.join(missing_vars)}")
    print("Por favor, configura el archivo .env con todas las variables necesarias.")
    sys.exit(1)

def get_disabled_hosts(ZABBIX_API_TOKEN):
    headers = {'Content-Type': 'application/json'}
    data = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "name", "status", "lastaccess"],
            "selectTags": "extend",  # Aseguramos que se obtengan los tags de cada host
            "filter": {
                "status": 1  # '1' es para deshabilitados
            }
        },
        "id": 2,
        "auth": ZABBIX_API_TOKEN
    }
    
    response = requests.post(ZABBIX_URL, json=data, headers=headers)
    hosts = response.json().get("result", [])
    
    # Filtrar hosts que no tienen el tag "disabled"
    filtered_hosts = []
    for host in hosts:
        tags = host.get("tags", [])
        # Excluimos hosts con tags 'duplicated' o 'disabled'
        if not any(tag['tag'] in ['duplicated', 'disabled'] for tag in tags):
            filtered_hosts.append(host)
    
    return filtered_hosts

# Obtener y mostrar los hosts deshabilitados sin el tag "disabled"
disabled_hosts = sorted(get_disabled_hosts(ZABBIX_API_TOKEN), key=lambda x: x['name'])

# Solo proceder si hay hosts deshabilitados
if disabled_hosts:
    # Crear la lista HTML de hosts
    lista_html = "<ul>"
    for host in disabled_hosts:
        lista_html += f"<li>{host['name']}</li>"
    lista_html += "</ul>"

    # Cuerpo del correo en formato HTML
    cuerpo_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cuerpo del Correo</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333;
                background-color: #f4f4f4;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            h2 {{
                color: #0066cc;
            }}
            p {{
                font-size: 16px;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Lista de Hosts Deshabilitados en Zabbix</h2>
            <p>A continuación se indican la lista de hosts deshabilitados en Zabbix:</p>
            {lista_html}
            <p>Recordar que si se deshabilita un host y no se quiere que salga en este informe, agregar como tag en el host la clave <i>disabled</i> y valor <i>true</i></p>
        </div>
    </body>
    </html>
    """

    # Crear el objeto del mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = "sender@example.com"
    mensaje['To'] = "destination@example.com"
    mensaje['Subject'] = "Lista de Hosts Deshabilitados en Zabbix"

    # Agregar el cuerpo del correo (HTML)
    mensaje.attach(MIMEText(cuerpo_html, 'html'))

    # Establecer conexión con el servidor SMTP y enviar el correo
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Inicia TLS para una conexión segura
        server.login(SMTP_USER, SMTP_PASSWORD)  # Autenticarse
        server.sendmail(mensaje['From'], mensaje['To'], mensaje.as_string())  # Enviar el correo
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Ocurrió un error al enviar el correo: {e}")
    finally:
        server.quit()  # Cerrar la conexión SMTP
else:
    print("No hay hosts deshabilitados para notificar.")
