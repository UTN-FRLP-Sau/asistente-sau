# Chatbot Asistente para la Secretaría de Asuntos Universitarios

Este proyecto consiste en el desarrollo de un asistente virtual inteligente para la Secretaría de Asuntos Universitarios (SAU) de la Universidad Tecnológica Nacional, Facultad Regional La Plata (UTN FRLP).

## Descripción del Proyecto

El chatbot está diseñado para brindar atención automatizada a estudiantes y demás usuarios, ofreciendo respuestas inmediatas a consultas frecuentes relacionadas con los servicios que ofrece la SAU. Entre los temas que cubre se encuentran:

- Comedor universitario  
- Actividades y horarios deportivos  
- Becas y ayudas económicas  
- Boleto estudiantil y beneficios  
- Trámites administrativos y consultas generales  

El asistente tiene como objetivo principal descomprimir la atención presencial, telefónica y por correo, optimizando los recursos humanos de la Secretaría de Asuntos Universitarios. Al mismo tiempo, mejora la accesibilidad y disponibilidad de información relevante para la comunidad estudiantil, agilizando la comunicación, reduciendo los tiempos de respuesta ante consultas frecuentes y ofreciendo un canal digital de atención continua, eficiente y fácil de usar.

Los usuarios pueden interactuar con el chatbot a través de una interfaz web accesible desde cualquier navegador, o bien mediante un bot integrado en la plataforma **Telegram**. De este modo, se garantiza un acceso rápido, flexible y multiplataforma a la información, desde cualquier dispositivo y en cualquier momento.

## Tecnologías Utilizadas

El desarrollo del chatbot se llevó a cabo utilizando las siguientes tecnologías:

- **Rasa**: plataforma open source para la creación de asistentes conversacionales con inteligencia artificial.
- **Python**: lenguaje de programación principal del proyecto.
- **Docker**: para la contenerización de servicios y facilitar el despliegue.
- **K3s**: distribución ligera y certificada de **Kubernetes**, utilizada para orquestar y escalar el sistema en entornos de producción.
- **Redis**: base de datos en memoria de código abierto, utilizada principalmente por Rasa como lock store para gestionar el bloqueo de conversaciones y asegurar la consistencia del diálogo en entornos distribuidos.
- **Locust**: herramienta de prueba de carga de código abierto, utilizada para simular usuarios concurrentes y medir el rendimiento del chatbot.
- **Ngrok**: servicio de tunelización usado que expone servicios locales a Internet, facilitando la prueba de webhooks de Telegram y otras integraciones durante el desarrollo.
- **Telegram Bot API**: para la integración del asistente con la aplicación de mensajería Telegram.
- **HTML/CSS/JavaScript**: para el desarrollo del frontend web de interacción con el chatbot.


Pasos para correr el proyecto:
Asegurarse de Usar Python 3.10.* para un correcto funcionamiento de Rasa y el resto de dependencias
Crear entorno virtual(recomendado)
Activar entorno con: source venv/bin/activate
Instalar Rasa,locust,Docker,K3s,Redis,Ngrok

Crear configmaps:

ConfigMap para credentials.yml.template
kubectl create configmap rasa-credentials-template-cm --from-file=credentials.yml.template=./credentials.yml.template

ConfigMap para endpoints.yml:
kubectl create configmap rasa-endpoints-cm --from-file=endpoints.yml=./endpoints.yml

Aplicar configuracion de Ingress:
kubectl apply -f rasa-ingress.yaml

Para desarrollo configurar previamente token de tu cuenta de ngrok para luego levantar ngrok:
ngrok http 80

Crear Secrets:
kubectl create secret generic telegram-secrets \
  --from-literal=TELEGRAM_TOKEN='tu_token' \
  --from-literal=TELEGRAM_BOT_USERNAME='tu_usuario_bot'

Actualizar o Agregar por primera vez Webhook al Secret con el comando:
./actualizar_webhook.sh <pasar url que te genera ngrok como parametro>

Entrenar modelo de Rasa:
rasa train

Actualizar la ruta del volumen montado de los rasa-deployment.yaml para que coincida con tu nombre de usuario:
volumes:
        - name: models-volume
          hostPath:
            path: /home/'tu-usuario'/asistente-sau/chatbot/models

Aplicar redeploy de los pods con:
./redeploy-rasa.sh

Configurar ip del websocket en el index.html:
socketUrl: "http://'ip_de_tu_computadora':30001",

Levantar servidor web python:
python3 -m http.server 8000 --bind 0.0.0.0


Ejecutar test de carga con Locust(configurar ip del websocket en locustfile.py):
locust -f locustfile.py

Acceder a intefaz web mediante:
http://localhost:8000/

Ejecutar en consola el test de carga(u: cantidad de usuarios simultaneos, r: incremento de usuarios):
locust -f locustfile.py --host http://localhost:5005 --headless -u 150 -r 10 --run-time 1m


Mostrar logs del pod:
kubectl logs -f $(kubectl get pods -l app=rasa -o jsonpath="{.items[0].metadata.name}")


# Construir la imagen docker localmente
docker build -t manuelmorullo/rasa-chatbot:latest .

# Iniciar sesión (si no lo has hecho ya)
docker login

# Subir la imagen
docker push manuelmorullo/rasa-chatbot:latest

Para depurar access token:
https://developers.facebook.com/tools/debug/accesstoken/

Para configurar el webhook:
https://developers.facebook.com/apps/1206692898068573/use_cases/customize/wa-settings/

El access Token para que sea permanente se genera desde el user admin ya creado en la bussinees suite:
https://business.facebook.com/latest/settings/system_users

config de whatsapp:
https://business.facebook.com/latest/settings/whatsapp_account/


Salida consola rasa:
journalctl -u rasa -f

Reiniciar servicios (para produccion):
sudo systemctl restart rasa
sudo systemctl restart rasa-actions