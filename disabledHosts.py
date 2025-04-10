import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuración de la API de Zabbix
ZABBIX_API_URL = 'https://zabbix-url/api_jsonrpc.php'
ZABBIX_API_TOKEN = 'api-key'

# Configuración de la conexión SMTP
SMTP_SERVER = 'smtp-server'
SMTP_PORT = 25
SMTP_USER = 'smtp-user'
SMTP_PASSWORD = 'smtp-password'

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
    
    response = requests.post(ZABBIX_API_URL, json=data, headers=headers, verify='plantech.pem')
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
